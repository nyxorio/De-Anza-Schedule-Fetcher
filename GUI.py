'''
Maiah Pardo & Minh Pham
CIS 41B  |  Spring 2019
Final Project Frontend
'''

import matplotlib
matplotlib.use('TkAgg')
import tkinter as tk, tkinter.messagebox as tkmb, tkinter.filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import ttk
import sqlite3
import os
import re
import numpy as np

CURRENT = 'Spring 2019'

class Master(tk.Tk):
    '''Main window for fetching data and displaying list of states'''
    def __init__(self):
        super().__init__()
        self.title("Departments Groups")
        self.resizable(False, False)
        self.geometry("+720+0")

        quarters = ['Fall 2018', 'Winter 2019', 'Spring 2019', 'Summer 2019']
        self.quarterSelection = tk.StringVar()
        self.quarterSelection.set(CURRENT)
        for i, q in zip(range(len(quarters)), quarters):
            tk.Radiobutton(self, text=q, variable=self.quarterSelection, value=q).grid(row=0,column=i,sticky='w')

        for q in quarters:
            filename = 'Database'+os.sep+(q.replace(' ', '')+'_Classes.db')
            if os.path.isfile(filename):
                conn = sqlite3.connect(filename)
                break
        try:
            cur = conn.cursor()
        except UnboundLocalError:
            print('No database available for data')
            self.destroy()
            return

        cur.execute("SELECT name FROM Groups ORDER BY name")

        tk.Label(self, text="Select the department group(s) you would like to list").grid(columnspan=4)
        F = tk.Frame(self)
        S = tk.Scrollbar(F)
        self.lb = tk.Listbox(F, width=40, selectmode="multiple", yscrollcommand=S.set)
        self.lb.insert(tk.END, *[d[0] for d in cur.fetchall()])
        conn.close()

        self.lb.grid()
        S.grid(row=0,column=1, sticky='ns')
        S.config(command=self.lb.yview)
        F.grid(columnspan=4)

        tk.Button(self, text="Compare All Departments", command=lambda: graphAllDepartmentsMenu(self)).grid(columnspan=2, column=1, sticky='w')
        tk.Button( self, text="Ok", command=lambda: Departments(self, self.quarterSelection.get(), [self.lb.get(i) for i in self.lb.curselection()] ) ).grid(row=3, column=2, columnspan=2, sticky='n')

class Departments(tk.Toplevel):
    '''Window with all departments based on the group selected'''
    def __init__(self,master, quarter:str, groupNames:list):
        super().__init__(master)
        self.title("Departments")
        self.focus_set()
        self.grab_set()
        self.resizable(False, False)
        self.geometry("+720+0")

        if len(groupNames) == 0:
            tkmb.showerror("Invalid Selection", "Please select at least one department group.", parent=self)
            self.destroy()
            return
        if not os.path.isfile('Database'+os.sep+quarter.replace(' ','')+'_Classes.db'):
            tkmb.showerror("Invalid Quarter", "Quarter does not have a database created.", parent=self)
            self.destroy()
            return

        def done():
            conn.close()
            self.destroy()
            plt.close('all')
        self.protocol("WM_DELETE_WINDOW", done)

        conn = sqlite3.connect('Database'+os.sep+quarter.replace(' ','')+'_Classes.db')
        self.cur = conn.cursor()

        departments = []
        for groupName in groupNames:
            self.cur.execute("SELECT Departments.dep FROM Departments JOIN Groups ON Departments.group_id = Groups.id AND Groups.name = ?",(groupName,))
            for d in self.cur.fetchall():
                departments.append(d[0])

        tk.Label(self, text="Select the departments you would like to view").grid(columnspan=4)
        F = tk.Frame(self)
        S = tk.Scrollbar(F)
        self.lb = tk.Listbox(F, width=40, selectmode="multiple", yscrollcommand=S.set)
        self.lb.insert(tk.END, *sorted(departments))

        self.lb.grid()
        S.grid(row=0,column=1, sticky='ns')
        S.config(command=self.lb.yview)
        F.grid(columnspan=4)

        self.filters = [[], {'filter': 'Inclusive'}, ('Greater than:', 0)]  # [statuses], {days selected: True/False}, ('Greater'/'Equal'/'Less', num)

        tk.Button( self, text="Filter", command=lambda: filterWindow(self, [self.lb.get(i) for i in self.lb.curselection()]) ).grid(row=3, column=1)
        tk.Button( self, text="Fetch Courses", command=lambda: tagDisplay(self, [self.lb.get(i) for i in self.lb.curselection()]) ).grid(row=3, column=2)
        tk.Button( self, text="Graph Selected Departments by Popularity", command=lambda:graphDepsPopularity(self, quarter)).grid(columnspan=4, sticky='n')

