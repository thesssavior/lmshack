def scraper(studentID, pw, tuple_list, driver, headless, full_auto, options, root, scrape_button):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException

    import time

    # progress of other contents is stopped 뚫기
    def remove_popup():
        try:
            # Attempt to find and click the button if it's clickable within 10 seconds
            resumemsg = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.confirm-msg-box > div.confirm-msg-text"))).get_attribute('innerText')
            elapsedTime = calculateElapsedTime(resumemsg)
            time.sleep(1)
            yesbtn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "confirm-ok-btn"))).click()
        except:
            print("first time watching")
            elapsedTime = 0
        try: 
            yesbtn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "confirm-ok-btn"))).click()
        except: 
            print("no other pages running at the same time")
        return elapsedTime

    def navigate_lecture_page():
        # lecture page
        driver.switch_to.default_content()
        iframe0 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'iframe#tool_content.tool_launch')))
        iframe0 = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#tool_content.tool_launch")))
        driver.switch_to.frame(iframe0)
        iframe1 = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.xnlailvc-commons-frame")))
        driver.switch_to.frame(iframe1)
        playbtn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "vc-front-screen-play-btn"))).click()

        elapsedTime = remove_popup()

        driver.switch_to.default_content()
        driver.switch_to.frame(iframe0)

        return elapsedTime

    def relocate_to_dashboard():
        driver.get("https://learning.hanyang.ac.kr/")
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

    # 뒤로가기
    def relocate(n=3):
        # after the lecture is done
        driver.execute_script(f"window.history.go({-n})")
        try:
            # Switch to the alert
            alert = driver.switch_to.alert            
            # Accept the alert (click OK)
            alert.accept()
        except:
            # Handle cases where no alert was present, if necessary
            pass
        driver.switch_to.default_content()

    def extract_running_time(elapsedTime):
        # extract the length of the video: maybe i should just use the time bar at the bottom of the vid
        runningtime = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.xnvchp-info-duration > span:not(.title)"))).text
        try: 
            t = calculateRunningtime(runningtime)-elapsedTime
            elapsedTime=0
        except:
            t = calculateRunningtime(runningtime)
            print("first time watching")
        return t

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

    def get_tuple_list():
        # input: login info, output: all the lectures done in order 
        # 총 걸리는 시간, 강의 리스트를 미리 가져와서 진행 상황을 보여줄 수 있음
        n_hours_left = []
        tuple_list_preprocess = []
        courses = WebDriverWait(driver, delay).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"ic-DashboardCard__link")))
        for i, course in enumerate(courses):
            # Dashboard: select course
            courses = WebDriverWait(driver, delay).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"ic-DashboardCard__link")))
            courses[i].click()

            # 주차학습
            weeklylessons = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME,"context_external_tool_140"))).click()
            iframe = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#tool_content")))
            driver.switch_to.frame(iframe)

            try:
                d_day_elems = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//span[contains(@class, 'xncb-component-sub-d_day') and contains(@class, 'D-')]")))
            except TimeoutException:
                relocate(2)
                continue

            # d_day_elem 마다 몇주차인지 가져오기
            for d_day_elem in d_day_elems:
                j = 0
                parent_div = d_day_elem.find_element(By.XPATH, "./../..")

                # 이때 영상 강의인지도 판단해서 끌어오기: 영상 이미지가 없으면 / 몇주차인지 안나와있음 / incomplete 아니면 넘김
                try: 
                    i_tag = parent_div.find_elements(By.CSS_SELECTOR, "i.xnmb-module_item-icon.mp4, i.xnmb-module_item-icon.movie, i.xnmb-module_item-icon.screenlecture")
                    # class="xnmb-module_item-completed incomplete"
                    incomplete = parent_div.find_element(By.CSS_SELECTOR, "span.xnmb-module_item-completed.incomplete")
                    week_number = parent_div.find_element(By.CSS_SELECTOR, "span.xnmb-module_item-meta_data-lesson_periods-week").text
                except:
                    continue
                
                # empty div 안에 요소가 몇개 있는지 -> 한 주차 여러강의 판단 가능.
                # 만약 한주차 여러강의 -> extra indexing 
                empty_div = d_day_elem.find_element(By.XPATH, "./../../../..")
                children_elements = empty_div.find_elements(By.XPATH, "./*")
                number_of_children = len(children_elements)
                child_div = parent_div.find_element(By.CSS_SELECTOR, "p.xnlal-attendance-list-item-meta_data-lecture_periods")
                playtime = child_div.find_element(By.XPATH, './span[not(@class)]').text
                lecture_name = parent_div.find_element(By.CSS_SELECTOR, 'a.xnmb-module_item-left-title.link').text
                
                if number_of_children > 1:
                    for k, child in enumerate(children_elements):
                        div = child.find_element(By.XPATH, "./*")
                        if div == parent_div:
                            j = k

                # "n시간 남음" 도 처리해야함
                # class="xncb-component-sub-d_day D-0", innertext = n시간 전
                if d_day_elem.text[-4:] == "시간 전":
                    # tuple = (course_number, week_number: n주차, hours left: n시간 전)
                    n_hours_left.append((i, int(week_number[:-2])-1, d_day_elem.text[:-4], j, playtime, lecture_name))
                else:
                    # tuple = (course_number, week_number: n주차, d-day: D-number)
                    tuple_list_preprocess.append((i, int(week_number[:-2])-1, d_day_elem.text[2:], j, playtime, lecture_name))
            
            # empty div 안에 요소가 몇개 있는지 -> 한 주차 여러강의 판단 가능.
            # 만약 한주차 여러강의 -> extra indexing 

            relocate(2)

        # print(n_hours_left, tuple_list_preprocess)
        sorted_n_hours_left = sorted(n_hours_left, key=lambda x: int(x[2]))
        sorted_tuple_list = sorted(tuple_list_preprocess, key=lambda x: int(x[2]))
        tuple_list1 = [(x[0], x[1], x[3], x[4], x[5]) for x in sorted_n_hours_left]
        tuple_list2 = [(x[0], x[1], x[3], x[4], x[5]) for x in sorted_tuple_list]
        tuple_list = tuple_list1+tuple_list2
        # [(course no, week no, lecture no within the week, runningtime, lecture name)...]
        print(tuple_list)
        return tuple_list

    def watch_lectures(tuple_list):
        driver.get("https://learning.hanyang.ac.kr/")

        # make sure the format is cards
        bar_elems = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.fOyUs_bGBk.eHiXd_bGBk.eHiXd_dnnz.eHiXd_ycrn.eHiXd_bPzo.eHiXd_cuTS.eHiXd_wWyq")))
        if len(bar_elems)>1:
            bar_elems[3].click()
            formats = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sJGfW_bGBk")))
            card_format = formats[0]
            link_card_format = card_format.find_element(By.XPATH,"./..").click()
        else:
            bar_elems[0].click()
            formats = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sJGfW_bGBk")))
            card_format = formats[0]
            aria_checked_value = card_format.get_attribute("aria-checked")
            # Check if it's 'true'
            if aria_checked_value == 'true':
                pass
            else:
                link_card_format = card_format.find_element(By.XPATH,"./..").click()

        for courseNo, weekNo in tuple_list:

            # dashboard
            courses = WebDriverWait(driver, delay).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"ic-DashboardCard__link")))
            
            # Select the specific element from the list based on the courseNo
            courses[courseNo].click()        

            # weekly lessons
            weeklylessons = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME,"context_external_tool_140"))).click()
            iframe = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#tool_content")))
            driver.switch_to.frame(iframe)

            # empty divs do the job!!
            lessons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[not(@*)]")))
            lesson = lessons[weekNo]

            # target the player image to identify videos
            i_tags = lesson.find_elements(By.CSS_SELECTOR, "i.xnmb-module_item-icon.mp4, i.xnmb-module_item-icon.movie, i.xnmb-module_item-icon.screenlecture")

            # n주차에서 그 주차에 있는 강의를 다 돌려주기. 
            # 강의가 2개 이상
            # 이거 i_tag를 매번 다시 찾아줘야 되나? 걍 frame 문제?
            if len(i_tags)>1:
                for i in range(len(i_tags)):
                    # renew data, navigate to the lecture
                    lessons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[not(@*)]")))
                    lesson = lessons[weekNo]
                    i_tags = lesson.find_elements(By.CSS_SELECTOR, "i.xnmb-module_item-icon.mp4, i.xnmb-module_item-icon.movie")
                    parent_div = i_tags[i].find_element(By.XPATH, "./..")
                    a_tag = parent_div.find_element(By.CSS_SELECTOR, ".xnmb-module_item-left-title.link").click()

                    # watch the video
                    elapsedTime = navigate_lecture_page()

                    # 왜 time.slee() 코드가 없냐?
                    t = extract_running_time(elapsedTime)
                    print(t)
                    time.sleep(t)

                    # relocate
                    relocate(1)
                    WebDriverWait(driver, delay).until(EC.title_contains("주차학습"))
                    iframe = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#tool_content")))
                    driver.switch_to.frame(iframe)
                
                relocate_to_dashboard()

            # 강의가 1개만 
            else: 
                i_tag = i_tags[0]
                parent_div = i_tag.find_element(By.XPATH, "./..")
                a_tag = parent_div.find_element(By.CSS_SELECTOR, ".xnmb-module_item-left-title.link").click()
                elapsedTime = navigate_lecture_page()
                t = extract_running_time(elapsedTime)
                print(t)
                time.sleep(t)
                relocate_to_dashboard()

    def full_auto_watch_lectures(tuple_list):
        driver.get("https://learning.hanyang.ac.kr/")

        # make sure the format is cards
        bar_elems = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.fOyUs_bGBk.eHiXd_bGBk.eHiXd_dnnz.eHiXd_ycrn.eHiXd_bPzo.eHiXd_cuTS.eHiXd_wWyq")))
        if len(bar_elems)>1:
            bar_elems[3].click()
            formats = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sJGfW_bGBk")))
            card_format = formats[0]
            link_card_format = card_format.find_element(By.XPATH,"./..").click()
        else:
            bar_elems[0].click()
            formats = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sJGfW_bGBk")))
            card_format = formats[0]
            aria_checked_value = card_format.get_attribute("aria-checked")
            # Check if it's 'true'
            if aria_checked_value == 'true':
                pass
            else:
                link_card_format = card_format.find_element(By.XPATH,"./..").click()

        tuple_list = [(x[0],x[1],int(x[2])) for x in tuple_list]
        for courseNo, weekNo, lectureNo in tuple_list:

            # dashboard
            courses = WebDriverWait(driver, delay).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"ic-DashboardCard__link")))
            
            # Select the specific element from the list based on the courseNo
            courses[courseNo].click()        

            # weekly lessons
            weeklylessons = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME,"context_external_tool_140"))).click()
            iframe = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#tool_content")))
            driver.switch_to.frame(iframe)

            # empty divs do the job!!
            lessons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[not(@*)]")))
            lesson = lessons[weekNo]

            # target the player image to identify videos
            i_tags = lesson.find_elements(By.CSS_SELECTOR, "i.xnmb-module_item-icon.mp4, i.xnmb-module_item-icon.movie, i.xnmb-module_item-icon.screenlecture")

            # full auto 일 때, 한 주차에 강의가 여러개, j = lectureNo 인풋 맞춰서 돌리기
            i_tag = i_tags[lectureNo]
            parent_div = i_tag.find_element(By.XPATH, "./..")
            a_tag = parent_div.find_element(By.CSS_SELECTOR, ".xnmb-module_item-left-title.link").click()
            
            elapsedTime = navigate_lecture_page()
            t = extract_running_time(elapsedTime)
            print(t)
            time.sleep(t)
            relocate_to_dashboard()

    def create_table(frame, data):
        num_rows = len(data)

        # Create a table frame
        table_frame = tk.Frame(frame)
        table_frame.pack()

        column_widths = [max([len(str(row[i])) for row in data]) for i in range(4)]

        # Create labels for column headings
        label = tk.Label(table_frame, text="과목명", padx=10, pady=5, borderwidth=1, relief="solid")
        label.grid(row=0, column=1)
        label = tk.Label(table_frame, text="주차", padx=10, pady=5, borderwidth=1, relief="solid")
        label.grid(row=0, column=2)
        label = tk.Label(table_frame, text="영상 길이", padx=10, pady=5, borderwidth=1, relief="solid")
        label.grid(row=0, column=3)
        label = tk.Label(table_frame, text="강의명", padx=10, pady=5, borderwidth=1, relief="solid")
        label.grid(row=0, column=4)

        # Create labels for each item in the list
        for i in range(num_rows):
            label = tk.Label(table_frame, text=f"{i+1}", padx=10, pady=5, borderwidth=1, relief="solid")
            label.grid(row=i+1, column=0)
            for j in range(4):
                label = tk.Label(table_frame, text=data[i][j], padx=10, pady=5, borderwidth=1, relief="solid", width=column_widths[j])
                label.grid(row=i+1, column=j+1)

    # Initialize the Chrome driver
    service = Service(executable_path=driver)
    driver = webdriver.Chrome(service=service)

    delay = 10
    wait = WebDriverWait(driver, delay) # Wait up to 10 seconds

    # login page
    driver.minimize_window()
    driver.get("https://learning.hanyang.ac.kr/")
    uid = driver.find_element(By.ID, "uid")
    uid.send_keys(studentID)
    upw = driver.find_element(By.ID, "upw")
    upw.send_keys(pw)
    login_btn = driver.find_element(By.ID, "login_btn").click()

    if full_auto:
        scrape_button.config(text="셋업 중... 약 30초 소요")
        root.update()
        tuple_list = get_tuple_list()
        import tkinter as tk
        frame = tk.Toplevel(root)
        frame.title("재생목록")
        data_list=[(options[int(x[0])], x[1]+1, x[3], x[4]) for x in tuple_list]
        create_table(frame, data_list)
        scrape_button.config(text="실행 중...")
        root.update()
        full_auto_watch_lectures(tuple_list)
    else:
        watch_lectures(tuple_list)

# tuple_list = [(1,10)]
# scraper("ssavior", "Tmdwn1290!", tuple_list, "chromedriver.exe", False, False)