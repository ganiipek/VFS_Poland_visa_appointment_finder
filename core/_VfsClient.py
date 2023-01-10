

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

from fake_useragent import UserAgent


from core._ConfigReader import _ConfigReader
from core._Telegram import _TelegramManager
from core._RecaptchaSolver import _RecaptchaSolver


class Page(Enum):
    START = 0
    LOGIN = 1
    CONFIRMATION = 2
    USER_DETAILS = 3
    APPOINTMENT_DETAILS = 4
    APPOINTMENT_CONFIRMATION = 5
    PAGE_NOT_FOUND = 6


class _VfsClient:
    def __init__(self, logging):
        self._config_reader = _ConfigReader()
        self._recaptcha_solver = _RecaptchaSolver()
        self._logging = logging
        self._telegram_manager = _TelegramManager(logging)
        self._current_page = Page.LOGIN
        self._error_count = 0

    def _init_web_driver(self):
        options = ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")

        self._web_driver = Chrome(options=options)  # open the webpage
        time.sleep(5)
        self._web_driver.maximize_window()
        self._web_driver.get("https://visa.vfsglobal.com/tur/en/pol/login")
        time.sleep(10)

    def _check_page(self):
        try:
            if self._web_driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/h1").text == "Access denied":
                self._set_current_page(Page.PAGE_NOT_FOUND)
                # self._telegram_manager.send_message("Access denied. Try again login")
        except NoSuchElementException as error:
            if self._web_driver.current_url == "https://visa.vfsglobal.com/tur/en/pol/login":
                self._set_current_page(Page.LOGIN)

            elif self._web_driver.current_url == "https://visa.vfsglobal.com/tur/en/pol/dashboard":
                self._set_current_page(Page.CONFIRMATION)

            elif self._web_driver.current_url == "https://visa.vfsglobal.com/tur/en/pol/your-details":
                self._set_current_page(Page.USER_DETAILS)

            elif self._web_driver.current_url == "https://visa.vfsglobal.com/tur/en/pol/applicationdetails":
                self._set_current_page(Page.APPOINTMENT_DETAILS)

            if self._web_driver.current_url == "https://visa.vfsglobal.com/tur/en/pol/page-not-found":
                self._set_current_page(Page.PAGE_NOT_FOUND)
                # self._telegram_manager.send_message("Page not found. Try again login")

    def _set_current_page(self, page):
        self._current_page = page
        print("Current page: {}".format(self._current_page))

    def _fill_login_page(self):
        try:
            vfs_account_email = self._config_reader.read_prop(
                "VFS", "vfs_email")
            vfs_account_password = self._config_reader.read_prop(
                "VFS", "vfs_password")

            self._logging.debug(
                "self._logging in with email: {}".format(vfs_account_email))

            time.sleep(5)

            # WebDriverWait(self._web_driver, 10) \
            #     .until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div#onetrust-button-group button#onetrust-accept-btn-handler"))) \
            #     .click()

            _email_input = self._web_driver.find_element(By.ID, "mat-input-0")
            _email_input.send_keys(vfs_account_email)
            _password_input = self._web_driver.find_element(
                By.ID, "mat-input-1")
            _password_input.send_keys(vfs_account_password)

            self._logging.debug("Bot is waiting for Recaptch solved")
            result = self._recaptcha_solver.solve_recaptcha(
                driver=self._web_driver,
                url='https://visa.vfsglobal.com/tur/en/pol/login')

            # The user will manually solve Recaptcha here. Then, the code below will click on Sign In
            # Recaptcha can be easily solved within 15 seconds
            time.sleep(5)

            self._web_driver.switch_to.default_content()
            WebDriverWait(self._web_driver, 40).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.mat-focus-indicator.btn.mat-btn-lg.btn-block.btn-brand-orange.mat-stroked-button.mat-button-base"))).click()

            time.sleep(5)

            self._error_count = 0
            return True
        except Exception as error:
            self._logging.error(error)
            self._error_count += 1
            return False

    def _fill_confirmation_page(self):
        try:
            self._web_driver.maximize_window()
            # Based on my experiments, 12 seconds should be enough
            time.sleep(1)

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

            self._error_count = 0
            return True
        except Exception as error:
            self._logging.error(error)
            self._error_count += 1
            return False

    def _fill_personal_details_page(self):
        try:
            first_name = self._config_reader.read_prop(
                "USER", "user_first_name")
            last_name = self._config_reader.read_prop("USER", "user_last_name")
            gender = self._config_reader.read_prop("USER", "user_gender")
            passport_number = self._config_reader.read_prop(
                "USER", "user_passport_number")
            country_calling_code = self._config_reader.read_prop(
                "USER", "user_phone_country_code")
            phone_number = self._config_reader.read_prop(
                "USER", "user_phone_number")
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

            self._error_count = 0
            return True
        except Exception as error:
            self._logging.error(error)
            self._error_count += 1
            return False

    def _fill_appointment_page(self):
        category = self._config_reader.read_prop("USER", "user_visa_category")
        sub_category = self._config_reader.read_prop("USER", "user_visa_sub_category")
        visa_centre = self._config_reader.read_prop("USER", "user_visa_centre")

        try:
            self._logging.info("Getting appointment date: Category: {}, Sub-Category: {}, Visa Centre: {}".format(
                category, sub_category, visa_centre))

            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div/span[contains(., 'appointment category' )]"))).click()   # Opens the Drop-down menu
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//mat-option/span[contains(., '{}' )]".format(category)))).click()        # Clicks on the option

            time.sleep(2)
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div/span[contains(., 'sub-category' )]"))).click()
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//mat-option/span[contains(., '{}')]".format(sub_category)))).click()

            time.sleep(2)

            self._error_count = 0
            return True
        except Exception as error:
            self._logging.error(error)
            self._error_count += 1
            return False

    def _get_appointment_date(self):
        visa_centre = self._config_reader.read_prop("USER", "user_visa_centre")

        try:
            WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//div/span[contains(., 'Application Centre' )]"))).click()
            # Any centre that is connected to Istanbul region is fine. I tested through "Reconsideration" category, since I saw availability for all 5 cities. When the "Poland in Istanbul" text is used, it selected the first city that includes this phrase

            WebDriverWait(self._web_driver, 7).until(EC.element_to_be_clickable(
                (By.XPATH, "//mat-option/span[contains(., '{}')]".format(visa_centre)))).click()

            return True
        except TimeoutException:
            self._logging.debug(
                "Visa centre not found: {}".format(visa_centre))
            
            self._error_count = 0
            return False

        except Exception as error:
            self._logging.error(error)
            self._error_count += 1
            return False

    def check_slot(self, attempt=0):
        while True:
            time.sleep(5)
            self._check_page();

            if self._error_count > 5:
                self._logging.error("Too many errors. Count: {}".format(self._error_count))
                self._telegram_manager.send_message("Too many errors. Count: {} Page: {}".format(self._error_count, self._current_page))

            if self._current_page == Page.PAGE_NOT_FOUND:
                self._web_driver.get("https://visa.vfsglobal.com/tur/en/pol/login")
                time.sleep(5)
                self._set_current_page(Page.LOGIN)

            elif self._current_page == Page.LOGIN:
                if self._fill_login_page():
                    self._set_current_page(Page.CONFIRMATION)
                else:
                    time.sleep(10)

            elif self._current_page == Page.CONFIRMATION:
                if self._fill_confirmation_page():
                    self._set_current_page(Page.USER_DETAILS)
                else:
                    time.sleep(10)

            elif self._current_page == Page.USER_DETAILS:
                if self._fill_personal_details_page():
                    self._set_current_page(Page.APPOINTMENT_DETAILS)
                else:
                    time.sleep(10)

            elif self._current_page == Page.APPOINTMENT_DETAILS:
                if self._fill_appointment_page():
                    if self._get_appointment_date():
                        self._set_current_page(Page.APPOINTMENT_CONFIRMATION)
                    else:
                        self._logging.info("No slots available")

                        WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                            (By.ID, "navbarDropdown"))).click()           # Click on "My Account"
                        WebDriverWait(self._web_driver, 20).until(EC.element_to_be_clickable(
                            (By.CLASS_NAME, "dropdown-item"))).click()    # Click on "Dashboard"

                        self._set_current_page(Page.CONFIRMATION)
                        break
                    # Close the browser
                    # self._web_driver.close()
                    # self._web_driver.quit()
            elif self._current_page == Page.APPOINTMENT_CONFIRMATION:
                first_name = self._config_reader.read_prop(
                    "USER", "user_first_name")
                last_name = self._config_reader.read_prop(
                    "USER", "user_last_name")
                server_host = self._config_reader.read_prop(
                    "DEFAULT", "server_host")
                bot_name = self._config_reader.read_prop("DEFAULT", "bot_name")

                message = "[{} - {}] Appointment slots available. Name: {}, Last Name: {}, Attempt: {}".format(
                    server_host, bot_name, first_name, last_name, attempt)

                if self._telegram_manager.send_telegram_message(message):
                    self._logging.info(message)
                    time.sleep(5)
                    # self._set_current_page(Page.START) # Sürekli mesaj atması için kapatıldı
