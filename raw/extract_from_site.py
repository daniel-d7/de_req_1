### Credited to NguyenQuan2388 at https://github.com/NguyenQuan2388/Crawl_Data_TopDev/
### I made some modifications on my own to adapt to the new TopDev site html code and data needed

from datetime import datetime
from json import load
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from dotenv import load_dotenv
import os
import pandas as pd
import random
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver import ActionChains


def extract_from_site():
    load_dotenv()
    # credentials
    password = os.getenv("GIT_PASSWORD")
    username = os.getenv("GIT_USERNAME")

    # init ChromeDriver with options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    driver_service = Service(executable_path='./chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)

    # Navigate to TopDev login page
    driver.get('https://accounts.topdev.vn/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="btnLoginGithub"]')))

    # Click on GitHub login button
    try:
        github_login_button = driver.find_element(By.XPATH, '//*[@id="btnLoginGithub"]')
        github_login_button.click()
    except Exception as e:
        print("Error clicking GitHub login button:", e)
        driver.quit()

    # GitHub login process
    try:
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="login_field"]'))
        )
        username_input.send_keys(username)

        password_input = driver.find_element(By.XPATH, '//*[@id="password"]')
        password_input.send_keys(password)

        login_button = driver.find_element(By.XPATH, '//*[@id="login"]/div[3]/form/div/input[13]')
        login_button.click()
    except Exception as e:
        print("Error during GitHub login:", e)
        driver.quit()

    # Wait for login to complete
    WebDriverWait(driver, 10).until(EC.url_changes('https://accounts.topdev.vn/'))

    # Navigate to job listing page
    driver.get('https://topdev.vn/viec-lam-it')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="frontend-v4"]')))

    # Handle pop-up closing
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Close"]'))
        )
        close_button.click()
    except Exception as e:
        print("No pop-up found or error closing pop-up:", e)

    # Get total jobs
    try:
        total = int(driver.find_element(By.XPATH, '//*[@id="frontend-v4"]/main/div[2]/div/div/div[1]/section/h1/span').text)
        print("Total jobs:", total)
    except Exception as e:
        print("Error getting total jobs:", e)
        driver.quit()

    # Scroll to load all jobs
    retry_count = 0
    def scroll_to_load_all_jobs():
        max_retry = 3
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            iframe = driver.find_element(By.TAG_NAME, "mb-4 inline-block max-w-[152px]")
            ActionChains(driver)\
                .scroll_to_element(iframe)\
                .perform()
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                if retry_count < max_retry:
                    retry_count += 1
                    print(f'Limit reached, retrying in 5 sec, total retry = {retry_count}')
                    sleep(5)
                    True
                else:
                    break
            last_height = new_height

    scroll_to_load_all_jobs()

    # Store data
    url_jobs = []
    jobs_data = []

    # Get list of job URLs
    for i in range(1, total + 1):
        try:
            urls_path = f'//*[@id="frontend-v4"]/main/div[2]/div/div/div[1]/section/ul/li[{i}]/a/div/div/div[2]/h3/a' if i <= 11 else f'//*[@id="frontend-v4"]/main/div[2]/div/div/div[1]/section/ul/div/ul/li[{i}]/a/div/div/div[2]/h3/a'
            element = driver.find_element(By.XPATH, urls_path)
            url = element.get_attribute('href')
            url_jobs.append(url)
        except Exception as e:
            print(f"Error getting URL for job {i}")
            continue

    # Get data from each job
    for url in url_jobs:
        driver.get(url)
        sleep(2)  # Salary element
        try:
            #-----------------Salary-----------------#
            salary = driver.find_element(By.XPATH, '//*[@id="detailJobPage"]/div/section/section[2]/section/div/div/div[1]/p').text
        except Exception as e:
            salary = ""

        try:    
            #-----------------Location-----------------#
            location = driver.find_element(By.XPATH, '//*[@id="detailJobPage"]/div/section/section/div[2]/div/div/span/div/span').text
            location = location.replace(",", ": ")
        except Exception as e:
            location = ""

        try:    
            #-----------------Company Name-----------------#
            company_name = driver.find_element(By.XPATH, '//*[@id="detailJobPage"]/div/section/section/div[2]/p').text
        except Exception as e:
            company_name = ""
            
        try:    
            #-----------------Time Remain-----------------#
            time_remain = driver.find_element(By.XPATH, '//*[@id="detailJobPage"]/div/section/section[2]/section/div/div/div[2]/div/div/span')
            time_remain = time_remain.text.strip()
        except Exception as e:
            time_remain = ""
            
        try:    
            #-----------------Job Type-----------------#
            job_type = driver.find_element(By.XPATH, '//*[@id="detailJobPage"]/div/section/section/div[2]/h1').text
        except Exception as e:
            job_type = ""

        try:
            #-----------------Date Crawling------------------#
            time = datetime.now().strftime("%Y-%m-%d")
        except Exception as e:
            time = ""
        
        jobs_data.append([time, job_type, company_name, salary, location, time_remain, url])

    # Close the driver
    driver.quit()
    # Convert list to DataFrame
    jobs_df = pd.DataFrame(jobs_data)
    # Write data to dataframe
    data = pd.DataFrame(columns=["time", "job_type", "company_name", "salary", "location", "time_remain", "url"])
    data = pd.concat([data, jobs_df], ignore_index=True)
    
    return data