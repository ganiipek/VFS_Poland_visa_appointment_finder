from selenium.webdriver import Chrome, ChromeOptions
# To find the elements
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait             # To wait
from selenium.webdriver.support import expected_conditions as EC    # To wait
# To resize the chrome window
from selenium.webdriver.chrome.options import Options
# To apply try/except
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import requests
import time

from twocaptcha import TwoCaptcha
solver = TwoCaptcha('8ad541582c76eca15bf84750aaf3ff7c')

# driver_path = r"C:\Program Files (x86)\chromedriver_win32\chromedriver.exe"
# brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# option = webdriver.ChromeOptions()
# option.binary_location = brave_path

browser = Chrome()

browser.get("https://www.google.com/recaptcha/api2/demo")

site_key_element = WebDriverWait(browser, 20).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-sitekey]")))
				

site_key = site_key_element.get_attribute("data-sitekey")
print(site_key)
page_url = "https://www.google.com/recaptcha/api2/demo"
method = "userrecaptcha"
key = "8ad541582c76eca15bf84750aaf3ff7c"

result = solver.recaptcha(sitekey=site_key,
                          url=page_url)

print(result)
print(result["code"])


# token_url = "http://2captcha.com/res.php?key={}&action=get&id={}".format(
#     key, captcha_id)

# while True:
#     time.sleep(10)
#     response = requests.get(token_url)

#     if response.text[0:2] == 'OK':
#     	break


# captha_results = response.text[3:]
browser.execute_script(
    """document.querySelector('[name="g-recaptcha-response"]').innerText='{}'""".format(result["code"]))

WebDriverWait(browser, 20).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[id="recaptcha-demo-submit"]'))).click()

time.sleep(30)
