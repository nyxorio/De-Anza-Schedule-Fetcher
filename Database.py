'''
Maiah Pardo & Minh Pham
CIS 41B  |  Spring 2019
Final Project Backend

This file uses web scraping and threading to get De Anza class data by a chosen quarter, then adds data to an SQL database
'''

import re
import requests
import queue
from bs4 import BeautifulSoup
import sqlite3
import threading
import os

#QUARTER, DATABASE = 'F2018', 'Fall2018_Classes.db'   # Fall 2018 quarter
#QUARTER, DATABASE = 'M2019', 'Summer2019_Classes.db' # Summer 2019 quarter
QUARTER, DATABASE = 'S2019', 'Spring2019_Classes.db' # Spring 2019 quarter
#QUARTER, DATABASE = 'W2019', 'Winter2019_Classes.db' # Winter 2019 quarter

URL_CATALOG = "https://www.deanza.edu/schedule/"
URL_CLASS_LISTING = "https://www.deanza.edu/schedule/listings.html?dept={}&t={}" # department, quarter
URL = "https://www.deanza.edu" # to add partial links

try:
    page = requests.get(URL_CATALOG)
except requests.exceptions.RequestException as ex:
    raise SystemExit("Could not connect to", URL_CATALOG, ex)
soup = BeautifulSoup(page.content, 'lxml')
departments = {}
for info in soup.select('select option'):
    data = info.text.split(' - ')
    if(len(data) == 2):
        departments[data[1]] = data[0]      # key = full class name, val = short cut name (to fill in URL_CLASS_SCHED)

def getData(dep, q):
    '''task function to get all class data from webscraping, store into a list and put into a queue'''
    try:
        page_classes = requests.get(URL_CLASS_LISTING.format(departments[dep], QUARTER))
    except requests.exceptions.RequestException as ex:
        raise SystemExit("Could not connect to url", URL_CLASS_LISTING, ex)

    soup = BeautifulSoup(page_classes.content, 'lxml')
    try:
        data = soup.select(f"tbody tr[class*={departments[dep].replace('/', '-')}]")
    except AttributeError as e:
        return

    for tag in data:
        rows = tag.find_all('td')
        if rows[0].text not in ['LAB', 'TBA', 'CLAS']: # if row only contains class data
            class_details_partial_link = tag.find('a')['href']  # partial link of class title
            class_data = [i.text for i in rows]
            class_data[9] = dep # replace index 9 with department
            if re.search('View Footnote', class_data[4]):
                class_data[4] = re.sub('View Footnote', '', class_data[4])
            if re.search('·', class_data[5]):
                class_data[5] = re.sub('·', '', class_data[5])
            if class_data[7].isupper(): # if teacher name is all caps
                class_data[7] = (class_data[7]).title() # proper name format

            # class title link to get class details
            link = URL + str(class_details_partial_link)
            try:
                page_details = requests.get(link)
            except requests.exceptions.RequestException as e:
                raise SystemExit("Could not connect to url", URL_CLASS_LISTING, e) # raise a different error

            soup = BeautifulSoup(page_details.content, 'lxml')
            s = soup.select('div dl dd')
            class_data.append(float((s[0].text).replace(' Units', ''))) # units
            class_data.append(s[-1].text) # pre-requisites

            description = soup.select_one('div p')
            class_data.append(description.text)
            q.put(class_data)


q = queue.Queue()
data_list = []
threads = []

for dep in departments: # 77 departments
    t = threading.Thread(target=getData, args=(dep, q)) # 77 threads
    threads.append(t)
    t.start()

for t in threads:
    t.join()
    while not q.empty(): # each thread puts multiple items in the queue (num of classes in the department)
        data_list.append(q.get())

if not os.path.exists('Database'):
    os.mkdir('Database')
os.chdir(os.path.join(os.getcwd(), 'Database'))

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS Groups")
cur.execute("DROP TABLE IF EXISTS Departments")
cur.execute("DROP TABLE IF EXISTS Instructors")
cur.execute("DROP TABLE IF EXISTS Classes")

cur.execute('''CREATE TABLE Groups(
                        id INTEGER PRIMARY KEY UNIQUE,
                        name TEXT UNIQUE ON CONFLICT IGNORE
                        );''')


cur.execute('''CREATE TABLE Departments(
                        id INTEGER PRIMARY KEY,
                        abbrv TEXT,
                        dep TEXT UNIQUE ON CONFLICT IGNORE,
                        group_id INTEGER
                        );''')