class filterWindow(tk.Toplevel):
    '''Window for user to select filters for the courses'''
    def __init__(self, master, selection:list):
        super().__init__(master)
        self.transient(master)
        self.master = master
        self.focus_set()
        self.title("Filter")
        self.grab_set()
        self.resizable(False, False)
        self.geometry("+720+0")

        if len(selection) == 0:
            tkmb.showerror("Invalid Selection", "Please select at least one course.", parent=self)
            self.destroy()
            return

        F1 = tk.Frame(self)
        tk.Label(F1, text="Select the course status(es) you wanted to be displayed.").grid(columnspan=2)
        lb = tk.Listbox(F1, width=40, selectmode="multiple")
        lb.insert(tk.END, *['Open', 'WL', 'Full'])
        if len(master.filters[0])!=0:
            for status in master.filters[0]:
                lb.selection_set(lb.get(0, "end").index(status))
        lb.grid()
        F1.grid(columnspan=2)

        F2 = tk.Frame(self)
        tk.Label(F2, text="Select the days that the course sessions include").grid(columnspan=3)
        days = [tk.BooleanVar() for i in range(6)]
        choices = ['M', 'T', 'W', 'R', 'F', 'Online']
        if len(master.filters[1])>1:
            for i,c in zip( range(len(days)), choices ):
                days[i].set(master.filters[1][c])
        for j in range(2):
            for k in range(3):
                tk.Checkbutton(F2, text=choices[j*3+k], variable=days[j*3+k]).grid(row=j+1, column=k, sticky='w')
        dateFilter = tk.StringVar(value=master.filters[1]['filter'])
        tk.Radiobutton(F2, text="Inclusive: Class include one or more days", variable=dateFilter, value='Inclusive').grid(columnspan=3)
        tk.Radiobutton(F2, text="Strict: Class days must match all selected", variable=dateFilter, value='Strict').grid(columnspan=3)
        F2.grid(columnspan=2)

        F3 = tk.Frame(self)
        tk.Label(F3, text="Enter course number filter").grid(columnspan=3)
        tk.Label(F3, text="Course is ").grid()
        comp = tk.StringVar(value=master.filters[2][0])
        tk.OptionMenu(F3, comp, "Greater than:", "Equal to:", "Less than:").grid(row=1, column=1)
        num = tk.StringVar(value=master.filters[2][1])
        e = tk.Entry(F3, textvariable=num)
        e.grid(row=1, column=2)
        F3.grid(columnspan=2)

        def ok():
            master.filters[0] = [lb.get(i) for i in lb.curselection()]  # list for statuses
            master.filters[1]['filter'] = dateFilter.get()              # filter setting for date
            if any(d.get() for d in days):                              # checks for a True value to be saved
                for c,i in zip(choices, range(len(choices))):
                    master.filters[1][c] = days[i].get()                # dictionary with date: selected boolean
            try:
                master.filters[2] = (comp.get(), int(num.get()))        # tuple with comparision mode and number
                self.destroy()
            except:
                tkmb.showerror("Error", "Invalid input for Course Number Filter")
                num.set(0)
                return
            tagDisplay(master, selection)

        def reset():
            master.filters = [[], {'filter': 'Inclusive'}, ('Greater than:', 0)]
            lb.selection_clear(0, tk.END)
            for i in range(len(days)):
                days[i].set(False)
            dateFilter.set(master.filters[1]['filter'])
            comp.set(master.filters[2][0])
            num.set(master.filters[2][1])

        tk.Button(self, text="Reset", command=reset).grid(sticky='n')
        tk.Button(self, text="Filter", command=ok).grid(row=3, column=1, sticky='n')

