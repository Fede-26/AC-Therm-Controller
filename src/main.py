from apilib import *
from pprint import pprint
import logging
from logging.handlers import RotatingFileHandler
import time

logging.basicConfig(
        handlers=[RotatingFileHandler('./application.log', maxBytes=100000, backupCount=10)],
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S')

def main():

    # Get the current program
    interval = getCurrentInterval()
    # Get the old program (from the last time the script was run)
    oldInterval = getOldInterval()

    # Set the current program if the programs has changed
    if interval != oldInterval:
        logging.info(f"Interval has changed from {oldInterval} to {interval}")
        if getModalitaAuto():
            for unit in getUnits():
                temperature = getTempFromSetting(getCurrentInterval()["programma"], unit["unit"])
                # print(f"Unit: {unit['label']}, Temperature: {temperature}", end='   ')
                if temperature == 0.0:
                    # Switch the unit off
                    if not switchUnit(unit, False):
                        logging.error(f"Failed to switch off unit {unit['label']}")
                    pass
                else:
                    # Switch the unit on
                    if not switchUnit(unit, True):
                        logging.error(f"Failed to switch on unit {unit['label']}")
                    if not setTemperature(unit, temperature):
                        logging.error(f"Failed to set temperature for unit {unit['label']}")
        setOldInterval(interval) # Save the new program as the old program
    else:
        logging.debug("Program has not changed")


if __name__ == "__main__":
    # Run the main function every 5 minutes
    try:
        while True:
            main()
            time.sleep(60*5)
    except KeyboardInterrupt:
        logging.info("Exiting...")
        cleanup()
        logging.info("Cleanup complete")
