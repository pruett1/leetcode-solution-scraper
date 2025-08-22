from seleniumbase import SB
from selenium.webdriver.common.by import By
import time
from math import floor

def get_num_problems(sb: SB, logger, percent) -> int:
    problem_list = sb.get_element("svg[data-icon='filter']")
    for _ in range(7):
        problem_list = problem_list.find_element(By.XPATH, "..")

    assert len(problem_list.find_elements(By.XPATH, "./*")) == 2, "Expected two children at this level"

    problem_list = problem_list.find_elements(By.XPATH, "./*")[1].find_element(By.XPATH, "./*")
    logger.info(f"problem_list children len = {len(problem_list.find_elements(By.XPATH, './*'))}")
    problem_list_len = len(problem_list.find_elements(By.XPATH, "./*"))
    problems_num = floor(problem_list_len*percent) + 1 # +1 because 1 indexed
    return problems_num

def fetch_problem_list(sb: SB, logger):
    sb.wait_for_element("svg[data-icon='filter']") # wait for page to load
    problem_list = sb.get_element("svg[data-icon='filter']")
    for _ in range(7):
        problem_list = problem_list.find_element(By.XPATH, "..")
    problem_list = problem_list.find_elements(By.XPATH, "./*")[1].find_element(By.XPATH, "./*")
    return problem_list

def click_ith_problem(sb: SB, logger, problem_list, i):
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

def check_premium_message(sb: SB, logger, message_type) -> bool:
    premium_message = ""
    if message_type == "problem":
        premium_message = "Thanks for using LeetCode! To view this question you must subscribe to premium."
    elif message_type == "solution":
        premium_message = "Thanks for using LeetCode! To view this solution you must subscribe to premium."
    premium_divs = sb.find_elements(By.XPATH, f".//div[contains(text(), '{premium_message}')]")
    if premium_divs:
        logger.warning("Premium-only problem detected, skipping...")
        sb.driver.back()
        return True
    return False

def get_problem_params(sb: SB, logger, data: dict):
    # wait for the problem description to load
    sb.wait_for_element("div[data-track-load='description_content']")
    desc = sb.get_element("div[data-track-load='description_content']")

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

def get_sol_wrapper(sb: SB):
    solution_wrapper = sb.get_element("div.relative.h-full.overflow-auto.transition-opacity")
    solution_wrapper = solution_wrapper.find_elements(By.XPATH, "./*")[2]
    solution_wrapper = solution_wrapper.find_elements(By.XPATH, "./*")[0]
    return solution_wrapper

def set_sol_lang(sb: SB, logger, lang: str):
    sb.wait_for_element(By.XPATH, "//span[contains(text(), 'All')]")
    all_langs = sb.find_elements(By.XPATH, "//span[contains(text(), 'All')]")
    logger.debug(f"Found {len(all_langs)} 'All' language selectors")
    
    assert all_langs, "No all language selector found"
    # Get the next sibling element after 'All' (the language selector)
    lang_wrapper = all_langs[0].find_element(By.XPATH, "..").find_elements(By.XPATH, "./*")[2]

    for language in lang_wrapper.find_elements(By.XPATH, "./*"):
        logger.debug(f"Checking language: {language.text.lower()}")
        if lang in language.text.lower():
            if language.get_attribute("style") == "order: -1;":
                logger.debug("Language is already selected, skipping selection")
                break
            logger.info(f"Selecting language: {language.text}")
            language.click()
            break

