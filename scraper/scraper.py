from .login import login_bypass_captcha
from .filter import open_filter, select_difficulty, select_topic, close_filter
from .problems import get_num_problems, fetch_problem_list, click_ith_problem, check_premium_message 
from .problems import get_problem_params, get_problem_sol, go_back_to_problem_list
import logging
import time
import json
import os

class Scraper:
    def __init__(self):
        os.makedirs('out', exist_ok=True)

        class NewLineFormatter(logging.Formatter):
            def format(self, record):
                message = super().format(record)
                return message.replace("\n", "\n                                  ")

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('out/webscraper.log', mode='w')
        file_handler.setFormatter(NewLineFormatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

        self.logger = logger

    def set_sb(self, sb):
        self.sb = sb

    def login_bypass_captcha(self):
        login_bypass_captcha(self.sb, self.logger)

    def open_filter(self):
        return open_filter(self.sb, self.logger)
    
    def close_filter(self):
        close_filter(self.sb, self.logger)

    def select_difficulty(self, fields_wrapper):
        select_difficulty(self.sb, self.logger, self.difficulty, fields_wrapper)

    def select_topic(self, fields_wrapper):
        select_topic(self.sb, self.logger, self.topic, fields_wrapper)

    def get_num_problems(self) -> int:
        return get_num_problems(self.sb, self.logger, self.percent)
    
    def fetch_problem_list(self):
        return fetch_problem_list(self.sb, self.logger)
    
    def click_ith_problem(self, problem_list, i):
        return click_ith_problem(self.sb, self.logger, problem_list, i)
    
    def check_premium_message(self, message_type) -> bool:
        return check_premium_message(self.sb, self.logger, message_type)
    
    def get_problem_desc(self, data: dict):
        get_problem_params(self.sb, self.logger, data)
    
    def get_problem_sol(self, data: dict, problems_data: list, i: int):
        get_problem_sol(self.sb, self.logger, data, self.target_num_sols, self.lang, problems_data, i)

    def go_back_to_problem_list(self):
        go_back_to_problem_list(self.sb, self.logger)

    def intro_messages(self):
        print("\nLeetCode Solution Scraper\n\nThis will scrape for solutions based on difficulty, topic, and language\n")
        print("In all following prompts leave the input blank for the default values")
        print("Default values are:\n difficulty = easy\n topic = array\n lang = python\n percent of questions = 0.75\n target number of solutions per problem = 5\n")

        difficulty = input("Enter the difficulty level (easy, med., hard): ").strip().lower()
        if difficulty not in ["easy", "med.", "hard", ""]:
            print("Invalid difficulty level. Please enter 'easy', 'med.', or 'hard'.")
            exit(1)
        difficulty = difficulty if difficulty != "" else "easy"

        topic = input("Enter the topic (e.g. 'array', 'string'): ").strip().lower()
        topic = topic if topic != "" else "array"

        lang = input("Enter the programming language (e.g. 'python', 'c++'): ").strip().lower()
        if lang not in ["python", "c++", "java", ""]: # Current langauages supported from logic in script for solution identification
            print("Invalid programming language. Please enter 'python', 'c++', or 'java'.")
            exit(1)
        lang = lang if lang != "" else "python"

        percent = input("Enter the percentage of problems to scrape (0.25 for 25%, 0.5 for 50%, etc.): ").strip()
        percent = float(percent) if percent != "" else 0.75

        target_num_sols = input("Enter the target number of solutions per problem: ").strip()
        target_num_sols = int(target_num_sols) if target_num_sols != "" else 5

        print(f"\nStarting webscraper...\n difficulty: {difficulty}\n topic: {topic}\n language: {lang}\n percent: {percent}\n target number of solutions: {target_num_sols}\n")

        self.logger.info(f"Starting webscraper with difficulty: {difficulty}, topic: {topic}, lang: {lang}, percent: {percent}, target_num_sols: {target_num_sols}")
        self.difficulty = difficulty
        self.topic = topic
        self.lang = lang
        self.percent = percent
        self.target_num_sols = target_num_sols

    def write_data_to_file(self, problems_data: list):
        with open(f"out/{self.difficulty}_{self.topic}_{self.lang}_{self.percent}_{self.target_num_sols}_{int(time.time())}.jsonl", "w") as f:
            for problem in problems_data:
                f.write(json.dumps(problem) + "\n")
            self.logger.info(f"Saved problems to output_{self.difficulty}_{self.topic}.jsonl")