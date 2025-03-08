import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="function")
def browser():
    service = Service(ChromeDriverManager().install())  # Use Service for WebDriver
    driver = webdriver.Chrome(service=service)  # Pass the service instance
    driver.maximize_window()
    yield driver
    driver.quit()
