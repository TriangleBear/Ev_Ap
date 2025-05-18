class ThemeManager:
    def __init__(self, app):
        self.app = app

    def apply_theme(self, new_appearance_mode):
        if new_appearance_mode == "Light":
            self.app.app_title.configure(text_color="black")
            self.app.db_status_label.configure(text_color="gray20")
            if hasattr(self.app, 'appearance_mode_label'):
                self.app.appearance_mode_label.configure(text_color="black")
            if "home" in self.app.nav_buttons:
                self.app.nav_buttons["home"].configure(text_color="black")
            if "events" in self.app.nav_buttons:
                self.app.nav_buttons["events"].configure(text_color="black")    
            if "members" in self.app.nav_buttons:
                self.app.nav_buttons["members"].configure(text_color="black")
            if "reports" in self.app.nav_buttons:
                self.app.nav_buttons["reports"].configure(text_color="black")
            if "settings" in self.app.nav_buttons:
                self.app.nav_buttons["settings"].configure(text_color="black")
            if "help" in self.app.nav_buttons:
                self.app.nav_buttons["help"].configure(text_color="black")
            if "about" in self.app.nav_buttons:
                self.app.nav_buttons["about"].configure(text_color="black")
            

        elif new_appearance_mode == "Dark":
            self.app.app_title.configure(text_color="white")
            self.app.db_status_label.configure(text_color="gray80")
            if hasattr(self.app, 'appearance_mode_label'):
                self.app.appearance_mode_label.configure(text_color="white")
            if "home" in self.app.nav_buttons:
                self.app.nav_buttons["home"].configure(text_color="white")
            if "events" in self.app.nav_buttons:
                self.app.nav_buttons["events"].configure(text_color="white")    
            if "members" in self.app.nav_buttons:
                self.app.nav_buttons["members"].configure(text_color="white")
            if "reports" in self.app.nav_buttons:
                self.app.nav_buttons["reports"].configure(text_color="white")
            if "reports" in self.app.nav_buttons:
                self.app.nav_buttons["reports"].configure(text_color="white")
            if "settings" in self.app.nav_buttons:
                self.app.nav_buttons["settings"].configure(text_color="white")
            if "help" in self.app.nav_buttons:
                self.app.nav_buttons["help"].configure(text_color="white")
            if "about" in self.app.nav_buttons:
                self.app.nav_buttons["about"].configure(text_color="white")

        else:  # System mode
            self.app.app_title.configure(text_color=None)
            self.app.db_status_label.configure(text_color=None)
            if hasattr(self.app, 'appearance_mode_label'):
                self.app.appearance_mode_label.configure(text_color=None)

            for key in self.app.nav_buttons:
                self.app.nav_buttons[key].configure(text_color=None)
