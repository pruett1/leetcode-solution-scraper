from seleniumbase import SB
from selenium.webdriver.common.by import By
import time
import logging
from data import login
import json

class NewLineFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        return message.replace("\n", "\n                                  ")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('webscraper.log', mode='w')
file_handler.setFormatter(NewLineFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# difficulty = input("Enter the difficulty level (easy, med., hard): ").strip().lower()
# if difficulty not in ["easy", "med.", "hard"]:
#     print("Invalid difficulty level. Please enter 'easy', 'med.', or 'hard'.")
#     exit(1)

# topic = input("Enter the topic (e.g., 'array', 'string'): ").strip().lower()

# lang = input("Enter the programming language (e.g., 'python3'): ").strip().lower()

difficulty = "easy"
topic = "greedy"
lang = "python3"

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
    problem_list_len = len(problem_list.find_elements(By.XPATH, "./*"))

    problems_data = []

    # for i in range(2, problem_list_len + 1): # the first problem is always the daily problem which may not be the right difficulty/topic
    for i in range(2, 3):
        # Because changing the page, need to re-fetch the problem list each time
        sb.wait_for_element("svg[data-icon='filter']") # wait for page to load
        problem_list = sb.get_element("svg[data-icon='filter']")
        for _ in range(7):
            problem_list = problem_list.find_element(By.XPATH, "..")
        problem_list = problem_list.find_elements(By.XPATH, "./*")[1].find_element(By.XPATH, "./*")

        # Get the i-th problem (1 indexed)
        logger.debug(f"len of problem_list children: {len(problem_list.find_elements(By.XPATH, './*'))}, fetching problem {i}")
        while i > len(problem_list.find_elements(By.XPATH, "./*")):
            logger.warning(f"Problem {i} does not exist")
            sb.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.info("Scrolled to bottom of page, waiting for more problems to load...")
            time.sleep(1) # wait for problems to load

            problem_list = sb.get_element("svg[data-icon='filter']")
            for _ in range(7):
                problem_list = problem_list.find_element(By.XPATH, "..")
            problem_list = problem_list.find_elements(By.XPATH, "./*")[1].find_element(By.XPATH, "./*")

            logger.debug(f"len of problem_list children after scroll: {len(problem_list.find_elements(By.XPATH, './*'))}")

        problem = problem_list.find_element(By.XPATH, f"./*[{i}]")
        assert problem.get_attribute("tagName").lower() == "a", "Expected problem to be an a tag"
        problem.click()
        logger.info(f"Clicked on problem: {sb.get_current_url()}")

        # Check if premium-only message exists
        premium_message = "Thanks for using LeetCode! To view this question you must subscribe to premium."
        premium_divs = sb.find_elements(By.XPATH, f".//div[contains(text(), '{premium_message}')]")
        if premium_divs:
            logger.warning("Premium-only problem detected, skipping...")
            sb.driver.back()
            continue

        # wait for the problem description to load
        sb.wait_for_element("div[data-track-load='description_content']")
        desc = sb.get_element("div[data-track-load='description_content']")

        # set up data structure to hold problem data
        data = {"desc": "",
                "examples": [],
                "constraints": [],
                "solution": ""}

        # get problem description data
        data_ind = "desc" # set initial data index
        text = ""
        for elem in desc.find_elements(By.XPATH, "./*"):
            logger.debug(f"Current data_ind: {data_ind}, text: {text}")
            logger.debug(f"Processing element: {elem.text.strip()}")
            if "example" in elem.text.strip().lower()[:7] and data_ind != "examples":
                logger.info(f"Found example section, switching data index to 'examples' from '{data_ind}'")
                data[data_ind] = text.strip()
                text = ""
                data_ind = "examples"
            elif data_ind == "examples" and "example" in elem.text.strip().lower()[:7]:
                logger.info("Continuing to collect examples")
                data[data_ind].append(text.strip()[11:]) # remove "Example N:\n" prefix
                text = ""
            elif "constraints" in elem.text.strip().lower()[:11] and data_ind != "constraints":
                logger.info(f"Found constraints section, switching data index to 'constraints' from '{data_ind}'")
                data[data_ind].append(text.strip()[11:]) # remove "Example N:\n" prefix
                text = ""
                data_ind = "constraints"

            text += elem.text.strip() + "\n"
        
        text = text.strip()[13:] # remove "Constraints:\n" prefix
        data[data_ind] = text.split("\n") if data_ind == "constraints" else text # split constraints into list

        # get solution
        logger.info("Finished collecting problem description, now collecting solution...")
        data_ind = "solution"
        sb.get_element("div[id='solutions_tab']").click()

        solution_wrapper = sb.get_element("div.relative.h-full.overflow-auto.transition-opacity")
        solution_wrapper = solution_wrapper.find_elements(By.XPATH, "./*")[2]
        solution_wrapper = solution_wrapper.find_elements(By.XPATH, "./*")[0]
        # logger.debug(f"<{solution_wrapper.tag_name} {solution_wrapper.get_attribute('outerHTML').split('>')[0][len(solution_wrapper.tag_name)+1:]}>")
        solutions_len = len(solution_wrapper.find_elements(By.XPATH, "./*"))

        for j in range(1, min(4, solutions_len)+1):
            # when go back from solution, the language filter sometimes resets so need to select language every time
            sb.wait_for_element(By.XPATH, "//span[contains(text(), 'All')]")
            all_langs = sb.find_elements(By.XPATH, "//span[contains(text(), 'All')]")
            logger.debug(f"Found {len(all_langs)} 'All' language selectors")
            
            assert all_langs, "No all language selector found"
            # Get the next sibling element after 'All' (the language selector)
            lang_wrapper = all_langs[0].find_element(By.XPATH, "..").find_elements(By.XPATH, "./*")[2]

            for language in lang_wrapper.find_elements(By.XPATH, "./*"):
                logger.debug(f"Checking language: {language.text.lower()}")
                if language.text.lower() == lang:
                    logger.info(f"Selecting language: {language.text}")
                    if language.get_attribute("style") == "order: -1;":
                        logger.debug("Language is already selected, skipping click")
                        break
                    language.click()
                    break

            solution_wrapper = sb.get_element("div.relative.h-full.overflow-auto.transition-opacity")
            solution_wrapper = solution_wrapper.find_elements(By.XPATH, "./*")[2]
            solution_wrapper = solution_wrapper.find_elements(By.XPATH, "./*")[0]

            time.sleep(2) # wait for solution to load
            solution = solution_wrapper.find_element(By.XPATH, f"./*[{j}]")
            logger.debug(f"<{solution.tag_name} {solution.get_attribute('outerHTML').split('>')[0][len(solution.tag_name)+1:]}>")
            solution.click()
            logger.info(f"Clicked on solution {j} in {lang}")
            sb.find_element(By.XPATH, "//div[contains(text(), 'All Solutions')]").click() # click on "All Solutions" to go back to the list of solutions
            time.sleep(5)
        
        problems_data.append(data)   

        logger.debug(f"Data collected for problem {i}")
        for key, value in data.items():
            logger.debug(f"{key}: {value}")
        # Go back to the problem list
        sb.driver.back()
        logger.info("Navigated back to problem list")
        time.sleep(3) # give time for the page to load

    with open(f"output_{difficulty}_{topic}.json", "w") as f:
        json.dump(problems_data, f, indent=4)
        logger.info(f"Saved problems to output_{difficulty}_{topic}.json")