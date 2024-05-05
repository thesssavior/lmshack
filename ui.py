import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import main2, set_first
import json, os, sys

# restart
def restart_script():
    python = sys.executable
    os.execl(python, python, *sys.argv)

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

    # Create a button to save settings
    save_button = tk.Button(settings_window, text="Save", command=lambda: save_settings(ID=studentIDEntry.get(), pw=pwEntry.get()))
    save_button.grid(row=5, columnspan=2, padx=5, pady=10)

# Save user settings to file
def save_settings(ID,pw):
    courses_list = set_first.set_first(studentID=ID, pw=pw, driver=chromedriver_path)
    print(courses_list)
    settings = {
        "id": ID,
        "pw": pw,
        "courses": courses_list
    }
    try:
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(settings, file, ensure_ascii=False)
        with open(json_path, "r", encoding="utf-8") as file:
            print("hey")
            data = json.load(file)
            print(data)
    except Exception as e:
        print(f"{e}")

    

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

def scrape_website(ID, pw):
    # access the selected values
    print(dropdowns, lectures)
    selected_courses = [dropdown.get() for dropdown in dropdowns if not dropdown.get()==""]
    selected_lectures = [lecture.get() for lecture in lectures]
    tupleList = [(options.index(course), int(lecture)-1) for course, lecture in zip(selected_courses,selected_lectures)]

    # 왜안되누?
    # processing = tk.Toplevel(root)
    # time_left = tk.Label(processing, text="wassup")
    # time_left.pack(padx=20, pady=20, side="bottom")

    main2.scraper(studentID=ID,pw=pw,tupleList=tupleList,driver=chromedriver_path)

    # Your web scraping code goes here
    messagebox.showinfo("Scraping Complete", "자동사냥 완료")

# Create the settings window
def open_settings_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    IDlabel = tk.Label(settings_window, text="Enter student ID:")
    IDlabel.grid(row=0, column=0, padx=5, pady=5)
    studentIDEntry = tk.Entry(settings_window)
    studentIDEntry.grid(row=0, column=1, padx=5, pady=5)

    pwlabel = tk.Label(settings_window, text="Enter password:")
    pwlabel.grid(row=1, column=0, padx=5, pady=5)
    pwEntry = tk.Entry(settings_window)
    pwEntry.grid(row=1, column=1, padx=5, pady=5)

    # Create a button to save settings
    save_button = tk.Button(settings_window, text="저장 (10초 쯤 소요)", command=lambda: save_settings(ID=studentIDEntry.get(), pw=pwEntry.get()))
    save_button.grid(row=5, columnspan=2, padx=5, pady=10)

# after init
def afterset(options):
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
    scrape_button = tk.Button(root, text="실행", command=lambda: scrape_website(ID, pw))
    scrape_button.pack(side="bottom")

    # Create a button to add more dropdowns
    add_dropdown_button = tk.Button(root, text="강의 추가", command=add_dropdown)
    add_dropdown_button.pack(side="bottom")

chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
# Get the directory of the executable
exe_dir = os.path.dirname(sys.argv[0])

# Define the path to the settings file
json_path = os.path.join(exe_dir, "settings.json")

dropdowns=[]
lectures=[]

root = tk.Tk()
root.title("LMS 자동사냥")

try:
    print(json_path)
    with open(json_path, "r", encoding="utf-8") as file:
        if os.access(json_path, os.R_OK):
            print("File has read permission")
        else:
            print("File does not have read permission")

        print("hey")
        data = json.load(file)
        ID, pw = data["id"], data["pw"]
        options = [course for course in data["courses"]]        
        afterset(options)
except FileNotFoundError:
    print(f"Error: JSON file not found at {json_path}")
except Exception as e:
    print(f"Error: {e}")
    initialize()

# Run the Tkinter event loop
root.mainloop()
