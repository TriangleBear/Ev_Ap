import customtkinter as CTk

class ThemeManager:
    def __init__(self, app):
        self.app = app

    def apply_theme(self, new_appearance_mode):
        CTk.set_appearance_mode(new_appearance_mode)

        if new_appearance_mode == "Light":
            text_color = "black"
            sub_text_color = "gray20"
        elif new_appearance_mode == "Dark":
            text_color = "white"
            sub_text_color = "gray80"
        else:  # System mode - get current system-based theme colors
            current_theme = CTk.ThemeManager.theme
            text_color = current_theme["CTkLabel"]["text_color"]
            sub_text_color = text_color  # or override if needed

        # Apply text colors
        self.app.app_title.configure(text_color=text_color)
        self.app.db_status_label.configure(text_color=sub_text_color)

        if hasattr(self.app, 'appearance_mode_label'):
            self.app.appearance_mode_label.configure(text_color=text_color)

        for key in self.app.nav_buttons:
            self.app.nav_buttons[key].configure(text_color=text_color)