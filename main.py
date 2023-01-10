import sys
import logging

from logging.config import fileConfig
from core._Timer import countdown
from core._ConfigReader import _ConfigReader
from core._VfsClient import _VfsClient
from core._Telegram import _TelegramManager

if __name__ == "__main__":
    count = 1
    fileConfig('config/logging.ini')
    logging = logging.getLogger(__name__);

    _config_reader = _ConfigReader()
    _interval = _config_reader.read_prop("DEFAULT", "interval");

    logging.debug("Interval: {}".format(_interval))
    logging.info("Starting VFS Appointment Bot")

    _vfs_client = _VfsClient(logging)
    _vfs_client._init_web_driver()

    _telegram_manager = _TelegramManager(logging)

    while True:
        try:
            logging.info("Running VFS Appointment Bot: Attempt#{}".format(count))
            _vfs_client.check_slot(attempt=count)
            logging.debug("Sleeping for {} seconds".format(_interval))
            countdown(int(_interval))
        except Exception as error:
            logging.info(error)
            # logging.debug(e, exc_info=True, stack_info=True)
            _telegram_manager.send_message("VFS Appointment Bot: Error occured. Please check the logs for more details")
            countdown(int(30))
            pass
        print("\n")
        count += 1