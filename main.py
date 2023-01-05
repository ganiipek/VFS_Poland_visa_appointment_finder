import sys
import logging

from logging.config import fileConfig
from core._Timer import countdown
from core._ConfigReader import _ConfigReader
from core._VfsClient import _VfsClient

if __name__ == "__main__":
    count = 1
    fileConfig('config/logging.ini')
    logging = logging.getLogger(__name__);

    _config_reader = _ConfigReader()
    _interval = _config_reader.read_prop("DEFAULT", "interval");

    logging.debug("Interval: {}".format(_interval))
    logging.info("Starting VFS Appointment Bot")

    _vfs_client = _VfsClient()
    _vfs_client._init_web_driver()
    _vfs_client._login()

    while True:
        try:
            logging.info("Running VFS Appointment Bot: Attempt#{}".format(count))
            _vfs_client.check_slot(attempt=count)
            logging.debug("Sleeping for {} seconds".format(_interval))
            countdown(int(_interval))
        except Exception as e:
            logging.info(e.args[0] + ". Please check the logs for more details")
            logging.debug(e, exc_info=True, stack_info=True)
            countdown(int(60))
            pass
        print("\n")
        count += 1