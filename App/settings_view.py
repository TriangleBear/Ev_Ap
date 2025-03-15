import customtkinter as CTk
from tkinter.colorchooser import askcolor

class SettingsView(CTk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        self.header = CTk.CTkLabel(self, text="Settings", font=CTk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)
        
        # Settings options
        self.options_frame = CTk.CTkFrame(self)
        self.options_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Appearance mode setting
        appearance_label = CTk.CTkLabel(self.options_frame, text="Appearance Mode:", font=CTk.CTkFont(size=18))
        appearance_label.pack(anchor="w", padx=10, pady=10)
        
        self.appearance_mode_menu = CTk.CTkOptionMenu(
            self.options_frame, 
            values=["Light", "Dark", "System"],
            command=self.app.change_appearance_mode
        )
        self.appearance_mode_menu.pack(anchor="w", padx=10, pady=10)
        self.appearance_mode_menu.set("System")
        
        # Color customization settings
        color_label = CTk.CTkLabel(self.options_frame, text="Customize Colors:", font=CTk.CTkFont(size=18))
        color_label.pack(anchor="w", padx=10, pady=10)
        
        self.bg_color_button = CTk.CTkButton(self.options_frame, text="Background Color", command=self.choose_bg_color)
        self.bg_color_button.pack(anchor="w", padx=10, pady=5)
        
        self.fg_color_button = CTk.CTkButton(self.options_frame, text="Foreground Color", command=self.choose_fg_color)
        self.fg_color_button.pack(anchor="w", padx=10, pady=5)
        
        self.apply_button = CTk.CTkButton(self.options_frame, text="Apply Colors", command=self.apply_colors)
        self.apply_button.pack(anchor="w", padx=10, pady=20)
        
        # Load saved colors
        self.load_colors()

    def choose_bg_color(self):
        color = askcolor()[1]
        if color:
            self.bg_color = color

    def choose_fg_color(self):
        color = askcolor()[1]
        if color:
            self.fg_color = color

    def apply_colors(self):
        if hasattr(self, 'bg_color'):
            self.app.root.configure(bg=self.bg_color)
            self.save_color('bg_color', self.bg_color)
        if hasattr(self, 'fg_color'):
            self.header.configure(text_color=self.fg_color)
            self.save_color('fg_color', self.fg_color)

    def save_color(self, color_type, color_value):
        with open('color_settings.txt', 'w') as file:
            file.write(f'{color_type}:{color_value}\n')

    def load_colors(self):
        try:
            with open('color_settings.txt', 'r') as file:
                lines = file.readlines()
                for line in lines:
                    color_type, color_value = line.strip().split(':')
                    if color_type == 'bg_color':
                        self.app.root.configure(bg=color_value)
                    elif color_type == 'fg_color':
                        self.header.configure(text_color=color_value)
        except FileNotFoundError:
            pass