from seleniumbase import SB
from selenium.webdriver.common.by import By
import time
import logging
from data import login

# difficulty = input("Enter the difficulty level (easy, med., hard): ").strip().lower()
# if difficulty not in ["easy", "med.", "hard"]:
#     print("Invalid difficulty level. Please enter 'easy', 'med.', or 'hard'.")
#     exit(1)

# topic = input("Enter the topic (e.g., 'array', 'string'): ").strip().lower()
# if topic not in ["array", "string"]:
#     print("Invalid topic. Please enter a valid topic.")
#     exit(1)

logging.basicConfig(filename='webscraper.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

difficulty = "easy"
topic = "greedy"

logger.info(f"Starting webscraper with difficulty: {difficulty}, topic: {topic}")

with SB(uc=True) as sb:
    # login and bypass captcha
    url = "https://leetcode.com/accounts/login/?next=%2Fproblemset%2F"
    sb.open(url)
    sb.uc_gui_click_captcha()

    # input username and password and submit
    sb.type("input[name='login']", login['user'])
    sb.type("input[name='password']", login['pwd'])
    sb.click("#signin_btn")
    logger.info("Logged in. Waiting for page to load...")

    # wait for filter to appear
    sb.wait_for_element("svg[data-icon='filter']")
    logger.info("Page loaded. Opening filter...")

    # open filter
    sb.click("svg[data-icon='filter']")

    # assert filter is visible
    sb.assert_element("div[data-radix-popper-content-wrapper]")

    # open filter fields
    popup = sb.find_element("div[data-radix-popper-content-wrapper]")
    fields_wrapper = popup
    for _ in range(4):
        fields_wrapper = fields_wrapper.find_element(By.XPATH, "./*")

    logger.info("Filter opened. Selecting difficulty and topic...")
 
    #select difficulty
    for field in fields_wrapper.find_elements(By.XPATH, "./*"):
        children = field.find_elements(By.XPATH, "./*")
        #check if the field is the difficulty field
        if len(children) >= 2 and "difficulty" in children[1].text.lower():
            logger.info("Found difficulty field, selecting difficulty...")
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
                logger.debug(f"Checking option: {label.text.lower()}")
                if difficulty in label.text.lower():
                    logger.info(f"Selecting difficulty: {difficulty}")
                    option.click()
                    break

    # select topic
    for field in fields_wrapper.find_elements(By.XPATH, "./*"):
        children = field.find_elements(By.XPATH, "./*")
        #check if the field is the topic field
        if len(children) >= 2 and "topics" in children[1].text.lower():
            logger.info("Found topic field, selecting topic...")
            selectors = children[2].find_elements(By.XPATH, "./*")
            assert len(selectors) == 2, "Expected two selectors"

            selectors[1].find_elements(By.XPATH, "./*")[1].click() # click the second child (open arrow) throws error otherwise not sure why
            assert selectors[1].get_attribute("data-state") == "open", "Selector did not open"

            topic_menu_id = selectors[1].get_attribute("aria-controls")

            topic_menu = sb.find_element(f"div[id='{topic_menu_id}']")

            topics_wrapper = topic_menu.find_element(By.XPATH, "./*").find_element(By.XPATH, "./*").find_elements(By.XPATH, "./*")
            assert len(topics_wrapper) == 2, "Expected search and list of topics"
            logger.info("Waiting 3 seconds for topics to load...")
            time.sleep(3) # wait for topics to load

            topics_wrapper = topics_wrapper[1].find_element(By.XPATH, "./*")
            logger.debug(f"Topics wrapper children len = {len(topics_wrapper.find_elements(By.XPATH, './*'))}")
        
            for option in topics_wrapper.find_elements(By.XPATH, "./*"):
                logger.debug(f"Checking option: {option.text.lower()} against topic: {topic}")
                if topic in option.text.lower():
                    logger.info(f"Selecting topic: {topic}")
                    option.click()
                    break
    
    #close filter
    logger.info("Closing filter...")
    sb.click("svg[data-icon='filter']")
    # time.sleep(5)

    problem_list = sb.get_element("svg[data-icon='filter']")
    for _ in range(7):
        problem_list = problem_list.find_element(By.XPATH, "..")

    assert len(problem_list.find_elements(By.XPATH, "./*")) == 2, "Expected two children at this level"

    problem_list = problem_list.find_elements(By.XPATH, "./*")[1].find_element(By.XPATH, "./*")
    logger.info(f"problem_list children len = {len(problem_list.find_elements(By.XPATH, './*'))}")
    problem_list_class = problem_list.get_attribute("class").replace(" ", ".")
    problem_list_len = len(problem_list.find_elements(By.XPATH, "./*"))

    for i in range(1, problem_list_len+1):
        # Because changing the page, need to re-fetch the problem list each time
        problem_list = sb.get_element("svg[data-icon='filter']")
        for _ in range(7):
            problem_list = problem_list.find_element(By.XPATH, "..")
        problem_list = problem_list.find_elements(By.XPATH, "./*")[1].find_element(By.XPATH, "./*")

        # Get the i-th problem (1 indexed)
        problem = problem_list.find_element(By.XPATH, f"./*[{i}]")
        assert problem.get_attribute("tagName").lower() == "a", "Expected problem to be an a tag"
        problem.click()
        logger.info(f"Clicked on problem: {sb.get_current_url()}")

        time.sleep(5)

        # Go back to the problem list
        sb.driver.back()
        logger.info("Navigated back to problem list")
        time.sleep(3)

