/**
 * Google Apps Script Web App — CRUD backend for Ev_Ap
 *
 * ===== SETUP INSTRUCTIONS =====
 * 1. Create a new Google Sheet (or open an existing one).
 * 2. Extensions → Apps Script → paste this code → save.
 * 3. Run the "setupSpreadsheet" function once (or use the Ev_Ap menu that appears).
 * 4. Deploy → New deployment → Web App (Execute as: Me, Access: Anyone).
 * 5. Copy the deployment URL → paste in Ev_Ap Settings → Google Sheets API URL.
 *
 * Sheet structure in the MAIN spreadsheet:
 *   "Members" — rfid, memberid, name, student_num, program, year, date_registered
 *   "Events"  — event_name, spreadsheet_id, spreadsheet_url, created_date, status
 *
 * Each event gets its OWN separate Google Sheet file with an "Attendance" sheet:
 *   "Attendance" — rfid, memberid, student_num, name, attendance_time
 */

// ── Spreadsheet ID storage ────────────────────────────────────────────
// Stored in ScriptProperties under key 'SPREADSHEET_ID'.
// If unset, the script will use whichever sheet is bound to it.

function getSpreadsheet_() {
  var key = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
  if (key) {
    try {
      return SpreadsheetApp.openById(key);
    } catch (e) {
      throw new Error('Cannot open configured spreadsheet. Run Setup → Configure Spreadsheet again.');
    }
  }
  // Fallback to bound sheet (if deployed as attachment to a sheet)
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (ss) return ss;
  throw new Error('No spreadsheet configured. Open the script editor and run setupSpreadsheet() first.');
}

// ── Menu for in-editor setup ──────────────────────────────────────────

function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Ev_Ap')
    .addItem('🔗 Configure Spreadsheet', 'setupSpreadsheet')
    .addItem('📋 View Current Config', 'showConfig')
    .addSeparator()
    .addItem('❓ Help', 'showHelp')
    .addToUi();
}

function setupSpreadsheet() {
  var ui = SpreadsheetApp.getUi();
  var currentId = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
  var msg = 'Enter the Google Sheet URL or Spreadsheet ID to use with Ev_Ap.';
  if (currentId) {
    msg += '\n\nCurrently configured ID: ' + currentId;
    msg += '\n\nLeave blank and press OK to keep the current setting.';
  }

  var response = ui.prompt('Ev_Ap — Configure Spreadsheet', msg, ui.ButtonSet.OK_CANCEL);
  if (response.getSelectedButton() !== ui.Button.OK) return;
  var input = response.getResponseText().trim();
  if (!input && currentId) return; // keep existing

  if (!input) {
    ui.alert('No input provided. Using the currently bound spreadsheet.');
    return;
  }

  var sheetId = extractId_(input);
  try {
    SpreadsheetApp.openById(sheetId);
    PropertiesService.getScriptProperties().setProperty('SPREADSHEET_ID', sheetId);
    ui.alert('✅ Spreadsheet configured!\n\nID: ' + sheetId + '\n\nThe Web App is ready to deploy.');
  } catch (e) {
    ui.alert('❌ Could not find a spreadsheet with that ID/URL.\n\nError: ' + e.message);
  }
}

function showConfig() {
  var ui = SpreadsheetApp.getUi();
  var id = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
  if (id) {
    var ss = SpreadsheetApp.openById(id);
    ui.alert('📋 Current Configuration\n\nSpreadsheet ID: ' + id + '\nTitle: ' + ss.getName());
  } else {
    ui.alert('📋 Current Configuration\n\nNo spreadsheet configured.\nUses the currently bound sheet.');
  }
}

function showHelp() {
  SpreadsheetApp.getUi().alert(
    'Ev_Ap — Google Sheets Backend\n\n' +
    '1. Set up: Run Setup → Configure Spreadsheet\n' +
    '2. Deploy: Deploy → New deployment → Web App\n' +
    '3. Copy the Web App URL into Ev_Ap Settings\n\n' +
    'Main spreadsheet has:\n' +
    '  - "Members" sheet (member records)\n' +
    '  - "Events" sheet (event registry)\n\n' +
    'Each event creates its own separate spreadsheet file in your Google Drive.'
  );
}

