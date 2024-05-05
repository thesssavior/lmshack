def set_first(studentID, pw, driver):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # extract only the useful part of the course titles
    def extract_title(element):
        temp = list(element)
        for i, char in enumerate(temp):
            if char == "_":
                extracted = "".join(temp[i+1:])
                break
        return extracted

    # Set Chrome options to run in headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration

    # Initialize the Chrome driver
    driver = webdriver.Chrome(executable_path=driver, options=chrome_options)
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
    driver.get("https://learning.hanyang.ac.kr/")
    uid = driver.find_element(By.ID, "uid")
    uid.send_keys(studentID)
    upw = driver.find_element(By.ID, "upw")
    upw.send_keys(pw)
    login_btn = driver.find_element(By.ID, "login_btn").click()
    courses = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,".ic-DashboardCard__header-subtitle.ellipsis"))) 
    courses_list = [extract_title(element.text) for element in courses]

    return courses_list
