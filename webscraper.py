from seleniumbase import SB
from selenium.webdriver.common.by import By
import time

# difficulty = input("Enter the difficulty level (easy, medium, hard): ").strip().lower()
# if difficulty not in ["easy", "medium", "hard"]:
#     print("Invalid difficulty level. Please enter 'easy', 'medium', or 'hard'.")
#     exit(1)

# topic = input("Enter the topic (e.g., 'array', 'string'): ").strip().lower()
# if topic not in ["array", "string"]:
#     print("Invalid topic. Please enter a valid topic.")
#     exit(1)

difficulty = "easy"
topic = "array"

with SB(uc=True) as sb:
    # login and bypass captcha
    url = "https://leetcode.com/accounts/login/?next=%2Fproblemset%2F"
    sb.open(url)
    sb.uc_gui_click_captcha()

    # input username and password and submit
    sb.type("input[name='login']", "")  # Replace with your username
    sb.type("input[name='password']", "")  # Replace with your password
    sb.click("#signin_btn")

    # open filter
    sb.click("div[id='radix-:rl:']")

    # assert filter is visible
    sb.assert_element("div[data-radix-popper-content-wrapper]")

    # set difficulty for filter
    # sb.click("div[id='radix-:ri3:']")
    # sb.assert_element("div[class='max-h-[210px] overflow-auto rounded-[8px]']")

    parent = sb.find_element("div[class='max-h-[210px] overflow-auto rounded-[8px]']")
    print(parent)
    children = parent.find_elements("div[class='text-sd-muted-foreground text-xs w-[86px]'")
    print(children)

    for child in children:
        if child.text == "Difficulty":
            row = child.find_element(By.XPATH, "..")
            row.find_element("div[class='border-sd-input']").click()

    time.sleep(10)

    sb.click(f'text={difficulty}')

    time.sleep(5)
