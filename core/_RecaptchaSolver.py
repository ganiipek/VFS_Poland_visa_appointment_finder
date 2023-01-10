from twocaptcha import TwoCaptcha
from core._ConfigReader import _ConfigReader
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait             # To wait
from selenium.webdriver.support import expected_conditions as EC    # To wait

class _RecaptchaSolver:
    def __init__(self):
        self._config_reader = _ConfigReader()
        self._2captcha_key = self._config_reader.read_prop(
            "DEFAULT", "2captcha_api_key")
        self._solver = TwoCaptcha(self._2captcha_key)

    def balance(self):
        return self._solver.balance()
    
    def get_sitekey(self, driver):
        # my_src = driver.find_element(
        #         By.XPATH, "//iframe[contains(@src,'https://www.google.com/recaptcha/api2/anchor')]").get_attribute("src")
        # parts = my_src.split("?k=")
        # return parts[1]
        return "6LdJReUUAAAAAPR1hddg-9JUC_TO13OrlKVpukHL"
    
    def get_token(self, site_key, page_url):
        return self._solver.recaptcha(
            sitekey=site_key,
            url=page_url)

    def form_submit(self, driver, token):
        driver.execute_script(
            "document.getElementById('g-recaptcha-response').innerHTML='{}';".format(token)
        )
        driver.execute_script(f"___grecaptcha_cfg.clients[0].B.B.callback('{token}')")

        # driver.execute_script("onSuccess('{}')".format(token))
        time.sleep(1)

    def solve_recaptcha(self, driver, url):
        site_key = self.get_sitekey(driver)
        token = self.get_token(site_key, url)
        self.form_submit(driver, token["code"])
        # return driver.find_element_by_class_name("recaptcha-success").text
        return True
