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

# input: 01:06 부터? / 21:22 부터? / 1:12:00 부터?
# You were watching this content before. Continue watching from 22:41?
def calculateElapsedTime(text):
    t = text[62:-1]
    elapsedTime = 0
    for i, char in enumerate(t):
        # 시간 까지 감
        if char == ":" and i == 1:
            elapsedTime+=3600*int(t[:i])
        # 분에서 끝남
        if char == ":" and (i == 2 or i == 4):
            elapsedTime+=60*int(t[i-2:i])
            elapsedTime+=int(t[i+1:])
    return(elapsedTime)

# for the logic class
def weekNoToLectureForLogic(weekNo):
    lectureNo = 8 + 3*(weekNo-1)
    return lectureNo

# receive inputs for: classes, order, (id, pw later maybe)
# coursesList = input("courses numbers seperated by space: ")
# coursesDictList = [{"courseNo": 0, "weekNo": 2}, {"courseNo": 2, "weekNo": 2}]

tupleList = [(1,8)]
# for courseNo, weekNo in tupleList.
# weekNo = actual week number - 1

# Split the input string into a list of strings, then convert each to an integer
# courseNos = [int(num) for num in coursesList.split()]

# for the course numbers, iterate

# login (after receiving the inputs)
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
driver.get("https://learning.hanyang.ac.kr/")
delay = 10
uid = driver.find_element(By.ID, "uid")
uid.send_keys("2024086344")
upw = driver.find_element(By.ID, "upw")
upw.send_keys("Tmdwn1290!")
login_btn = driver.find_element(By.ID, "login_btn").click()

for courseNo, weekNo in tupleList:

    print(courseNo, weekNo)

    # dashboard
    courses = WebDriverWait(driver, delay).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"ic-DashboardCard__link")))
    courses[courseNo].click()

    # weekly lessons
    weeklylessons = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME,"context_external_tool_140"))).click()
    iframe = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#tool_content")))
    driver.switch_to.frame(iframe)

    # logic lectures navigate wrong
    # lessons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "p.xnmb-module-title > a.xnmb-module_item-left-title.link")))

    lessons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[not(@*)]")))
    print(len(lessons))
    lesson = lessons[weekNo]
    i_tags = lesson.find_elements(By.CSS_SELECTOR, "i.xnmb-module_item-icon.mp4")

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
        # visibility instead of presence!! couldn't get inner text before cuz element was located when it was empty...
        resumemsg = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.confirm-msg-box > div.confirm-msg-text"))).get_attribute('innerText')
        elapsedTime = calculateElapsedTime(resumemsg)
        time.sleep(1)
        yesbtn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "confirm-ok-btn"))).click()

    except TimeoutException:
        # If the button is not found or not clickable within 10 seconds, this block is executed
        print("first time watching")

    driver.switch_to.default_content()
    driver.switch_to.frame(iframe0)

    # extract the length of the video
    runningtime = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.xnvchp-info-duration > span:not(.title)"))).text
    try: 
        t = calculateRunningtime(runningtime)-elapsedTime
        elapsedTime=0
    except:
        t = calculateRunningtime(runningtime)

    print(t)

    # what if u already watched some and the running time should be shorter?
    time.sleep(t)

    # while the sleep, can i use some ai to take notes and extract the essence?
    # maybe just extract the audio -> transcription -> chatgpt
    # or if i can't get the video: just take notes simultaneously
    # i really can't be bothered to fast forward...


    # navigate to another lecture -> just for loop the whole thing?
    # go back btn to get to the dashboard maybe?
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

    # why does the page pop up when it navigates through lectures? 
    # i don't want it to bother me at all, just make it run in the background 


