This is a program made by Maiah Pardo and Minh Pham to allow convenient access and reading of data from the De Anza courses offered during each quarter. It can be modified to include more quarters with relative ease, each with their own SQL database to store the data.

Database.py
====================================================================================================
This file should be executed before the GUI is started up. While definitely inconvenient, since the database is static as opposed to De Anza course statuses and courses ever changing, it makes it easier for the user to access data. It is possible to slightly rewrite this program to accept input argument for the desired quarter and fetch data on demand for the SQL database, however that operation is extremely lengthy (~1 min 10 seconds) even with multithreading due to the massive amount of data to be fetched from the websites.

This file accesses the De Anza website to fetch department groups, departments, courses offered by all these departments for the indicated quarter, and all the information avaiable for each course. It is made within bounds of De Anza's robots.txt.

The following modules are used in this python program:
- Web Access
- Database (SQL)
- System
- Multithreading
====================================================================================================

GUI.py
====================================================================================================
This file should be executed with databases already made. This program presents the user with an interactible GUI with many options and elements.

The mainWindow (Department Groups) will display all available quarters and department groups, allowing for the user to quickly narrow down the results they wish to view. Missing databases will show a warning for user. In addition, the user can quickly view graphs of different department groups'/departments' popularity for each quarter by simply selecting the quarter and clicked the appropriate graph button in the side menu. If exited, all windows including any open graphs will be terminated.

The next window (Departments) will display all the departments in the groups selected by the user. From here, the user can choose to filter and results from a variety of options (seating status, meeting dates, and course number) or simply fetch all available course numbers for the department they selected. In addition, the user can quickly compare the popularity between the departments that they have selected via a graph. If exited, the user will be returned to Department Groups.

The next window (Course ID) will display the course numbers available in the department for the quarter, with the user having the option to select what course numbers they want to list the classes for. In addition, they can quickly view the popularity of the courses they selected by a graph. If exited, the user will be returned to Departments.

The last window (Courses) will display details about each available class from the course selection indicated by the user. From here, the user can see details such as the CRN, Full course ID, Status, Course Name, Date, Time, Professor, Location, and Units. If they select course from this list, they can have the option to click Save Schedule to save their selected courses into a txt file. This txt file can also include course description and prerequisites if the user chooses. Once done saving, the user will then be returned to Courses window where they can save a different combination of classes. If exited, the user will be returned to Departments.

The following modules are used in this python program:
- Data Analysis (numpy) + Visualization (matplotlib)
- GUI
- Database (SQL)
- System