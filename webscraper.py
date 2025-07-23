from seleniumbase import SB
from selenium.webdriver.common.by import By
import time
from data import login

# difficulty = input("Enter the difficulty level (Easy, Med., Hard): ").strip().lower()
# if difficulty not in ["Easy", "Med.", "Hard"]:
#     print("Invalid difficulty level. Please enter 'East', 'Med.', or 'Hard'.")
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
    sb.type("input[name='login']", login['user'])
    sb.type("input[name='password']", login['pwd'])
    sb.click("#signin_btn")

    # open filter
    sb.click("svg[data-icon='filter']")

    # assert filter is visible
    sb.assert_element("div[data-radix-popper-content-wrapper]")

    # open filter fields
    popup = sb.find_element("div[data-radix-popper-content-wrapper]")
    fields_wrapper = popup
    for _ in range(4):
        fields_wrapper = fields_wrapper.find_element(By.XPATH, "./*")
 
    #select difficulty
    for field in fields_wrapper.find_elements(By.XPATH, "./*"):
        children = field.find_elements(By.XPATH, "./*")
        #check if the field is the difficulty field
        if len(children) >= 2 and "Difficulty" in children[1].text.lower():
            selectors = children[2].find_elements(By.XPATH, "./*")
            assert len(selectors) == 2, "Expected two selectors"

            selectors[1].click()
            assert selectors[1].get_attribute("data-state") == "open", "Selector did not open"

            diff_menu_id = selectors[1].get_attribute("aria-controls")

            diff_menu = sb.find_element(f"div[id='{diff_menu_id}']")

            list_cntr = diff_menu.find_element(By.XPATH, "./*")
            assert len(list_cntr.find_elements(By.XPATH, "./*")) == 3, "Expected three difficulty options"

            for option in list_cntr.find_elements(By.XPATH, "./*"):
                label = option.find_element(By.XPATH, "./*")
                if difficulty in label.text.lower():
                    option.click()
                    break

    # select topic
    for field in fields_wrapper.find_elements(By.XPATH, "./*"):
        children = field.find_elements(By.XPATH, "./*")
        #check if the field is the topic field
        if len(children) >= 2 and "Topics" in children[1].text.lower():
            selectors = children[2].find_elements(By.XPATH, "./*")
            assert len(selectors) == 2, "Expected two selectors"

            selectors[1].click()
            assert selectors[1].get_attribute("data-state") == "open", "Selector did not open"

            topic_menu_id = selectors[1].get_attribute("aria-controls")

            topic_menu = sb.find_element(f"div[id='{topic_menu_id}']")

            topics_wrapper = topic_menu.find_element(By.XPATH, "./*").find_element(By.XPATH, "./*").find_elements(By.XPATH, "./*")
            assert len(topics_wrapper) > 2, "Expected search and list of topics"

            topics_wrapper = topics_wrapper[1].find_element(By.XPATH, "./*")
            

            for option in topics_wrapper.find_elements(By.XPATH, "./*"):
                label = option.find_element(By.XPATH, "./*")
                if difficulty in label.text.lower():
                    option.click()
                    break
    time.sleep(5)
    #close filter
    sb.click("svg[data-icon='filter']")