import requests

def send_telegram_message(text:str):
    url = f"https://api.telegram.org/bot5221774800:AAGv9UnxzfrvbdgzPQs8dMNu4ppgotPHMX8/sendMessage?chat_id=-802602199&parse_mode=html&text={text}"
    try:
        r = requests.get(url=url)
        if r.status_code == 200:
            print("Telegram message sent successfully")
            return True
    except Exception as e:
        print(e)
        return False