class tagDisplay(tk.Toplevel):
    '''class to display all course numbers based on filter(s)'''
    def __init__(self, master, selection:list):
        super().__init__(master)
        self.transient(master)
        self.master = master
        self.focus_set()
        self.title("Course Selection")
        self.grab_set()
        self.resizable(False, False)
        self.geometry("+720+0")

        if len(selection) == 0:
            tkmb.showerror("Invalid Selection", "Please select at least one department.", parent=self)
            self.destroy()
            return

        courses = set()
        self.cur = master.cur

        def key(s):
            tag, num, letters = re.match(r'([A-Z]*) (\d*)([A-Z]*)', s).groups()
            return tag, int(num), letters

        for i in selection:
            master.cur.execute("SELECT Classes.tag FROM Classes JOIN Departments ON Classes.department_id=Departments.id AND Departments.dep = ?", (i, ))
            for data in master.cur.fetchall():
                courses.add(data[0])

        if(master.filters[2][1]>0):
            if master.filters[2][0].startswith('Greater'):
                courses = [ c for c in courses if int(re.findall(r"\d+", c)[0]) >= master.filters[2][1] ]
            elif master.filters[2][0].startswith('Less'):
                courses = [ c for c in courses if int(re.findall(r"\d+", c)[0]) <= master.filters[2][1] ]
            else: courses = [ c for c in courses if int(re.findall(r"\d+", c)[0]) == master.filters[2][1] ]

        tk.Label(self, text="Select the courses you would like to list").grid(columnspan=4)
        F = tk.Frame(self)
        S = tk.Scrollbar(F)
        self.lb = tk.Listbox(F, width=40, selectmode="multiple", yscrollcommand=S.set)
        if(len(courses)==0):
            self.destroy()
            tkmb.showinfo(":(", "There are no courses available for this department during this quarter.", parent=master)
            return
        self.lb.insert(tk.END, *sorted(courses, key=key))

        self.lb.grid()
        S.grid(row=0,column=1, sticky='ns')
        S.config(command=self.lb.yview)
        F.grid(columnspan=4)

        tk.Button( self, text="Graph Course Popularity", command=lambda: graphCoursePopularity(self, self.cur, [self.lb.get(i) for i in self.lb.curselection()]) ).grid(row=3, padx=10, pady=10)
        tk.Button( self, text="Fetch Classes", command=lambda: courseDisplay(self, [self.lb.get(i) for i in self.lb.curselection()]) ).grid(row=3, column=3, padx=10, pady=10)

