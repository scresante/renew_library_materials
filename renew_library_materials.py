#!/usr/bin/python3

from time import sleep
from sys import exit, argv
import re, datetime
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

MOST_DAYS_OUT = 3

url = 'http://lwpl.sirsi.net'

pd = Path("creds")
if (pd).is_file():
    with open(pd) as credfile:
        user, pin = credfile.readline().strip().split(' ')
else:
        user, pin = argv[1], argv[2]

    # user = input("Enter library card #: ")
    # pin = input("Enter PIN: ")


options = Options()
options.set_headless(headless=True)
browser = webdriver.Firefox(firefox_options = options)
browser.get(url)

# wait for item to appear, then click it
loginnow = WebDriverWait(browser, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, "login_button")));
# print("finished waiting")
uid = browser.find_element_by_id('user_id')
uid.send_keys(user)
password = browser.find_element_by_id('password')
password.send_keys(pin)
# loginnow = browser.find_element_by_class('login_button')
loginnow.click()

# print("sleeping")
sleep(5)
renew_link = browser.find_element_by_link_text('Renew My Materials')
renew_link.click()

due_dates = [ _.text for _ in browser.find_elements_by_xpath("//td[@align='left']")]
print("Previous due dates:")
print(*due_dates, sep='\n')

expire_soon = False

for date in due_dates:
    m = re.match('Due: (\d+)/(\d+)/(\d+),(\d+):(\d+)', date)
    if m:
        mo, day, yr, hr, mi = [int(_) for _ in m.groups()]
        due_on = datetime.datetime(yr, mo, day, hr, mi)
        now = datetime.datetime.now()
        if (due_on - now).days < MOST_DAYS_OUT:
            expire_soon = True
            print(f"Found a due date that is within {MOST_DAYS_OUT} days!: {m}")

if expire_soon == True:
    browser.find_element_by_id("renew_all").click()
    browser.find_element_by_xpath("//input[@value='Renew Selected Items']").click()
    sleep(5)
    due_dates = [ _.text for _ in browser.find_elements_by_xpath("//td[@align='left']")]
    print("New due dates:")
    print(*due_dates, sep='\n')
else:
    print(f"No items due within the {MOST_DAYS_OUT} day limit")

browser.close()
