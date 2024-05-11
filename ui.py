import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import scraper, init_set
import json, os, sys, requests

# restart
def restart_script():
    python = sys.executable
    os.execl(python, python, *sys.argv)

# user verification
def verify(license_key):
    import requests
    err = True
    url = 'https://api.gumroad.com/v2/licenses/verify'
    print(license_key)
    data = {
        'product_id': 'r6TqyTDBMrjaNF7tsRfMlA==',
        'license_key': license_key
    }

    # Making a POST request with data
    response = requests.post(url, data=data)

    # Checking the response status
    if response.status_code == 200:
        # If the request was successful, print the response content
        res = response.json()
        print(res)
        err = False
    else:
        # If there was an error, print the status code and error message
        print(f"Error: {response.status_code} - {response.text}")
        messagebox.showinfo("error", "라이센스 키 확인")
    return err

# init
def initialize():
    settings_window = tk.Frame(root)
    settings_window.pack(fill=tk.BOTH, expand=True)

    IDlabel = tk.Label(settings_window, text="Enter student ID:")
    IDlabel.grid(row=0, column=0, padx=5, pady=5)
    studentIDEntry = tk.Entry(settings_window)
    studentIDEntry.grid(row=0, column=1, padx=5, pady=5)

    pwlabel = tk.Label(settings_window, text="Enter password:")
    pwlabel.grid(row=1, column=0, padx=5, pady=5)
    pwEntry = tk.Entry(settings_window)
    pwEntry.grid(row=1, column=1, padx=5, pady=5)

    license_key_label = tk.Label(settings_window, text="라이센스 키 (이메일 확인)")
    license_key_label.grid(row=2, column=0, padx=5, pady=5)
    license_key_entry = tk.Entry(settings_window)
    license_key_entry.grid(row=2, column=1, padx=5, pady=5)

    # Create a button to save settings
    save_button = tk.Button(settings_window, text="Save", command=lambda: init_save_settings(studentIDEntry.get(), pwEntry.get(), license_key_entry.get().strip()))
    save_button.grid(row=5, columnspan=2, padx=5, pady=10)

# Save user settings to settings.json
# 굳이 수정권한을 줘야하나? 걍 initialize() 때만 돌리자
def init_save_settings(ID,pw,license_key):
    # user verification
    err = verify(license_key=license_key)
    if err:
        return 
    
    # scrape the list of courses 
    courses_list = init_set.init_set(studentID=ID, pw=pw, driver=chromedriver_path)

    # update settings.json
    settings = {
        "id": ID,
        "pw": pw,
        "courses": courses_list,
        "license_key": license_key,
        "headless": False,
        "full_auto": False
    }
    try:
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(settings, file, ensure_ascii=False)
    except Exception as e:
        print(e)
        pass

    restart_script()
    
def add_dropdown():
    # Create a new dropdown menu
    new_courses_label = tk.Label(root, text="과목명:")
    new_courses_label.pack()
    newCourse = tk.StringVar(root)
    new_dropdown = ttk.Combobox(root, textvariable=newCourse, values=options)
    new_dropdown.pack()
    dropdowns.append(new_dropdown)

    newLecturelabel = tk.Label(root, text="몇주차?:")
    newLecturelabel.pack()
    newLectureNoEntry = tk.Entry(root)
    newLectureNoEntry.pack()
    lectures.append(newLectureNoEntry)

def scrape_website(ID, pw, headless=False, full_auto=False):
    # access the selected values
    selected_courses = [dropdown.get() for dropdown in dropdowns if not dropdown.get()==""]
    selected_lectures = [lecture.get() for lecture in lectures]
    tuple_list = [(options.index(course), int(lecture)-1) for course, lecture in zip(selected_courses,selected_lectures)]

    scraper.scraper(studentID=ID,pw=pw,tuple_list=tuple_list,driver=chromedriver_path, headless=headless, full_auto=full_auto)

    messagebox.showinfo("Scraping Complete", "자동사냥 완료")

# update settings.json, headless and full_auto only 
def save_settings(headless, full_auto):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["headless"] = headless
    data["full_auto"] = full_auto

    try:
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)
    except Exception as e:
        print(e)
        pass

    restart_script()

# Create the settings window
def open_settings_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("설정")

    # headless option
    headless_var = tk.BooleanVar()
    headless_var.set(headless)  

    headless_label = tk.Label(settings_window, text="Headless", width=6)
    headless_label.grid(row=0, column=0, padx=10, pady=5)
    headless_button = tk.Checkbutton(settings_window, variable=headless_var, command=lambda: print("headless: ",headless_var.get()))
    headless_button.grid(row=0, column=1, padx=10, pady=5)

    # full_auto option
    switch_var = tk.BooleanVar()
    switch_var.set(full_auto)  

    switch_label = tk.Label(settings_window, text="Full auto", width=6)
    switch_label.grid(row=1, column=0, padx=10, pady=5)
    switch_button = tk.Checkbutton(settings_window, variable=switch_var, command=lambda: print("full auto: ",switch_var.get()))
    switch_button.grid(row=1, column=1, padx=10, pady=5)

    # Create a button to save settings
    save_button = tk.Button(settings_window, text="저장", command=lambda: save_settings(headless_var.get(),switch_var.get()))
    save_button.grid(row=5, columnspan=2, padx=5, pady=10)

# main ui if full_auto = True
def full_auto_main():
    # Create a button to open settings window
    settings_button = tk.Button(root, text="설정", command=open_settings_window)
    settings_button.pack(side="top", padx=10, pady=10)

    # Create a button to trigger scraping
    scrape_button = tk.Button(root, text="Full auto mode: 실행", command=lambda: scrape_website(ID, pw, headless, full_auto))
    scrape_button.pack(side="bottom", padx=10, pady=10)


# main ui after init
def main(options):
    # Create a button to open settings window
    settings_button = tk.Button(root, text="설정", command=open_settings_window)
    settings_button.pack(side="top")

    # receive courseNo
    # Create a label for the dropdown
    courses_label = tk.Label(root, text="과목명:")
    courses_label.pack()

    # Create the initial dropdown
    dropdown_var = tk.StringVar(root)
    dropdown = ttk.Combobox(root, textvariable=dropdown_var, values=options)
    dropdown.pack()
    dropdowns.append(dropdown)

    # lectureNo
    lecturelabel = tk.Label(root, text="몇주차?:")
    lecturelabel.pack()
    lectureNoEntry = tk.Entry(root)
    lectureNoEntry.pack()
    lectures.append(lectureNoEntry)

    # Create a button to trigger scraping
    scrape_button = tk.Button(root, text="실행", command=lambda: scrape_website(ID, pw, headless, full_auto))
    scrape_button.pack(side="bottom")

    # Create a button to add more dropdowns
    add_dropdown_button = tk.Button(root, text="강의 추가", command=add_dropdown)
    add_dropdown_button.pack(side="bottom")

# chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
# Get the directory of the executable
exe_dir = os.path.dirname(sys.argv[0])
chromedriver_path = os.path.join(exe_dir, "chromedriver.exe")
json_path = os.path.join(exe_dir, "settings.json")

dropdowns=[]
lectures=[]

root = tk.Tk()
root.title("LMS 자동사냥")

try:
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        ID, pw, license_key, headless, full_auto = data["id"], data["pw"], data["license_key"], data["headless"], data["full_auto"]
        options = [course for course in data["courses"]]  
        if full_auto:
            full_auto_main()
        else:
            main(options)
except:
    initialize()
    
# Run the Tkinter event loop
root.mainloop()
