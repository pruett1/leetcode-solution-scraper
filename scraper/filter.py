from seleniumbase import SB
from selenium.webdriver.common.by import By
import logging
import time

def open_filter(sb: SB, logger):
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
    return fields_wrapper

def select_difficulty(sb: SB, logger, difficulty: str, fields_wrapper) -> None:
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

def select_topic(sb: SB, logger, topic: str, fields_wrapper) -> None:
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

def close_filter(sb: SB, logger) -> None:
    logger.info("Closing filter...")
    sb.click("svg[data-icon='filter']")
    time.sleep(3) # wait for filter to take effect