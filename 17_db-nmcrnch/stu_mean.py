#Bob (Roster: Jerry Ye and Ahnaf Hasan)
#SoftDev pd07
#K #17: Average
#2018-10-08

import csv, sqlite3

data_file = "Database.db" #DO NOT CHANGE UNLESS YOU CHANGE EVERY OTHER OCCURENCE
courses = "./raw/courses.csv"
students = "./raw/peeps.csv"

db = sqlite3.connect(data_file)
c = db.cursor()

def makeTables(file_name:str, table_name:str, first, fType:str, second, sType:str, third, tType:str):
    command = "CREATE TABLE {} ( {} {}, {} {}, {} {} )".format(table_name, first, fType.upper(), second, sType.upper(), third, tType.upper() )  #build SQL stmt, save as string
    c.execute(command) #run SQL statement
    with open(file_name) as curr_file:
        reader = csv.DictReader(curr_file)
        for row in reader:
            fir = row[first] #everything in the column before the first delimiter is probably called 'code'
            sec = row[second] #same reasoning as above
            thi = row[third] #same reasoning as above above
            command = 'INSERT INTO {} VALUES(\"{}\", \"{}\", \"{}\")'.format(table_name, fir, sec, thi) #" " are needed so put in escape chars
            c.execute(command)

makeTables(courses, "courses", "code", "text", "mark", "integer", "id", "INTEGER" )
makeTables(students, "peeps", "name", "text", "age", "integer", "id", "integer")

command = "CREATE TABLE namesWithGrades (name INTEGER, id INTEGER, mark INTEGER)" #creates table that stores names, id, and grade. used later for names
c.execute(command)
command = "INSERT INTO namesWithGrades SELECT name, peeps.id, courses.mark FROM courses, peeps WHERE peeps.id = courses.id" #INSERT INTO <tabl1> SELECT <col> FROM <tabl2>
                                                                                                                            #copies table 2 into table 1
c.execute(command)


command = "CREATE TABLE peeps_avg (id INTEGER, average REAL)" #required by hw
c.execute(command)

c.execute("SELECT id, mark FROM namesWithGrades")
list_of_grades = c.fetchall() #Fetchall() returns a list of tuples (in this case, a duo) from a previous SELECT ... FROM ... call
print("Student grades in terms of (id, mark) is shown below:")
print(*list_of_grades) #iterates through list to print each stuff
#string = dict(list_of_grades) TEST

dict_average = {} #stores id and average in form of dict_average[id] = average

def insertIntoAvg():
    for iD in dict_average: #key is id, value is average
        command = "INSERT INTO peeps_avg VALUES(?, ?)" #Question marks(?) later replaced with tuple
        avgIdTuple = (iD, dict_average[iD],) #makes tuple composed of the id and average for next line
        c.execute(command, avgIdTuple) #executing with params
def avgCrunch():
    run_sum = 0 #running sum of current id
    nums = 0 #number of classes curr id is enrolled in, resets when new id appears
    for item in list_of_grades:
        #print(dict_average, run_sum, nums) TEST
        if item[0] not in dict_average: #item is a tuple and has indexing. Fills dict_average with id and average
            if nums != 0: #can prob remove, don't want to in case it breaks everything. Supposed to avoid division by zero(0)
                dict_average[list(dict_average.keys())[-1]] = run_sum / nums #list(dict_average.keys())[-1] returns the last key in dictionary. Turns dictionary temp into list
                                                                            #and uses Python's -1 indexing to get last key. Allows the value to be overwritten by the average
            run_sum = item[1] #reset run_sum to the grade of the next id
            nums = 1 #curr id exists, therefore enrolled in at least 1 class
            dict_average[item[0]] = item[1] #dict_average[id] = average
        else:
            run_sum += item[1] #curr id is in dictionary, so add the grades to the running sum
            nums += 1 #classes enrolled in increases by 1
    dict_average[list(dict_average.keys())[-1]] = run_sum / nums #last item is untouched. This makes up for it. Removing causes incorrect data
    insertIntoAvg()
avgCrunch()
#Prints the IDs and averages of the students
print("\n\nStudent averages shown in terms of (id, average) below:")
for key in dict_average:
    print("Id:", key, "\nAverage:", dict_average[key], "\n")
#print(dict_average) TEST



command = "CREATE TABLE nameIdAverage (name TEXT, id INTEGER, average REAL)"
c.execute(command)
command = "INSERT INTO nameIdAverage SELECT name, peeps_avg.id, peeps_avg.average FROM namesWithGrades, peeps_avg WHERE peeps_avg.id = namesWithGrades.id"
c.execute(command) #all the names, ids, and averages in one table


def showAll():
    displayList = []
    c.execute("SELECT * FROM nameIdAverage")
    display = c.fetchall() #returns list
    for item in display:
        if item in displayList: #duplicate, move on
            continue
        else:
            displayList.append(item) #append cause new item
    print(*displayList)
def addToTable(code:str, mark:int, id:int):
    if id not in dict_average:
        print("That person does not exist, please try again")
    else:
        command = "INSERT INTO courses VALUES({}, {}, {})".format("\"" + code + "\"", mark, id)
        c.execute(command)
        avgCrunch()


showAll()

addToTable("systems", 95, 10)




db.commit()
db.close()