function extractId_(input) {
  input = input.trim();
  // Already looks like a raw ID (no slashes, no https)
  if (/^[a-zA-Z0-9_-]{30,}$/.test(input)) return input;
  // Try to extract from URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
  var match = input.match(/\/d\/([a-zA-Z0-9_-]+)/);
  if (match) return match[1];
  return input;
}

// ── doGet / doPost — Web App API ──────────────────────────────────────

function doGet(e) {
  var action = e.parameter.action || '';
  var output;

  try {
    switch (action) {
      case 'listMembers':
        output = listMembers_();
        break;
      case 'listEvents':
        output = listEvents_();
        break;
      case 'getEventDetails':
        output = getEventDetails_(e.parameter);
        break;
      case 'config':
        output = getConfig_();
        break;
      case 'setConfig':
        output = setConfig_(e.parameter);
        break;
      default:
        output = { success: false, error: 'Unknown action: ' + action };
    }
  } catch (err) {
    output = { success: false, error: err.message };
  }

  return ContentService.createTextOutput(JSON.stringify(output))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var action = e.parameter.action || '';
  var body = {};
  try {
    body = JSON.parse(e.postData.contents);
  } catch (_) {}
  var output;

  try {
    switch (action) {
      case 'addMember':
        output = addMember_(body);
        break;
      case 'getMember':
        output = getMember_(body);
        break;
      case 'createEvent':
        output = createEvent_(body);
        break;
      case 'recordAttendance':
        output = recordAttendance_(body);
        break;
      case 'getAttendees':
        output = getAttendees_(body);
        break;
      case 'checkAttended':
        output = checkAttended_(body);
        break;
      case 'deleteEvent':
        output = deleteEvent_(body);
        break;
      case 'getEventDetails':
        output = getEventDetails_(body);
        break;
      case 'scanAttendance':
        output = scanAttendance_(body);
        break;
      default:
        output = { success: false, error: 'Unknown action: ' + action };
    }
  } catch (err) {
    output = { success: false, error: err.message };
  }

  return ContentService.createTextOutput(JSON.stringify(output))
    .setMimeType(ContentService.MimeType.JSON);
}

// ── Config API endpoints ──────────────────────────────────────────────

function getConfig_() {
  var id = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
  var data = {
    spreadsheetId: id || null,
    configured: !!id,
    spreadsheetName: null,
    spreadsheetUrl: null
  };
  if (id) {
    try {
      var ss = SpreadsheetApp.openById(id);
      data.spreadsheetName = ss.getName();
      data.spreadsheetUrl = ss.getUrl();
    } catch (e) {
      data.error = 'Cannot open spreadsheet: ' + e.message;
    }
  } else {
    try {
      var ss = SpreadsheetApp.getActiveSpreadsheet();
      if (ss) {
        data.spreadsheetName = ss.getName() + ' (active, not saved in config)';
        data.spreadsheetUrl = ss.getUrl();
        data.configured = false;
      }
    } catch (_) {}
  }
  return { success: true, data: data };
}

function setConfig_(params) {
  var urlOrId = params.url || params.spreadsheetId || '';
  if (!urlOrId) {
    return { success: false, error: 'Provide ?url=SPREADSHEET_ID_OR_URL' };
  }
  var sheetId = extractId_(urlOrId);
  try {
    SpreadsheetApp.openById(sheetId);
    PropertiesService.getScriptProperties().setProperty('SPREADSHEET_ID', sheetId);
    return { success: true, data: { spreadsheetId: sheetId } };
  } catch (e) {
    return { success: false, error: 'Invalid spreadsheet ID/URL: ' + e.message };
  }
}

// ── Sheet helpers ─────────────────────────────────────────────────────

function getSheet_(name) {
  var ss = getSpreadsheet_();
  var sheet = ss.getSheetByName(name);
  if (!sheet) sheet = ss.insertSheet(name);
  return sheet;
}

function ensureHeaders_(sheet, headers) {
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  }
}

// ── Events registry helpers ───────────────────────────────────────────

function getEventsSheet_() {
  var ss = getSpreadsheet_();
  var sheet = ss.getSheetByName('Events');
  if (!sheet) {
    sheet = ss.insertSheet('Events');
    sheet.getRange(1, 1, 1, 5).setValues([['event_name', 'spreadsheet_id', 'spreadsheet_url', 'created_date', 'status']]);
  }
  return sheet;
}

