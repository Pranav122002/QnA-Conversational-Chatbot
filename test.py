from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(chrome_options)
driver.maximize_window()

driver.get("http://localhost:3000/")

icon = driver.find_element(By.CSS_SELECTOR, ".floating-icon")
icon.click()

questions = [
    "What is admission enquiry number ?",
    "What is address ?",
    "What is Fr. CRIT ?",
    "How many students are placed in TCS in year 2020?",
]
n = 3
while n>0:
    n = n-1
    for q in questions:
        inputbar = driver.find_element(By.CLASS_NAME, "bar")
        submitbtn = driver.find_element(By.CLASS_NAME, "submitbtn")

        WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element_value((By.CLASS_NAME, "bar"), ""))

        # inputbar.clear()  
        inputbar.send_keys(q)
        submitbtn.click()

        initial_qat_count = len(driver.find_elements(By.CSS_SELECTOR, ".qatcontainer .qat"))

        while True:
            try:
                WebDriverWait(driver, 10).until(
                    lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".qatcontainer .qat")) > initial_qat_count
                )
                break 
            except TimeoutException:
                print("New question element is not added within the specified time.")

# driver.quit()
