from pages.login_page import LoginPage

def test_basic_auth_login(browser):
    login_page = LoginPage(browser)
    login_page.login("admin","admin")

    assert "Congratulations" in browser.page_source
    print("Login Success")