function getEventSpreadsheetId_(eventName) {
  var sheet = getEventsSheet_();
  var rows = sheet.getDataRange().getValues();
  for (var i = 1; i < rows.length; i++) {
    if (rows[i][0] === eventName) {
      return rows[i][1];
    }
  }
  return null;
}

// ── CRUD: Members ─────────────────────────────────────────────────────

function listMembers_() {
  var ss = getSpreadsheet_();
  var sheet = ss.getSheetByName('Members');
  if (!sheet || sheet.getLastRow() < 2) return { success: true, data: [] };

  var rows = sheet.getDataRange().getValues();
  var headers = rows[0];
  var members = [];
  for (var i = 1; i < rows.length; i++) {
    var obj = {};
    for (var j = 0; j < headers.length; j++) obj[headers[j]] = rows[i][j];
    members.push(obj);
  }
  return { success: true, data: members };
}

function addMember_(body) {
  var sheet = getSheet_('Members');
  var headers = ['rfid', 'memberid', 'name', 'student_num', 'program', 'year', 'date_registered'];
  ensureHeaders_(sheet, headers);

  var existing = getMember_({ rfid: body.rfid });
  if (existing.success && existing.data) {
    return { success: false, error: 'Member already exists' };
  }

  // Format rfid column as plain text to prevent number auto-conversion
  if (sheet.getLastRow() > 0) {
    sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).setNumberFormat('@');
  }

  var now = new Date();
  var dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  sheet.appendRow([
    body.rfid,
    body.memberid,
    body.name,
    body.student_num,
    body.program,
    body.year,
    dateStr
  ]);
  return { success: true };
}

function getMember_(body) {
  var ss = getSpreadsheet_();
  var sheet = ss.getSheetByName('Members');
  if (!sheet || sheet.getLastRow() < 2) return { success: true, data: null };

  var rows = sheet.getDataRange().getValues();
  var headers = rows[0];
  var searchRfid = String(body.rfid);
  for (var i = 1; i < rows.length; i++) {
    if (String(rows[i][0]) === searchRfid) {
      var obj = {};
      for (var j = 0; j < headers.length; j++) obj[headers[j]] = rows[i][j];
      return { success: true, data: obj };
    }
  }
  return { success: true, data: null };
}

// ── CRUD: Events ──────────────────────────────────────────────────────

function createEvent_(body) {
  var name = body.eventName.replace(/ /g, '_');

  // Create a new standalone spreadsheet for this event
  var newSS = SpreadsheetApp.create('Ev_Ap - ' + name);
  var attSheet = newSS.getSheets()[0];
  attSheet.setName('Attendance');
  var headers = ['rfid', 'memberid', 'student_num', 'name', 'attendance_time'];
  ensureHeaders_(attSheet, headers);
  // Format rfid column as plain text
  attSheet.getRange('A:A').setNumberFormat('@');

  // Register event in the main spreadsheet's Events sheet
  var eventsSheet = getEventsSheet_();
  var now = new Date();
  var dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm:ss');
  eventsSheet.appendRow([name, newSS.getId(), newSS.getUrl(), dateStr, 'active']);

  return { success: true, eventName: name, spreadsheetId: newSS.getId(), spreadsheetUrl: newSS.getUrl() };
}

function recordAttendance_(body) {
  var spreadsheetId = getEventSpreadsheetId_(body.eventName);
  if (!spreadsheetId) {
    return { success: false, error: 'Event not found: ' + body.eventName };
  }

  var memberRes = getMember_({ rfid: body.rfid });
  if (!memberRes.success || !memberRes.data) {
    return { success: false, error: 'No member found with the given RFID' };
  }

  var ss = SpreadsheetApp.openById(spreadsheetId);
  var sheet = ss.getSheetByName('Attendance');
  if (!sheet) {
    return { success: false, error: 'Attendance sheet not found in event spreadsheet' };
  }
  var headers = ['rfid', 'memberid', 'student_num', 'name', 'attendance_time'];
  ensureHeaders_(sheet, headers);
  sheet.getRange('A:A').setNumberFormat('@');

  var member = memberRes.data;
  var now = new Date();
  var timeStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm:ss');
  sheet.appendRow([member.rfid, member.memberid, member.student_num, member.name, timeStr]);
  return { success: true };
}