class courseDisplay(tk.Toplevel):
    '''class for displayWindow for course selection'''
    def __init__(self, master, selection:list):
        super().__init__(master)
        self.transient(master)
        self.focus_set()
        self.title("Course Selection")
        self.grab_set()
        self.resizable(False, False)

        if len(selection) == 0:
            tkmb.showerror("Invalid Selection", "Please select at least one course number.", parent=self)
            self.destroy()
            return

        self.master = master
        self.cur = master.cur
        filters = master.master.filters

        self.cols = ['CRN', 'Course ID', 'Status', 'Course Name', 'Date', 'Time', 'Professor', 'Location', 'Units']

        def done():
            self.destroy()
            master.destroy()
            master.master.grab_set()
            master.master.focus_set()
        self.protocol("WM_DELETE_WINDOW", done)

        tk.Label(self, text="Select courses to save to file or graph (Hold Ctrl or Shift to select multiple).").grid(columnspan=len(self.cols), sticky='n')

        F = tk.Frame(self)
        verticalScroll = tk.Scrollbar(F)
        horizontalScroll = tk.Scrollbar(F, orient=tk.HORIZONTAL)
        lb = ttk.Treeview(F, columns=self.cols, show='headings', xscrollcommand=horizontalScroll, yscrollcommand=verticalScroll)
        lb.column('#1', width=50, minwidth=50, stretch=False)
        lb.column('#2', width=100, minwidth=85, stretch=False)
        lb.column('#3', width=50, minwidth=50, stretch=False)
        lb.column('#4', width=440, minwidth=250, stretch=False)
        lb.column('#5', width=80, minwidth=80, stretch=False)
        lb.column('#6', width=125, minwidth=125, stretch=False)
        lb.column('#7', width=170, minwidth=170, stretch=False)
        lb.column('#8', width=100, minwidth=100, stretch=False)
        for col in self.cols:
            lb.heading(col, text=col, anchor='w')

        courseData = []
        for i in selection:
            self.cur.execute("SELECT * FROM Classes JOIN Instructors ON Classes.instructor_id=Instructors.id AND Classes.tag = ? ORDER BY Classes.section", (i, ))
            for data in self.cur.fetchall():
                courseData.append(data)

        if len(filters[1].values())>1:
            if 'Online' in filters and filters[1]['Online']:
                courseData = [ c for c in courseData if c[8]=='ONLINE' ]
            elif filters[1]['filter'] == 'Inclusive':
                days = [ k for k,v in filters[1].items() if v==True ]
                courseData = [ course for course in courseData if any( d in course[5] for d in days) ]
            else:
                days = [ k for k,v in filters[1].items() if v==True ]
                courseData = [ course for course in courseData if all( d in course[5] for d in days) ]

        if (len(filters[0])>0):
            courseData = [ course for status in filters[0] for course in courseData if course[3]==status ]

        for data in courseData:
            lb.insert( '', 'end', values=(data[0], data[1]+'-'+data[2], data[3], data[4], data[5], data[6], data[-1], data[8], data[10]) )

        lb.grid()
        verticalScroll.grid(row=0, column=1, sticky='ns')
        horizontalScroll.grid(sticky='ew')
        verticalScroll.config(command=lb.yview)
        horizontalScroll.config(command=lb.xview)
        F.grid(columnspan=6, sticky='w')

        tk.Button( self, text="Save Schedule", command=lambda: self.save( [lb.item(i) for i in lb.selection()] ) ).grid(column=3, sticky='w')

    def save(self, selection:list):
        '''method to save selected data to file'''
        if len(selection) == 0:
            tkmb.showerror("Invalid Selection", "Please select at least one course.", parent=self)
            return

        extra = tkmb.askyesnocancel('Detailed information', 'Do you want to include information on prerequisites and course description?', parent=self)
        if extra == None: return
        fileLocation = tk.filedialog.asksaveasfilename(initialdir='.',initialfile='schedule.txt', filetypes = (("Text Documents", "*.txt"),), parent=self)
        if fileLocation == '':                                 # check for X or Cancel
            return
        if os.path.isfile(fileLocation):
            os.remove(fileLocation)     # reset schedule.txt

        with open(fileLocation, 'a') as f:
            f.write( "{:5}  |  {:12}  |  {:6}  |  {:78}  |  {:5}  |  {:17}  |  {:29}  |  {:8}  |  {}\n".format(*self.cols) )
            f.write( "-"*205+"\n" )
            for data in [ i['values'] for i in selection ]:
                f.write( "{:5}  |  {:12}  |  {:6}  |  {:78}  |  {:5}  |  {:17}  |  {:29}  |  {:^8}  |  {}\n".format(*data) )
                if extra==True:
                    self.cur.execute("SELECT description, prerequisites FROM Classes WHERE crn=?", (data[0],))
                    result = self.cur.fetchall()
                    f.write("\nCourse Description: "+result[0][0]+'\n')
                    f.write("\nCourse Prerequisites: "+result[0][1]+'\n')
                    f.write( "-"*205+"\n" )

        self.master.master.filters = [[], {'filter': 'Inclusive'}, ('Greater than:', 0)]

