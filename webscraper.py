from seleniumbase import SB
from selenium.webdriver.common.by import By
from scraper.scraper import Scraper
import time

def main():
    scraper = Scraper()
    scraper.intro_messages()

    with SB(uc=True) as sb:
        scraper.set_sb(sb)
        scraper.login_bypass_captcha()

        # Open filter and set difficulty and topic
        fields_wrapper = scraper.open_filter()
        scraper.select_difficulty(fields_wrapper)
        scraper.select_topic(fields_wrapper)
        scraper.close_filter()

        problems_num = scraper.get_num_problems()
        problems_data = []
        try:
            for i in range(2, problems_num): # the first problem is always the daily problem which may not be the right difficulty/topic
                problem_list = scraper.fetch_problem_list() # Need to refetch problem list bc stale elements after navigating back

                scraper.click_ith_problem(problem_list, i)

                if scraper.check_premium_message("problem"): continue

                # set up data structure to hold problem data
                data = {"desc": "",
                        "examples": [],
                        "constraints": [],
                        "solution": ""}

                scraper.get_problem_desc(data) # modifies data in place
                scraper.get_problem_sol(data, problems_data, i) # modifies in place and appends to problems_data per solution found

                scraper.go_back_to_problem_list()
        finally:
            scraper.write_data_to_file(problems_data)

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"\nTotal time: {((end_time - start_time)/60):.2f} minutes")