import logging
import time
import datetime
from enum import Enum

from selenium.webdriver import Chrome, ChromeOptions
# To find the elements
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait             # To wait
from selenium.webdriver.support import expected_conditions as EC    # To wait
# To resize the chrome window
from selenium.webdriver.chrome.options import Options
# To apply try/except
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from core._ConfigReader import _ConfigReader
from core._Telegram import send_telegram_message

class Page(Enum):
    START = 0
    LOGIN = 1
    CONFIRMATION = 2
    USER_DETAILS = 3
    APPOINTMENT_DETAILS = 4
    APPOINTMENT_CONFIRMATION = 5


class _VfsClient:
    def __init__(self):
        self._config_reader = _ConfigReader()
        self._current_page = Page.START

    def _init_web_driver(self):
        options = ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        self._web_driver = Chrome(options=options)# open the webpage
        time.sleep(5)
        self._web_driver.maximize_window()
        self._web_driver.get("https://visa.vfsglobal.com/tur/en/pol/login")
        time.sleep(10)

    def _login(self):
        vfs_account_email = self._config_reader.read_prop("VFS", "vfs_email")
        vfs_account_password = self._config_reader.read_prop(
            "VFS", "vfs_password")

        logging.debug("Logging in with email: {}".format(vfs_account_email))

        time.sleep(5)

        WebDriverWait(self._web_driver, 10) \
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div#onetrust-button-group button#onetrust-accept-btn-handler"))) \
            .click()

        _email_input = self._web_driver.find_element(By.ID, "mat-input-0")
        _email_input.send_keys(vfs_account_email)
        _password_input = self._web_driver.find_element(By.ID, "mat-input-1")
        _password_input.send_keys(vfs_account_password)

        WebDriverWait(self._web_driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")))
        WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "div.recaptcha-checkbox-border"))).click()

        # The user will manually solve Recaptcha here. Then, the code below will click on Sign In
        # Recaptcha can be easily solved within 15 seconds
        logging.debug("Bot is waiting for Recaptch solved")
        time.sleep(15)

        self._web_driver.switch_to.default_content()
        WebDriverWait(self._web_driver, 40).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.mat-focus-indicator.btn.mat-btn-lg.btn-block.btn-brand-orange.mat-stroked-button.mat-button-base"))).click()
        
        time.sleep(5)

        self._set_current_page(Page.CONFIRMATION)

    def _set_current_page(self, page):
        self._current_page = page
        print("Current page: {}".format(self._current_page))

    def _fill_confirmation_page(self):
        #####################
        # Confirmations page
        #####################
        try: 
            self._web_driver.maximize_window()
            time.sleep(1)  # Based on my experiments, 12 seconds should be enough

            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(.//text(),'before scheduling')]"))).click()
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(.//text(), 'choose the correct' )]"))).click()

            # When the page is narrowed by the sides, the location of the button is changing and finally the click operation works
            self._web_driver.set_window_size(100, 700)
            # Button class içindeki yazıyı, boşlukları noktalarla değiştirerek yaz. Bekleme yapmadan da çalışmadı bu nedense, stackoverflow'da öyle çözmüş biri
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.mat-focus-indicator.btn.mat-btn-lg.btn-block.btn-brand-orange.mat-raised-button.mat-button-base"))).click()

            ############################
            # Terms and Conditions page
            ############################
            # Tıkladığında, inspect tarafında renklenen kısmın içindeki "id" değerini gir
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(.//text(), 'Continue Terms and Conditions' )]"))).click()

            # Button class içindeki yazıyı, boşlukları noktalarla değiştirerek yaz. Bekleme yapmadan da çalışmadı bu nedense, stackoverflow'da öyle çözmüş biri
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.mat-focus-indicator.btn.mat-btn-lg.btn-block.btn-brand-orange.mat-stroked-button.mat-button-base"))).click()

            # To easily observe the future operations on the page, turn the window into the maximized version
            self._web_driver.maximize_window()

            return True
        except Exception as error:
            logging.debug("Unable to fill the confirmation page")
            return False

    def _fill_personal_details_page(self):
        try:
            first_name = self._config_reader.read_prop("USER", "user_first_name")
            last_name = self._config_reader.read_prop("USER", "user_last_name")
            gender = self._config_reader.read_prop("USER", "user_gender")
            passport_number = self._config_reader.read_prop("USER", "user_passport_number")
            country_calling_code = self._config_reader.read_prop("USER", "user_phone_country_code")
            phone_number = self._config_reader.read_prop("USER", "user_phone_number")
            email = self._config_reader.read_prop("USER", "user_email")

            time.sleep(2)
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div/span[contains(., 'Select' )]"))).click()
            # Because of the blank spaces at the start&end of the options of dropdown menu, this syntax is used
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//mat-option/span[text()=' " + gender + " ']"))).click()

            # If it does not wait for a while, it does not click to the next dropdown
            time.sleep(2)
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div/span[contains(., 'Select' )]"))).click()
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//mat-option/span[contains(., 'Turkiye')]"))).click()

            # Since it created problems, I moved non-dropdown ones after the dropdown ones
            self._web_driver.find_element(
                By.XPATH, "//input[@placeholder='Enter your first name']").send_keys(first_name)
            self._web_driver.find_element(
                By.XPATH, "//input[@placeholder='Please enter last name.']").send_keys(last_name)
            self._web_driver.find_element(
                By.XPATH, "//input[@placeholder='Enter passport number']").send_keys(passport_number)
            self._web_driver.find_element(
                By.XPATH, "//input[@placeholder='44']").send_keys(country_calling_code)
            self._web_driver.find_element(
                By.XPATH, "//input[@placeholder='012345648382']").send_keys(phone_number)
            self._web_driver.find_element(
                By.XPATH, "//input[@placeholder='Enter Email Address']").send_keys(email)

            # Write the text inside of the Button class, by replacing "blanks" with "dots"
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.mat-focus-indicator.mat-stroked-button.mat-button-base.btn.btn-block.btn-brand-orange.mat-btn-lg"))).click()

            time.sleep(5)
            return True
        except Exception as error:
            logging.debug("Unable to fill the personal details page")
            print(error)
            return False

    def _fill_appointment_page(self):
        try:
            category = self._config_reader.read_prop("USER", "user_visa_category")
            sub_category = self._config_reader.read_prop("USER", "user_visa_sub_category")
            visa_centre = self._config_reader.read_prop("USER", "user_visa_centre")

            logging.info("Getting appointment date: Category: {}, Sub-Category: {}, Visa Centre: {}".format(category, sub_category, visa_centre)) 
            
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div/span[contains(., 'appointment category' )]"))).click()   # Opens the Drop-down menu
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//mat-option/span[contains(., 'National' )]"))).click()        # Clicks on the option

            time.sleep(2)
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div/span[contains(., 'sub-category' )]"))).click()
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//mat-option/span[contains(., 'Turkish')]"))).click()

            time.sleep(2)
            return True
        except:
            logging.debug("Unable to fill the appointment page")
            return False

    def _get_appointment_date(self):
        visa_centre = self._config_reader.read_prop("USER", "user_visa_centre")

        WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "//div/span[contains(., 'Application Centre' )]"))).click()
        # Any centre that is connected to Istanbul region is fine. I tested through "Reconsideration" category, since I saw availability for all 5 cities. When the "Poland in Istanbul" text is used, it selected the first city that includes this phrase
        try:
            WebDriverWait(self._web_driver, 7).until(EC.element_to_be_clickable(
                (By.XPATH, "//mat-option/span[contains(., 'Poland in Ankara')]"))).click()

            return True
        except TimeoutException:
            logging.debug("Visa centre not found: {}".format(visa_centre))
            print("Visa centre not found: {}".format(visa_centre))
            return False

    def check_slot(self, attempt=0):
        while True:
            if self._current_page == Page.CONFIRMATION:
                if self._fill_confirmation_page():
                    self._set_current_page(Page.USER_DETAILS)

            if self._current_page == Page.USER_DETAILS:
                if self._fill_personal_details_page():
                    self._set_current_page(Page.APPOINTMENT_DETAILS)

            if self._current_page == Page.APPOINTMENT_DETAILS:
                if self._fill_appointment_page():
                    if self._get_appointment_date():
                        self._set_current_page(Page.APPOINTMENT_CONFIRMATION)

                    else:
                        logging.info("No slots available")

                        WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                            (By.ID, "navbarDropdown"))).click()           # Click on "My Account"
                        WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                            (By.CLASS_NAME, "dropdown-item"))).click()    # Click on "Dashboard"

                        self._set_current_page(Page.CONFIRMATION)
                        break
                    # Close the browser
                    # self._web_driver.close()
                    # self._web_driver.quit()
            if self._current_page == Page.APPOINTMENT_CONFIRMATION:
                first_name = self._config_reader.read_prop("USER", "user_first_name")
                last_name = self._config_reader.read_prop("USER", "user_last_name")
                server_host = self._config_reader.read_prop("DEFAULT", "server_host")
                message = "[{}] Appointment slots available. Name: {}, Last Name: {}, Attempt: {}".format(server_host, first_name, last_name, attempt)

                if send_telegram_message(message):
                    logging.info(message)
                    time.sleep(10)
                    # self._set_current_page(Page.START) # Sürekli mesaj atması için kapatıldı