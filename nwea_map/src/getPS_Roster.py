"""
Python script to access PowerSchool Oracle DB and pull the complete all time roster
 of students that have ever attended a school in KIPP Chicago.  This script uses 
 the pyodbc module to connect to both the PowerSchool Oralce database and the 
 kippchidata MySQL database. Roster is pulled down from PowerSchool and saved in a list.
 A table is created matching the list (and dropped if already extant) and the roster
 is then inserted into the new table. 
"""

print("Loading modules . . . ")
import pyodbc

# Establish connection to PowerSchool
print("Establishing connection to PowerSchool . . . ")
ps_con = pyodbc.connect("DSN=PS")

# Establish connection to kippchidata
print("Establishing connectino to kippchidata . . . ")
kcd_con = pyodbc.connect("DSN=kippchidata")

# Instantiate cursors
print("Instantiating cursors . . . ")

ps_cur = ps_con.cursor()
kcd_cur = kcd_con.cursor()

# Get roster from PowerSchool
print("Getting current roster from PowerSchool . . . ")

ps_roster = ps_cur.execute("""
	SELECT	student_number,
		last_name,
		first_name,
		dob,
		grade_level,
		enroll_status,
		schoolid
	FROM	students;
	""")
roster = ps_roster.fetchall()

# Load roster to kippchi data
print("Load roster to kippchi data . . . ")

print("Drop tbl_PS_Roster_All if it exists . . . ")

kcd_cur.execute("DROP TABLE IF EXISTS tbl_PS_Roster_All")
kcd_cur.commit()

print("Create tbl_PS_Roster_All . . . ")

kcd_cur.execute("""
	CREATE TABLE tbl_PS_Roster_All (
		StudentID INT,
		StudentLastName VARCHAR(50),
		StudentFirstName VARCHAR(50),
		StudentDateofBirth VARCHAR(10),
	        Grade INT,
		Enroll_Status INT,
		SchoolID INT
		);
	""")
kcd_cur.commit()

# Upload roster
print("Insert roster into tbl_PS_Roster_All . . . ")
kcd_cur.executemany("INSERT INTO tbl_PS_Roster_All VALUES (?,?,?,?,?,?,?)", roster)
kcd_cur.commit()

print("Data transfer between PowerSchool and kippchitest complete!")
