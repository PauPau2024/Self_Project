from pages.base_page import BasePage
from config.config import BASE_URL, USERNAME, PASSWORD

class LoginPage(BasePage):
    def login(self):
        auth_url = f"https://{USERNAME}:{PASSWORD}@{BASE_URL}/basic_auth"
        self.open_url(auth_url)
