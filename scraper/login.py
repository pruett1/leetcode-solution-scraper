from seleniumbase import SB
from selenium.webdriver.common.by import By
import logging
from data import login

def login_bypass_captcha(sb: SB, logger) -> None:
    # login and bypass captcha
    url = "https://leetcode.com/accounts/login/?next=%2Fproblemset%2F"
    sb.open(url)
    sb.uc_gui_click_captcha()

    # input username and password and submit
    sb.type("input[name='login']", login['user'])
    sb.type("input[name='password']", login['pwd'])
    sb.click("#signin_btn")
    logger.info("Logged in. Waiting for page to load...")