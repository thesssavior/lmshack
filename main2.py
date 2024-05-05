def scraper(studentID, pw, tupleList, driver):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException

    import time

    # n hour m min l sec -> seconds
    def calculateRunningtime(text):
        runningtime = 0
        for i, char in enumerate(text):
            if char == "시":
                runningtime+=3600*int(text[:i])
            if char == "분":
                try:
                    runningtime+=60*int(text[i-2:i])
                except:
                    runningtime+=60*int(text[i-1:i])
            if char == "초":
                runningtime+=int(text[i-2:i])
        return(runningtime)

    def calculateElapsedTime(text):
        t = text[62:-1]
        elapsedTime = 0
        # 시간 까지 감
        if len(t) == 8:
            elapsedTime+=3600*int(t[:2])+60*int(t[3:5])+int(t[6:])
        # 분 까지만 있음
        else:
            elapsedTime+=60*int(t[:2])+int(t[3:])
        return(elapsedTime)

    # login (after receiving the inputs)
    print(tupleList)
    service = Service(executable_path=driver)
    driver = webdriver.Chrome(service=service)
    driver.get("https://learning.hanyang.ac.kr/")
    delay = 10
    wait = WebDriverWait(driver, delay)  # Wait up to 10 seconds
    uid = driver.find_element(By.ID, "uid")
    uid.send_keys(studentID)
    upw = driver.find_element(By.ID, "upw")
    upw.send_keys(pw)
    login_btn = driver.find_element(By.ID, "login_btn").click()
    
    for courseNo, weekNo in tupleList:

        # dashboard
        courses = WebDriverWait(driver, delay).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"ic-DashboardCard__link")))
        courses[courseNo].click()

        # weekly lessons
        weeklylessons = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME,"context_external_tool_140"))).click()
        iframe = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#tool_content")))
        driver.switch_to.frame(iframe)

        # empty divs do the job!!
        lessons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[not(@*)]")))
        lesson = lessons[weekNo]

        # target the player image to identify videos
        i_tags = lesson.find_elements(By.CSS_SELECTOR, "i.xnmb-module_item-icon.mp4, i.xnmb-module_item-icon.movie")

        # n주차에서 강의를 다 돌려줄 수는 있는데 일단 하나씩만
        if i_tags:
            i_tag = i_tags[0]
            parent_div = i_tag.find_element(By.XPATH, "./..")
            a_tag = parent_div.find_element(By.CSS_SELECTOR, ".xnmb-module_item-left-title.link").click()

        else:
            print("No <i> tags found")

        # nth week's lesson
        # receive lesson number input
        driver.switch_to.default_content()
        iframe0 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'iframe#tool_content.tool_launch')))
        iframe0 = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#tool_content.tool_launch")))
        driver.switch_to.frame(iframe0)
        iframe1 = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.xnlailvc-commons-frame")))
        driver.switch_to.frame(iframe1)
        playbtn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "vc-front-screen-play-btn"))).click()

        # only if i have watched it before
        try:
            # Attempt to find and click the button if it's clickable within 10 seconds
            resumemsg = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.confirm-msg-box > div.confirm-msg-text"))).get_attribute('innerText')
            elapsedTime = calculateElapsedTime(resumemsg)
            time.sleep(1)
            yesbtn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "confirm-ok-btn"))).click()
        except TimeoutException:
            print("first time watching")

        driver.switch_to.default_content()
        driver.switch_to.frame(iframe0)

        # extract the length of the video: maybe i should just use the time bar at the bottom of the vid
        runningtime = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.xnvchp-info-duration > span:not(.title)"))).text
        try: 
            t = calculateRunningtime(runningtime)-elapsedTime
            elapsedTime=0
        except:
            t = calculateRunningtime(runningtime)

        time.sleep(t)

        # after the lecture is done
        driver.execute_script("window.history.go(-3)")
        try:
            # Switch to the alert
            alert = driver.switch_to.alert
            # Print the text from the alert
            print(alert.text)
            # Accept the alert (click OK)
            alert.accept()
        except:
            # Handle cases where no alert was present, if necessary
            pass
        driver.switch_to.default_content()



