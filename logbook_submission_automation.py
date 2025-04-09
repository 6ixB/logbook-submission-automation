"""
================================================================================
Script Name   : logbook_submission_automation.py
Author        : MY23-1
Created       : 2025-04-09
Last Modified : 2025-04-09
Version       : 1.0.0
License       : MIT

Description:
    This script automates login and navigation in a browser using Selenium.
    It extracts cookies after login to enable API access via the `requests` module.
    Intended for automation of post-login data fetching from web applications.

Usage:
    $ python logbook_submission_automation.py

Dependencies:
    - Python 3.9+
    - selenium
    - python-dotenv
    - requests

Change Log:
    - v1.0.0 : Initial release

================================================================================
"""

import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import requests

load_dotenv()

# Constants, change if needed
SLEEP_TIME = 2
ENRINCHMENT_LOGIN_URL = "https://enrichment.apps.binus.ac.id/Login/Student/Login"
ACTIVITY_ENRICHMENT_BASE_URL = "https://activity-enrichment.apps.binus.ac.id"
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TEMPLATE_FILE_PATH = 'template.xlsx'

options = Options()
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(SLEEP_TIME * 5)

session = requests.Session()


def fill_logbook_activity():
    response = session.get(f"{ACTIVITY_ENRICHMENT_BASE_URL}/LogBook/GetMonths")
    response_json = response.json()

    # Get logbooks from the response
    logbooks = response_json["data"]

    # Read the template file
    data = pd.read_excel("template.xlsx", engine='openpyxl')
    data['Month'] = data['Date'].dt.month_name()
    data['InsertDate'] = data['Date'].dt.strftime("%Y-%m-%dT00:00:00")

    for _, row in data.iterrows():
        # Find the logbook for matching months with template row
        logbook = next(
            logbook for logbook in logbooks if logbook["month"] == row["Month"])
        logbook_header_id = logbook["logBookHeaderID"]
        response = session.post(f"{ACTIVITY_ENRICHMENT_BASE_URL}/LogBook/GetLogBook", {
            "logBookHeaderID": logbook_header_id
        })

        logbook_month = response.json()["data"]
        logbook_row = next(
            x for x in logbook_month if x["date"] == row["InsertDate"])

        # Construct data for the logbook entry
        data = {
            "ID": logbook_row["id"],
            "LogBookHeaderID": logbook_header_id,
            "Date": row["InsertDate"],
            "Activity": row["Activity"],
            "ClockIn": row["ClockIn"],
            "ClockOut": row["ClockOut"],
            "Description": row["Description"]
        }

        # Send the data to the server
        response = session.post(
            f"{ACTIVITY_ENRICHMENT_BASE_URL}/LogBook/StudentSave", data)
        if response.json()["json"]:
            print(f"Logbook for {row['Date']} success to insert or update")
        else:
            print(f"Logbook for {row['Date']} fail to insert or update")


def visit_logbook_tab():
    logbook_tab = driver.find_element(by=By.CLASS_NAME, value="logBookTab")
    logbook_tab.click()
    time.sleep(SLEEP_TIME)
    print(f'Current Page: {driver.title}')

    # Set selenium driver's cookies to requests module session's cookies
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    driver.quit()


def visit_activity_page():
    goto_activity_page = driver.find_element(
        By.XPATH, "//*[text()='Go to Activity Enrichment Apps']")
    goto_activity_page.click()
    time.sleep(SLEEP_TIME)
    print(f'Current Page: {driver.title}')

    loggedin_account_button = driver.find_element(
        By.CSS_SELECTOR,
        f"div.table[data-test-id='{EMAIL}']"
    )
    loggedin_account_button.click()
    time.sleep(SLEEP_TIME)
    print(f'Current Page: {driver.title}')


def login():
    email_input = driver.find_element(by=By.ID, value="i0116")
    email_input.send_keys(EMAIL)

    next_button = driver.find_element(by=By.ID, value="idSIButton9")
    next_button.click()
    time.sleep(SLEEP_TIME)
    print(f'Current Page: {driver.title} - Inputting email')

    password_input = driver.find_element(by=By.ID, value="i0118")
    password_input.send_keys(PASSWORD)

    next_button = driver.find_element(by=By.ID, value="idSIButton9")
    next_button.click()
    time.sleep(SLEEP_TIME)
    print(f'Current Page: {driver.title} - Inputting password')

    no_stay_login_button = driver.find_element(by=By.ID, value="idBtn_Back")
    no_stay_login_button.click()
    time.sleep(SLEEP_TIME)
    print(f'Current Page: {driver.title} - Disabling stay signed in')


def visit_login_page():
    driver.get(ENRINCHMENT_LOGIN_URL)
    time.sleep(SLEEP_TIME)
    print(f'Current Page: {driver.title}')

    login_button = driver.find_element(by=By.ID, value="btnLogin")
    login_button.click()
    time.sleep(SLEEP_TIME)
    print(f'Current Page: {driver.title}')


def main():
    visit_login_page()
    login()
    visit_activity_page()
    visit_logbook_tab()
    fill_logbook_activity()


if __name__ == '__main__':
    main()
