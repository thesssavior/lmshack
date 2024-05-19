import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import scraper, init_set, encryption
import json, os, sys, requests

# restart
def restart_script():
    python = sys.executable
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    print(script_dir)
    chdir = os.chdir(script_dir)
    print(chdir)
    os.execl(python, python, *sys.argv)

# init
def initialize():
    settings_window = tk.Frame(root)
    settings_window.pack(fill=tk.BOTH, expand=True)

    IDlabel = tk.Label(settings_window, text="학생 ID:")
    IDlabel.grid(row=0, column=0, padx=5, pady=5)
    studentIDEntry = tk.Entry(settings_window)
    studentIDEntry.grid(row=0, column=1, padx=5, pady=5)

    pwlabel = tk.Label(settings_window, text="비번:")
    pwlabel.grid(row=1, column=0, padx=5, pady=5)
    pwEntry = tk.Entry(settings_window)
    pwEntry.grid(row=1, column=1, padx=5, pady=5)

    # Create a button to save settings
    save_button = tk.Button(settings_window, text="실행", command=lambda: init_save_settings(studentIDEntry.get(), pwEntry.get()))
    save_button.grid(row=5, columnspan=2, padx=5, pady=10)

# Save user settings to settings.json
# 굳이 수정권한을 줘야하나? 걍 initialize() 때만 돌리자
def init_save_settings(ID,pw):
    
    # scrape the list of courses 
    courses_list = init_set.init_set(studentID=ID, pw=pw, driver=chromedriver_path)

    # update settings.txt
    settings = {
        "id": ID,
        "pw": pw,
    }

    # update settings.json
    settings_open = {
        "headless": False,
        "full_auto": False,
        "version": 1.0,
        "courses": courses_list,
    }

    try:
        encryption.encryption(settings, notkey_path, txt_path)
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(settings_open, file, ensure_ascii=False)
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

def scrape_website(ID, pw, headless=False, full_auto=False, scrape_button=None):
    # access the selected values
    selected_courses = [dropdown.get() for dropdown in dropdowns if not dropdown.get()==""]
    selected_lectures = [lecture.get() for lecture in lectures]
    tuple_list = [(options.index(course), int(lecture)-1) for course, lecture in zip(selected_courses,selected_lectures)]

    scraper.scraper(studentID=ID,pw=pw,tuple_list=tuple_list,driver=chromedriver_path, headless=headless, full_auto=full_auto, options=options, root=root, scrape_button=scrape_button)

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
    settings_button.pack(side="top", padx=10)

    # Create a button to trigger scraping
    scrape_button = tk.Button(root, text="Full auto mode: 실행", command=lambda: scrape_website(ID, pw, headless, full_auto, scrape_button))
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

# Get the directory of the executable
# exe_dir = os.path.dirname(os.path.abspath(__file__))
exe_dir = os.path.dirname(sys.argv[0])
print(os.getcwd())
exe_path = os.path.join(exe_dir, "LMSauto.exe")
chromedriver_path = os.path.join(exe_dir, "chromedriver.exe")
json_path = os.path.join(exe_dir, "settings.json")
txt_path = os.path.join(exe_dir, "settings.txt")
notkey_path = os.path.join(exe_dir, "notkey.bin")
print(exe_dir)
print(chromedriver_path)
dropdowns=[]
lectures=[]

root = tk.Tk()
root.title("LMS 자동사냥")

try:
    data = encryption.decryption(notkey_path,txt_path)
    ID, pw = data["id"], data["pw"]
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        headless, full_auto = data["headless"], data["full_auto"]
        options = [course for course in data["courses"]]  
        current_version = data["version"]
    if full_auto:
        full_auto_main()
    else:
        main(options)
except Exception as e:
    print(e)
    initialize()
    
# Run the Tkinter event loop
root.mainloop()
