import customtkinter as CTk

class ThemeManager: #Sauce: "Button Foreground change color during light,dark,system mode"
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

    def get_disabled_bg_color(self):
        current_mode = CTk.get_appearance_mode()
        if current_mode == "Light":
            return "#f0f0f0"  # Light gray for light mode
        elif current_mode == "Dark":
            return "#1a1a1a"  # Dark gray for dark mode
        else:  # System mode
            return "#f0f0f0"  # Default to light gray
        
    def get_disabled_text_color(self):
        current_mode = CTk.get_appearance_mode()
        if current_mode == "Light":
            return "#666666"  # Darker gray for better contrast in light mode
        elif current_mode == "Dark":
            return "#aaaaaa"  # Lighter gray for better contrast in dark mode
        else:  # System mode
            return "#666666"  # Default to darker gray