class graphAllDepartmentsMenu(tk.Toplevel):
    '''Menu to allow user to choose plot'''
    def __init__(self, master):
        super().__init__(master)
        self.transient(master)
        self.focus_set()
        self.title("Graph Selection")
        self.resizable(False, False)

        self.master = master

        def done():
            self.destroy()
            plt.close('all')
        self.protocol("WM_DELETE_WINDOW", done)

        tk.Button(self, text="Graph number of classes by department groups", command=lambda: self.check(1)).grid(row=0, padx=10,pady=10)
        tk.Button(self, text="Graph number of classes by department", command=lambda: self.check(2)).grid(row=0,column=1,padx=10,pady=10)

    def check(self, choice):
        if not os.path.isfile(os.path.join('Database', self.master.quarterSelection.get()).replace(' ','')+'_Classes.db'):
            tkmb.showerror("Invalid Quarter", "Quarter does not have a database created.", parent=self)
            return
        graphPercentClasses(self.master, choice)

class graphPercentClasses(tk.Toplevel):
    '''Graphs percentage of total offered courses by department group or department'''
    def __init__(self, master, choice):
        super().__init__(master)
        self.transient(master)
        self.resizable(False, False)

        quarter = master.quarterSelection.get()
        self.title(f"Overall Stats for {quarter}")

        conn = sqlite3.connect( os.path.join('Database', quarter.replace(' ','')+'_Classes.db') )
        cur = conn.cursor()

        titlechoices = {1: 'Offered Courses by Department Group', 2: 'Top 25 Departments by Popularity'}
        ylabelchoices = {1: 'Department Groups', 2: 'Departments'}

        plotchoices = {1:'''SELECT Groups.name, COUNT(Classes.crn) AS num_classes FROM Classes 
                                JOIN Departments ON Departments.id = Classes.department_id
                                JOIN Groups ON Departments.group_id = Groups.id 
                                GROUP BY Departments.group_id ORDER BY num_classes ASC''',

                       2: '''SELECT Departments.dep, COUNT(Classes.crn) AS num_classes FROM Classes 
                                JOIN Departments ON Departments.id = Classes.department_id 
                                GROUP BY Classes.department_id ORDER BY num_classes DESC LIMIT 25'''
                       }

        fig = plt.figure(figsize=(15, 8))
        plt.title(titlechoices[choice])
        plt.ylabel(ylabelchoices[choice])

        cur.execute(plotchoices[choice])
        data = cur.fetchall() # returns 24 tuples: ( groupname OR department, count of classes in group)

        ylabels = [i[0] for i in data]
        arr_numclasses = np.array([i[1] for i in data]) # num classes by department grouping

        cur.execute(plotchoices[1])
        total_classes = np.array([i[1] for i in cur.fetchall()]).sum()     #sum of total amount of classes in
        plt.xlabel(f'Percentage of Offered Courses (Percentage out of {total_classes} classes)')

        xAxis = (arr_numclasses/total_classes)*100

        if choice==2:
            ylabels = ylabels[::-1]
            xAxis = xAxis[::-1]

        plt.yticks(np.arange(len(ylabels)), ylabels, wrap=True, fontsize=8, verticalalignment='center')
        plt.barh(np.arange(len(ylabels)), xAxis, align='center')

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid(row=0, column=0)
        canvas.draw()
        conn.close()

