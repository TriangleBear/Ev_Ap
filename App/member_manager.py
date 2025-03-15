import customtkinter as CTk
from CTkMessagebox import CTkMessagebox
from dblite import DBActions
from icecream import ic

class MemberManager:
    def __init__(self, app):
        self.app = app
        self.rfid_cache = {}

    def register_member_button_clicked(self):
        ic("register_member_button_clicked")
        register_window = CTk.CTkToplevel(self.app.root)
        register_window.title("Register New Member")
        register_window.geometry("400x300")
        register_window.attributes('-topmost', True)
        register_window.resizable(False, False)
        self.app.center_window(register_window)

        memberid_entry = CTk.CTkEntry(register_window, placeholder_text="Enter member ID")
        memberid_entry.pack(pady=5)

        name_entry = CTk.CTkEntry(register_window, placeholder_text="Enter name")
        name_entry.pack(pady=5)

        student_num_entry = CTk.CTkEntry(register_window, placeholder_text="Enter student number")
        student_num_entry.pack(pady=5)

        program_entry = CTk.CTkEntry(register_window, placeholder_text="Enter program")
        program_entry.pack(pady=5)

        year_entry = CTk.CTkEntry(register_window, placeholder_text="Enter year")
        year_entry.pack(pady=5)

        rfid_entry = CTk.CTkEntry(register_window, placeholder_text="Scan RFID")
        rfid_entry.pack(pady=5)

        def member_register():
            rfid_num = rfid_entry.get()
            member_id = memberid_entry.get()
            member_name = name_entry.get()
            student_num = student_num_entry.get()
            program = program_entry.get()
            year = year_entry.get()
            print(f"RFID: {rfid_num}")
            print(f"Member ID: {member_id}")
            print(f"Name: {member_name}")
            print(f"Student Number: {student_num}")
            print(f"Program: {program}")
            print(f"Year: {year}")

            if DBActions.member_exists(rfid_num):
                ic("Member already exists!")
                CTkMessagebox(title="Member Registration", message="Member already exists!", icon="error")
                register_window.after(300, register_window.destroy)
            else:
                ic("Registering new member...")
                DBActions.member_register(rfid_num, member_id, member_name, student_num, program, year)
                CTkMessagebox(title="Member Registration", message="Member Registered!", icon="check")
                register_window.after(300, register_window.destroy)

        submit_button = CTk.CTkButton(register_window, text="Submit", command=member_register)
        submit_button.pack(pady=5)

    def redeem_points_button_clicked(self):
        redeem_window = CTk.CTkToplevel(self.app.root)
        redeem_window.title("Redeem Points")
        redeem_window.geometry("400x300")
        redeem_window.attributes('-topmost', True)
        redeem_window.resizable(False, False)
        self.app.center_window(redeem_window)

        rfid_entry = CTk.CTkEntry(redeem_window, placeholder_text="Enter RFID")
        rfid_entry.pack(pady=5)

        points_entry = CTk.CTkEntry(redeem_window, placeholder_text="Enter points to redeem")
        points_entry.pack(pady=5)

        def redeem_points():
            rfid_num = rfid_entry.get().strip()
            if not rfid_num:
                CTkMessagebox(title="Redeem Points", message="RFID cannot be empty!", icon="error")
                return
            points = DBActions.get_member_points(rfid_num)
            if points is None:
                CTkMessagebox(title="Redeem Points", message="Member not found!", icon="error")
                return
            discount_20 = points * 0.20
            discount_50 = points * 0.50
            response = CTkMessagebox(title="Redeem Points", message=f"Points: {points}\n20% Discount: {discount_20}\n50% Discount: {discount_50}", icon="question", option_1="20%", option_2="50%")
            if response.get() == "20%":
                DBActions.redeem_points(rfid_num, discount_20)
            elif response.get() == "50%":
                DBActions.redeem_points(rfid_num, discount_50)
            CTkMessagebox(title="Redeem Points", message="Points redeemed successfully!", icon="check")
            redeem_window.destroy()

        redeem_button = CTk.CTkButton(redeem_window, text="Redeem", command=redeem_points)
        redeem_button.pack(pady=5)