import requests
import json
import datetime
from icecream import ic


class SheetDB:
    def __init__(self, api_url=''):
        self.api_url = api_url

    def set_api_url(self, url):
        self.api_url = url

    def _request(self, method, action, params=None, payload=None):
        if not self.api_url:
            raise ConnectionError("Google Sheets API URL not configured")
        p = {'action': action}
        if params:
            p.update(params)
        resp = None
        try:
            if method == 'GET':
                resp = requests.get(self.api_url, params=p, timeout=5)
            else:
                resp = requests.post(self.api_url, params=p, json=payload or {}, timeout=5)
            if 'accounts.google.com' in (resp.url or ''):
                return {'success': False, 'error': 'Redirected to Google sign-in. Deploy the script as a Web App with public access, then use the deployment URL (ends with /exec).'}
            resp.raise_for_status()
            return resp.json()
        except json.JSONDecodeError:
            preview = resp.text[:200] if resp and resp.text else '(empty)'
            ic(f"SheetDB non-JSON response ({action}): {preview}")
            msg = f'API returned non-JSON (HTTP {resp.status_code}). '
            if 'accounts.google.com' in preview or 'signin' in preview.lower():
                msg += 'The script is not deployed as a Web App or is not publicly accessible. Go to Extensions → Apps Script → Deploy → New Deployment → Web App (Execute as: Me, Access: Anyone).'
            elif resp.status_code == 404:
                msg += 'URL not found. Check the deployment URL.'
            elif resp.status_code == 302:
                msg += 'The URL redirects. Use the final deployment URL (ends with /exec).'
            else:
                msg += f'Response preview: {preview}'
            return {'success': False, 'error': msg}
        except requests.RequestException as e:
            ic(f"SheetDB {method} error ({action}): {e}")
            status = resp.status_code if resp else 'N/A'
            return {'success': False, 'error': f'Request failed (HTTP {status}): {e}'}

    def _post(self, action, payload=None):
        return self._request('POST', action, payload=payload)

    def _get(self, action, params=None):
        return self._request('GET', action, params=params)

    def member_register(self, rfid, memberid, name, student_num, program, year):
        created_on = datetime.datetime.now().strftime('%Y-%m-%d')
        result = self._post('addMember', {
            'rfid': rfid,
            'memberid': memberid,
            'name': name,
            'student_num': student_num,
            'program': program,
            'year': year,
            'date_registered': created_on
        })
        return 0 if result.get('success') else -1

    def member_exists(self, rfid):
        result = self._post('getMember', {'rfid': rfid})
        if result.get('success') and result.get('data'):
            return result['data']
        return None

    def list_tables(self):
        result = self._get('listEvents')
        if result.get('success'):
            return result.get('data', [])
        return []

    def create_event_table(self, table_name):
        table_name = table_name.replace(' ', '_')
        result = self._post('createEvent', {'eventName': table_name})
        return 0 if result.get('success') else -1

    def fetch_table_data(self, table_name):
        if table_name == 'Members':
            result = self._get('listMembers')
            if result.get('success'):
                return result.get('data', [])
            return []
        result = self._post('getAttendees', {'eventName': table_name})
        if result.get('success'):
            return result.get('data', [])
        return []

    def attendance_member_event(self, table_name, rfid):
        result = self._post('recordAttendance', {
            'eventName': table_name,
            'rfid': rfid
        })
        return 0 if result.get('success') else -1

    def scan_attendance(self, table_name, rfid):
        """Batched scan: member_exists + check_attended + record in one API call."""
        result = self._post('scanAttendance', {
            'eventName': table_name,
            'rfid': rfid
        })
        return result

    def member_attended_event(self, table_name, rfid):
        result = self._post('checkAttended', {
            'eventName': table_name,
            'rfid': rfid
        })
        if result.get('success'):
            return result.get('attended', False)
        return False

    def get_member_name(self, rfid):
        result = self._post('getMember', {'rfid': rfid})
        if result.get('success') and result.get('data'):
            return result['data'].get('name')
        return None

    def delete_event(self, event_name):
        result = self._post('deleteEvent', {'eventName': event_name})
        return 0 if result.get('success') else -1

    def get_event_details(self, event_name):
        result = self._post('getEventDetails', {'eventName': event_name})
        if result.get('success'):
            return result.get('data', {})
        return None

    def get_config(self):
        result = self._get('config')
        if result.get('success'):
            return result.get('data', {})
        return None

    def set_spreadsheet(self, url_or_id):
        result = self._get('setConfig', {'url': url_or_id})
        return result.get('success', False)

    def initialize_db(self, timeout=None):
        pass

    def db_exists(self):
        return bool(self.api_url)

    def get_db_connection(self, timeout=None):
        return self
