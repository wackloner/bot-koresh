import logging
import os


def restart_tor():
    logging.debug(f"Restarting tor: 'sudo killall -HUP tor'")
    res = os.system('sudo killall -HUP tor')
    logging.debug(f'Restarted: {res}')