class graphDepsPopularity(tk.Toplevel):
    '''Graphs department popularity based on number of Full or WL Classes out of total classes in department'''
    def __init__(self, master, quarter:str):
        super().__init__(master)
        self.transient(master)
        #self.focus_set()
        self.title(f"Department Comparison for {quarter}")
        self.geometry("+0+280")

        selection = [master.lb.get(i) for i in master.lb.curselection()]    # list of user selected department full names

        if len(selection) == 0: # if user chose to graph selection & selection list is empty
            self.destroy() # close self win - no graph
            tkmb.showerror("Error", "Please select 1 or more department group.", parent=master, icon='warning')
            return
        if len(selection) == 1:
            selection.append("This is not a real department")   # to enable casting the list as a tuple for SELECT

        cur = master.cur
        cur.execute(f'''SELECT Departments.abbrv, COUNT(Classes.crn) AS num_classes FROM Classes 
                    JOIN Departments ON Departments.id = Classes.department_id 
                    WHERE (Classes.status = 'Full' OR Classes.status = 'WL') 
                    AND Departments.dep IN {tuple(selection)} GROUP BY Classes.department_id ORDER BY num_classes ASC''')
        data = cur.fetchall() # returns list of tuples: [ ('department abbrv, num of classes that are full or wl)

        cur.execute(f'''SELECT Departments.abbrv, COUNT(Classes.crn) AS num_classes FROM Classes 
                    JOIN Departments ON Departments.id = Classes.department_id 
                    WHERE Departments.dep IN {tuple(selection)} GROUP BY Classes.department_id''')
        fullData = cur.fetchall()
        num_total_classes = np.array([ tup[1] for tup in fullData ])

        depCount = {k[0]:0 for k in fullData}
        for tup in data:
            depCount[tup[0]] = tup[1]

        xlabels = list(depCount.keys())
        arr_num_popular_classes = np.array(list(depCount.values()))  # num of Full or WL classes

        yData = (arr_num_popular_classes / num_total_classes)*100

        fig = plt.figure(figsize=(10, 8))
        plt.xticks(np.arange(len(xlabels)), xlabels, wrap=True, fontsize=8, horizontalalignment='center') # verticalalignment='center', rotation=45
        plt.bar(np.arange(len(xlabels)), yData, align='center')
        plt.title('Selected Departments Popularity')
        plt.xlabel('Departments')
        plt.ylabel("Number of Full or WL Classes (Percentage)")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid(row=0, column=0)
        canvas.draw()

class graphCoursePopularity(tk.Toplevel):
    '''Graphs course popularity based on Full or WL classes out of total classes of the same type'''
    def __init__(self, master, cur, tag_selection:list):
        super().__init__(master)
        self.transient(master)
        self.title("Course Comparison")

        # selection = list of user selected class tag names
        if len(tag_selection) == 0:
            self.destroy()
            tkmb.showerror("Error", "Please select between 1 and 20 courses", parent=master, icon='warning')
        if len(tag_selection) > 20: # no more than 20 selections
            self.destroy() # close self win - no graph
            tkmb.showerror("Error", "Please select between 1 and 20 courses", parent=master, icon='warning')
            return
        if len(tag_selection) == 1:
            tag_selection.append("Not a real course")   # enables IN tuple sql command

        classCount = {k:0 for k in tag_selection}

        cur.execute(f'''SELECT Classes.tag, COUNT(Classes.crn), Classes.status FROM Classes 
                                WHERE (Classes.status = 'Full' OR Classes.status = 'WL')
                                AND Classes.tag IN {tuple(tag_selection)}
                                GROUP BY Classes.tag''')
        num_full_classes = cur.fetchall() # returns [ (tag, count of full or wl classes) ]
        xlabels = tag_selection

        for tup in num_full_classes:
            classCount[tup[0]] = tup[1]

        arr_num_popular_classes = np.array(list(classCount.values()))  # num of Full or WL classes

        cur.execute(f'''SELECT COUNT(Classes.crn) FROM Classes 
                                WHERE Classes.tag IN {tuple(tag_selection)}
                                GROUP BY Classes.tag''')
        num_total_classes = np.array([i[0] for i in cur.fetchall()])

        yData = np.divide(arr_num_popular_classes, num_total_classes)*100

        fig = plt.figure(figsize=(8, 6))
        plt.xticks(np.arange(len(xlabels)), xlabels, wrap=True, fontsize=8, horizontalalignment='center')
        plt.bar(np.arange(len(xlabels)), yData, align='center')
        plt.title('Course Popularity')
        plt.xlabel('Courses')
        plt.ylabel("Number of Full or WL Classes (Percentage)")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid(row=0, column=0)
        canvas.draw()
        master.focus_set()

if __name__ == "__main__":
    Master().mainloop()