def get_problem_sol(sb: SB, logger, data: dict, target_num_sols: int, lang:str, problems_data: list, i: int):
    logger.info("Finished collecting problem description, now collecting solution...")
    data_ind = "solution"
    sb.get_element("div[id='solutions_tab']").click()

    solutions_len = len(get_sol_wrapper(sb).find_elements(By.XPATH, "./*"))

    for j in range(1, min(target_num_sols, solutions_len)+1):
        set_sol_lang(sb, logger, lang)

        solution_wrapper = get_sol_wrapper(sb)

        time.sleep(2) # wait for solution to load
        solution = solution_wrapper.find_element(By.XPATH, f"./*[{j}]")
        if "group/ads" in solution.get_attribute("class"):
            logger.warning(f"Detected solution {j} is an ad, skipping...")
            continue
        
        solution.click()
        logger.info(f"Clicked on solution {j} in {lang}")

        time.sleep(3)

        check_premium_message(sb, logger, "solution")

        solution_found = False
        sol_count = 1
        while not solution_found:
            code_elements = [c for c in sb.find_elements(By.TAG_NAME, "code") if "language-" in c.get_attribute("class")]
            ans = code_elements[-1*sol_count] if code_elements else None  # get the last code element with "language-" in its class
            
            if ans and lang in ans.get_attribute("class").lower():
                lines = []
                for line_span in ans.find_elements(By.XPATH, "./span"):
                    words = [w.text for w in line_span.find_elements(By.XPATH, "./span")]
                    line = "".join(words)
                    lines.append(line)
                data[data_ind] = "\n".join(lines) + "\n"

                if "class solution" in data[data_ind].lower():
                    solution_found = True
                    logger.info(f"Collected solution in {lang}")
                    logger.debug(f"Solution text: {ans.text.strip()}")
                else:
                    sol_count += 1
                    logger.warning(f"Code[-{sol_count}] in {lang} does not contain 'class solution', checking next code element")
                    if sol_count > len(code_elements):
                        logger.error(f"Could not find solution in {lang} after checking all code elements")
                        data[data_ind] += "Solution not found\n"
                        break  # break out of while loop to go to next solution
                    continue  # continue to check next code element
            else:
                code_block_wrapper = ans.find_element(By.XPATH, "./../../../..")
                lang_selector = code_block_wrapper.find_elements(By.XPATH, "./*")[0]
                lang_selector = lang_selector.find_elements(By.XPATH, "./*")

                for selector in lang_selector:
                    logger.debug(f"Checking language selector: {selector.text.lower()}")
                    if lang in selector.text.lower():
                        lang_selector = selector
                        break

                if not lang_selector or type(lang_selector) is list:
                    logger.error(f"lang selector not found for {lang}, trying another code element")
                    solution_found = False
                    sol_count += 1
                    if sol_count > len(code_elements):
                        logger.error(f"Could not find solution in {lang} after checking all code elements")
                        data[data_ind] += "Solution not found\n"
                        break
                    continue  # continue to check next code element

                sb.driver.execute_script("arguments[0].scrollIntoView(true);", lang_selector)
                sb.driver.execute_script("arguments[0].click();", lang_selector)  # force click via JS to avoid interception
                time.sleep(2)
                code_elements = [c for c in sb.find_elements(By.TAG_NAME, "code") if "language-" in c.get_attribute("class")]
                ans = code_elements[-1] if code_elements else None  # get the last code element with "language-" in its class
                if ans and lang in ans.get_attribute("class"):
                    # Extract each line by iterating over top-level spans
                    lines = []
                    for line_span in ans.find_elements(By.XPATH, "./span"):
                        words = [w.text for w in line_span.find_elements(By.XPATH, "./span")]
                        line = "".join(words)
                        lines.append(line)
                    data[data_ind] = "\n".join(lines) + "\n"

                    if "class solution" in data[data_ind].lower():
                        solution_found = True
                        logger.info(f"Collected solution in {lang}")
                        logger.debug(f"Solution text: {ans.text.strip()}")
                    else:
                        sol_count += 1
                        logger.warning(f"Code[-{sol_count}] in {lang} does not contain 'class solution', checking next code element")
                        if sol_count > len(code_elements):
                            logger.error(f"Could not find solution in {lang} after checking all code elements")
                            data[data_ind] += "Solution not found\n"
                            break
                        continue  # continue to check next code element
                else:
                    logger.error(f"Could not find solution in {lang} after re-selecting language")
                    data[data_ind] += "Solution not found\n"
                    break

        if data[data_ind] != "Solution not found\n":
            problems_data.append(data.copy())
        logger.debug(f"Data collected for problem {i}, solution {j} for {lang}")
        for key, value in data.items():
            logger.debug(f"{key}: {value}")
        sb.find_element(By.XPATH, "//div[contains(text(), 'All Solutions')]").click() # click on "All Solutions" to go back to the list of solutions

def go_back_to_problem_list(sb: SB, logger):
    sb.driver.back()
    logger.info("Navigated back to problem list")
    time.sleep(3) # give time for the page to load