cur.execute('''CREATE TABLE Instructors(
                        id INTEGER PRIMARY KEY,
                        name TEXT UNIQUE ON CONFLICT IGNORE
                        );''')

cur.execute('''CREATE TABLE Classes (
                    crn INTEGER PRIMARY KEY,
                    tag TEXT,
                    section TEXT,
                    status TEXT,
                    name TEXT,
                    days TEXT,
                    time TEXT,
                    instructor_id INTEGER,
                    location TEXT,
                    department_id INTEGER,
                    units REAL,
                    prerequisites TEXT,
                    description TEXT
                    );''')

grouping = {
    'APRN': 'Automotive Technology', 'AUTO':'Automotive Technology', 'SPED':'Disability Support', 'EDAC':'Disability Support' ,'LS': 'Disability Support',
    'LRNA': 'Disability Support', 'ES': 'Environmental Studies', 'ESCI': 'Environmental Studies', 'HUMI': 'Social Science & Humanities',
    'POLI': 'Social Science & Humanities', 'COMM':'Social Science & Humanities', 'GEO': 'Social Science & Humanities',
    'ECON': 'Social Science & Humanities', 'LING': 'Social Science & Humanities', 'PSYC': 'Social Science & Humanities',
    'PHIL': 'Social Science & Humanities', 'ANTH':'Social Science & Humanities', 'SOSC':'Social Science & Humanities',
    'SOC':'Social Science & Humanities', 'ASTR': 'Natural Science', 'MET': 'Natural Science', 'GEOL': 'Natural Science',
    'BIOL': 'Natural Science', 'PHYS': 'Natural Science', 'CHEM': 'Natural Science', 'FREN':'Language Studies',
    'KORE':'Language Studies', 'PERS':'Language Studies', 'MAND':'Language Studies', 'SPAN':'Language Studies',
    'SIGN':'Language Studies', 'JAPN':'Language Studies', 'RUSS':'Language Studies', 'HNDI':'Language Studies',
    'ITAL':'Language Studies', 'VIET':'Language Studies', 'GERM':'Language Studies', 'INTL':'International & Intercultural Studies',
    'ICS':'International/Intercultural Studies', 'CD':'Child Development', 'LART':'English Studies', 'ESL':'English Studies',
    'EWRT':'English Studies', 'READ':'English Studies', 'LIB':'English Studies', 'ELIT':'English Studies', 'SKIL':'English Studies',
    'ARTS':'Arts', 'PHTG':'Arts', 'MUSI':'Arts', 'THEA':'Arts', 'DANC':'Physical Education', 'PE':'Physical Education',
    'KNES':'Physical Education', 'CIS':'Computer Science & Engineering', 'ENGR': 'Computer Science & Engineering',
    'EDUC':'Education', 'COUN':'Counceling & Guidance', 'GUID':'Counceling & Guidance', 'CLP':'Counceling & Guidance',
    'ACCT': 'Mathematics', 'MATH':'Mathematics', 'WMST':'Women\'s Studies', 'HUMA':'Health', 'HTEC':'Health', 'NURS':'Health',
    'HLTH':'Health', 'NUTR':'Health', 'MASG':'Health', 'HIST':'History', 'ADMJ': 'Law & Legal System', 'PARA': 'Law & Legal System',
    'REST':'Real Estate', 'BUS':'Business', 'JOUR':'Journalism & Television', 'F/TV':'Journalism & Television',
    'DMT': 'Design & Manufacturing'
    }

for group in grouping.values():
    cur.execute("INSERT INTO Groups (name) VALUES (?)", (group,))

for full, abbr in departments.items():
    cur.execute("SELECT id FROM Groups WHERE name=?", (grouping[abbr],))
    cur.execute("INSERT INTO Departments (abbrv, dep, group_id) VALUES (?, ?, ?)", (abbr, full, cur.fetchone()[0]))

for data in data_list:
    cur.execute("SELECT id FROM Departments WHERE abbrv = ?", (data[1].split()[0],))
    department_id = cur.fetchone()[0]

    cur.execute("INSERT INTO Instructors (name) VALUES (?)", (data[7],))
    cur.execute("SELECT id FROM Instructors WHERE name = ?", (data[7],))
    instructor_id = cur.fetchone()[0]

    cur.execute("INSERT OR REPLACE INTO Classes (crn, tag, section, status, name, days, time, instructor_id, location,\
                department_id, units, prerequisites, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",\
                (data[0], data[1], data[2], data[3], data[4], data[5], data[6], instructor_id, data[8],\
                department_id, data[10], data[11], data[12]))

conn.commit()
conn.close()