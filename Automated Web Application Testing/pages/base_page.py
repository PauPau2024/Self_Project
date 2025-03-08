from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By

class BasePage:
    def __init__(self,driver):
        self.driver = driver
        self.wait = WebDriverWait(driver,10)
    
    def open_url(self,url):
        self.driver.get(url)

    def find_element(self,by,locator):
        return self.wait.until(EC.presence_of_element_located((by,locator)))

    def click_element(self,by,locator):
        element = self.find_element(by,locator)
        element.click()

    def enter_text(self,by,locator, text):
        element = self.find_element(by,locator)
        element.clear()
        element.send_keys(text)
                
