import requests

class _TelegramManager():
    def __init__(self, logging):
        self._logging = logging
        self.chat_id = "-802602199"
        self.bot_id = "5221774800:AAGv9UnxzfrvbdgzPQs8dMNu4ppgotPHMX8"

    def send_message(self, text:str):
        url = f"https://api.telegram.org/bot{self.bot_id}/sendMessage?chat_id={self.chat_id}&parse_mode=html&text={text}"
        try:
            r = requests.get(url=url)
            if r.status_code == 200:
                self._logging.debug("Message sent to Telegram: {}".format(text))
                return True
        except Exception as e:
            self._logging.error(e)
            return False