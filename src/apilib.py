import requests
import json
import logging
import toml
from datetime import datetime
import os

# logging.basicConfig(level=logging.INFO)
# DOESN'T WORK: logging.getLogger("requests").setLevel(logging.WARNING) # Disable requests logging

BASE_URL = "https://api.smartthings.com"
CONFIG_PATH = "configs/"


def getToken():
    # Get token from the credentials file
    with open(f"{CONFIG_PATH}credentials.toml") as f:
        token = toml.load(f)["token"]
    return "Bearer " + token

def getConfig():
    # Get the config file
    with open(f"{CONFIG_PATH}config.toml") as f:
        config = toml.load(f)
    return config

def getUnits():

    # Get all devices from the config
    units = getConfig()["units"]

    # Get all devices on smartthings
    response = requests.get(f"{BASE_URL}/devices", headers={"Authorization": getToken()})
    try:
        response = response.json()
    except json.decoder.JSONDecodeError:
        logging.error("JSON Decode Error (use debug to view response)")
        logging.debug(response.text)

    codes = response["items"]

    # Zip the names from the config to the devices id from smartthings
    devices = []
    for unit, label in units.items():
        for code in codes:
            if code["label"] == label:
                devices.append({"unit": unit, "deviceId": code["deviceId"], "label": label})

    # Devices = [ {unit: "unit01", deviceId: "deviceId", label: "label"} ]
    return devices


def getUnitStatus(deviceId):
    # Get the status of a specific device
    response = requests.get(f"{BASE_URL}/devices/{deviceId}/status", headers={"Authorization": getToken()})
    try:
        response = response.json()
    except json.decoder.JSONDecodeError:
        logging.error("JSON Decode Error (use debug to view response)")
        logging.debug(response.text)

    return response

# Simpliefied function to get only the relevant information
def getSimplifiedStatus(unit):
    status = getUnitStatus(unit["deviceId"])
    return {
        "unit": unit["unit"],
        "deviceId": unit["deviceId"],
        "label": unit["label"],
        "switch": status["components"]["main"]["switch"]["switch"]["value"],
        "setpoinTemperature": status["components"]["main"]["thermostatCoolingSetpoint"]["coolingSetpoint"]["value"],
        "measuredTemperature": status["components"]["main"]["temperatureMeasurement"]["temperature"]["value"],
        "mode": status["components"]["main"]["airConditionerMode"]["airConditionerMode"]["value"],
        # "fan": status["components"]["main"]["fanMode"]["value"],
    }

def getCurrentInterval():
    # Get the program that should be running
    config = getConfig()
    date_festive_straordinarie = config["general"]["date_festive_straordinarie"]
    program = config["general"]["programma"]
    # Get the current time and day
    today = datetime.now().date()
    now = datetime.now().time()
    if 0 <= today.weekday() <= 4:
        today_tipo = "feriali"
    else:
        today_tipo = "festivi"

    if today.strftime("%d-%m") in date_festive_straordinarie:
        today_tipo = "festivi"

    # Get the program for the current day
    for interval in config["programmi"][program]["orari"][today_tipo]:
        start = datetime.strptime(interval["inizio"], "%H:%M").time()
        end = datetime.strptime(interval["fine"], "%H:%M").time()

        # If the end time is 00:00, it means that the interval goes until the end of the day,
        # so we need to change it to 23:59
        if end == datetime.strptime("00:00", "%H:%M").time():
            end = datetime.strptime("23:59:59", "%H:%M:%S").time()
        if start <= now <= end:
            return interval

def getTempFromSetting(setting, unit_internal_code):
    # Get the temperature from the setting
    config = getConfig()
    program = config["general"]["programma"]
    temperature = config["programmi"][program]["temperature"]
    return temperature[unit_internal_code][setting-1] # The settings are 1-indexed


def setTemperature(unit, temperature):
    # Set the temperature of a device
    deviceId = unit["deviceId"]
    response = requests.post(f"{BASE_URL}/devices/{deviceId}/commands", headers={"Authorization": getToken()}, json={
        "commands": [
            {
                "component": "main",
                "capability": "thermostatCoolingSetpoint",
                "command": "setCoolingSetpoint",
                "arguments": [temperature]
            }
        ]
    })
    logging.info(f"Set temperature to {temperature} on device {unit["label"]}")
    return response.status_code == 200

def switchUnit(unit, switch):
    # Switch a device on or off
    # switch == True or False
    deviceId = unit["deviceId"]
    if switch:
        command = "on"
    else:
        command = "off"

    response = requests.post(f"{BASE_URL}/devices/{deviceId}/commands", headers={"Authorization": getToken()}, json={
        "commands": [
            {
                "component":"main",
                "capability":"switch",
                "command": command,
                "argument": ""
            }
        ]
    })
    logging.info(f"Set switch to {command} on device {unit['label']}")
    return response.status_code == 200

def getModalitaAuto():
    # Get the status of the automatic mode
    config = getConfig()
    return config["general"]["modalita_auto"]

def getOldInterval():
    # Get the old interval
    try:
        with open(f"{CONFIG_PATH}old_interval.toml") as f:
            oldInterval = toml.load(f)["oldInterval"]
    except FileNotFoundError:
        oldInterval = None
    return oldInterval

def setOldInterval(interval):
    # Save the old program
    with open(f"{CONFIG_PATH}old_interval.toml", "w") as f:
        toml.dump({"oldInterval": interval}, f)

def cleanup():
    # Remove the old program file
    try:
        os.remove(f"{CONFIG_PATH}old_interval.toml")
    except FileNotFoundError:
        pass