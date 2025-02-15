from rfid_app import RFIDApp

class RFIDApp(RFIDApp):
    def __init__(self):
        super().__init__()

    def run(self):
        super().run()

if __name__ == "__main__":
    app = RFIDApp()
    app.run()