function getAttendees_(body) {
  var spreadsheetId = getEventSpreadsheetId_(body.eventName);
  if (!spreadsheetId) return { success: true, data: [] };

  var ss = SpreadsheetApp.openById(spreadsheetId);
  var sheet = ss.getSheetByName('Attendance');
  if (!sheet || sheet.getLastRow() < 2) return { success: true, data: [] };

  var rows = sheet.getDataRange().getValues();
  var headers = rows[0];
  var attendees = [];
  for (var i = 1; i < rows.length; i++) {
    var obj = {};
    for (var j = 0; j < headers.length; j++) obj[headers[j]] = rows[i][j];
    attendees.push(obj);
  }
  return { success: true, data: attendees };
}

function checkAttended_(body) {
  var spreadsheetId = getEventSpreadsheetId_(body.eventName);
  if (!spreadsheetId) return { success: true, attended: false };

  var ss = SpreadsheetApp.openById(spreadsheetId);
  var sheet = ss.getSheetByName('Attendance');
  if (!sheet || sheet.getLastRow() < 2) return { success: true, attended: false };

  var rows = sheet.getDataRange().getValues();
  var searchRfid = String(body.rfid);
  for (var i = 1; i < rows.length; i++) {
    if (String(rows[i][0]) === searchRfid) {
      return { success: true, attended: true };
    }
  }
  return { success: true, attended: false };
}

function listEvents_() {
  var sheet = getEventsSheet_();
  var rows = sheet.getDataRange().getValues();
  var events = [];
  for (var i = 1; i < rows.length; i++) {
    if (rows[i][0]) events.push(rows[i][0]);
  }
  return { success: true, data: events };
}

function deleteEvent_(body) {
  var spreadsheetId = getEventSpreadsheetId_(body.eventName);
  if (spreadsheetId) {
    try {
      var ss = SpreadsheetApp.openById(spreadsheetId);
      ss.setTrashed(true);
    } catch (_) {}
  }

  // Remove from Events registry sheet
  var sheet = getEventsSheet_();
  var rows = sheet.getDataRange().getValues();
  for (var i = rows.length - 1; i >= 1; i--) {
    if (rows[i][0] === body.eventName) {
      sheet.deleteRow(i + 1);
      break;
    }
  }
  return { success: true };
}

function getEventDetails_(body) {
  var sheet = getEventsSheet_();
  var rows = sheet.getDataRange().getValues();
  for (var i = 1; i < rows.length; i++) {
    if (rows[i][0] === body.eventName) {
      return {
        success: true,
        data: {
          eventName: rows[i][0],
          spreadsheetId: rows[i][1],
          spreadsheetUrl: rows[i][2],
          createdDate: rows[i][3],
          status: rows[i][4] || 'active'
        }
      };
    }
  }
  return { success: false, error: 'Event not found: ' + body.eventName };
}

// ── Batched scan: member_exists + check_attended + record in one call ──

function scanAttendance_(body) {
  var member = getMember_({ rfid: body.rfid });
  if (!member.success || !member.data) {
    return { success: false, error: 'RFID number not found' };
  }

  var check = checkAttended_({ eventName: body.eventName, rfid: body.rfid });
  if (check.attended) {
    return { success: true, attended: true, member: member.data };
  }

  var spreadsheetId = getEventSpreadsheetId_(body.eventName);
  if (!spreadsheetId) {
    return { success: false, error: 'Event not found: ' + body.eventName };
  }

  var ss = SpreadsheetApp.openById(spreadsheetId);
  var sheet = ss.getSheetByName('Attendance');
  if (!sheet) {
    return { success: false, error: 'Attendance sheet not found in event spreadsheet' };
  }
  var headers = ['rfid', 'memberid', 'student_num', 'name', 'attendance_time'];
  ensureHeaders_(sheet, headers);
  sheet.getRange('A:A').setNumberFormat('@');

  var now = new Date();
  var timeStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm:ss');
  sheet.appendRow([member.data.rfid, member.data.memberid, member.data.student_num, member.data.name, timeStr]);

  return { success: true, attended: false, member: member.data, attendanceTime: timeStr };
}
