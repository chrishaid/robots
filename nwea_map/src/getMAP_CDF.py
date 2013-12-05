"""
Python Script to pull CDF zip file from NWEA's MAP reporting site
    Need to authenticate to , then navigate to export page and save file with a an appropriate name
"""

print("Loading modules . . . ")
import mechanize
import cookielib
import shutil
import os
import zipfile
import pyodbc
from datetime import datetime
import subprocess


# Browser
print("Instantiating mechanize browser . . .")
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
#br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Want debugging messages?
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# Open NWEAs's authenticate webpage
print("Navigating to NWEA Login PAge . . .")
r=br.open('https://pdx-map01.mapnwea.org/admin')

# Select form
# br.select_form(nr=0])
br.select_form(name='loginForm')

#Add authentication details and submit
br.form['password']='haiKIPP1'
br.form['username']='chaid@kippchicago.org'
print("Authenticating . . .")
br.submit()

#navigate to csv page and save file
r=br.open('https://pdx-map01.mapnwea.org/report/home/map')

#find download url
cdf_link = br.find_link(text_regex='Download')

cdf_url='https://pdx-map01.mapnwea.org'+cdf_link.url

print("Retriving CDF . . . ")
f=br.retrieve(cdf_url)#f is path to downloaded file

# Figure out year and season
def getSeasonYear():
    m =  datetime.now().month
    y = datetime.now().strftime('%y')
    if m in range(8,11):
        return "Fall" + y
    elif m in [range(1,3),12]:
        return "Winter" + y
    else:
        return "Spring" + y

sy = getSeasonYear()


#Now to save the file
#get establish destination  directory
print("Unzipping CDF archive file . . . ")
dest_dir=os.getcwd()+'/data/' + sy + '/NWEA_CDF_'+datetime.now().strftime('%y%m%d')

# Test if season directory 
if not os.path.isdir(dest_dir):
    os.makedirs(dest_dir)


# Move and rename file in one line
zf=zipfile.ZipFile(f[0])
zf.extractall(dest_dir)



# TO DO
# 1. run the bash script to get files ready for upload
print("Running data prep script.")

nwea_rel_dir = os.path.relpath(dest_dir,os.getcwd())


for fn in os.listdir(nwea_rel_dir):
    subprocess.call(["./map_cdf_prep_2.sh", nwea_rel_dir + "/" +fn ])



# Concatonate table names and season-year
t_assessments = "tblAssessmentResults" + sy
t_students = "tblStudentBySchool" + sy
t_classes = " tblClassAssignments" + sy
t_programs = "tblProgramAssignments" + sy




# 2. Establish odbc connection with MySQL
print("Connecting to MySQL Testing Database . . . ")
mapcon = pyodbc.connect('DSN=kippchidata; local_infile=1;')

cursor = mapcon.cursor()

# 3. Construct create table and instert table queries
# Create DROP Table query strings

print("Constructing queries . . . ")
q_drop_assessments = "DROP TABLE IF EXISTS " + t_assessments + ";"
q_drop_students = "DROP TABLE IF EXISTS " + t_students + ";"
q_drop_classes = "DROP TABLE IF EXISTS " + t_classes + ";"
q_drop_programs = "DROP TABLE IF EXISTS " + t_programs + ";"

#Create CREATE TABLE query Strings
# tblAssessments
q_create_assessments = """
    CREATE TABLE """ + t_assessments + """ (
	TermName VARCHAR(30), 
	StudentID INT, 
	SchoolName VARCHAR(100), 
	MeasurementScale VARCHAR(30),
	Discipline VARCHAR(11),
	GrowthMeasureYN VARCHAR(5), 
	TestType VARCHAR(20),
	TestName VARCHAR(100),
	TestID INT,
	TestStartDate VARCHAR(10),
	TestDurationInMinutes INT,
	TestRITScore SMALLINT(3),
	TestStandardError REAL(3,1),
	TestPercentile INT,
	TypicalFallToFallGrowth INT,
	TypicalSpringToSpringGrowth INT,
	TypicalFallToSpringGrowth INT,
	TypicalFallToWinterGrowth INT,
    RITtoReadingScore INT,
	RITtoReadingMin INT,
	RITtoReadingMax INT,
	Goal1Name VARCHAR(50),
	Goal1RitScore INT,
	Goal1StdErr REAL(3,1),
	Goal1Range VARCHAR(7),
	Goal1Adjective VARCHAR(2),
	Goal2Name VARCHAR(50),
	Goal2RitScore INT,
	Goal2StdErr REAL(3,1),
	Goal2Range VARCHAR(7),
	Goal2Adjective VARCHAR(2),
	Goal3Name VARCHAR(50),
	Goal3RitScore INT,
	Goal3StdErr REAL(3,1),
	Goal3Range VARCHAR(7),
	Goal3Adjective VARCHAR(2),
	Goal4Name VARCHAR(50),
	Goal4RitScore INT,
	Goal4StdErr REAL(3,1),
	Goal4Range VARCHAR(7),
	Goal4Adjective VARCHAR(2),
	Goal5Name VARCHAR(50),
	Goal5RitScore INT,
	Goal5StdErr REAL(3,1),
	Goal5Range VARCHAR(7),
	Goal5Adjective VARCHAR(2),
	Goal6Name VARCHAR(50),
	Goal6RitScore INT,
	Goal6StdErr REAL(3,1),
	Goal6Range VARCHAR(7),
	Goal6Adjective VARCHAR(2),
	Goal7Name VARCHAR(50),
	Goal7RitScore INT,
	Goal7StdErr REAL(3,1),
	Goal7Range VARCHAR(7),
	Goal7Adjective VARCHAR(2),
	Goal8Name VARCHAR(50),
	Goal8RitScore INT,
	Goal8StdErr REAL(3,1),
	Goal8Range VARCHAR(7),
	Goal8Adjective VARCHAR(2),
	TestStartTime TIME,
	PercentCorrect INT,
	ProjectedProficiency VARCHAR(17)
	);"""


# Students
q_create_students = """
    CREATE TABLE """ + t_students + """ (
	TermName VARCHAR(30),
	DistrictName VARCHAR(50),
	SchoolName VARCHAR(50),
	StudentLastName VARCHAR(50),
	StudentFirstName VARCHAR(50),
	StudentMI VARCHAR(2),
	StudentID INT,
	StudentDateOfBirth VARCHAR(10),
	StudentEthnicGroup VARCHAR(20),
	StudentGender VARCHAR(1),
	Grade INT);"""

# Classes
q_create_classes = """
    CREATE TABLE """ + t_classes + """ (
	TermName VARCHAR(30),
	StudentID INT,
	SchoolName VARCHAR(50),
	ClassName VARCHAR(50),
	TeacherName VARCHAR(50)
	);"""

# Programs
q_create_programs = """
    CREATE TABLE """ + t_programs + """ (
	TermName VARCHAR(30),
	StudentID INT,
	Program VARCHAR(50)
	);"""


# INFILE Data

print("Loading data into database  . . .")
#def load_data(infile, outtable) :
#    q_load="""
#    LOAD DATA LOCAL INFILE '""" + infile + """'
#	IGNORE INTO TABLE """ + outtable + """
#	FIELDS TERMINATED BY ','
#	;"""
#    cursor.execute(q_load)
#    mapcon.commit()

def load_data(infile, outtable):
    load_text="""
        mysql -h ec2-54-245-118-235.us-west-2.compute.amazonaws.com -u chaid --password=haiKIPP1 -D db_kippchidata --ssl-key=/home/ubuntu/.ssh/kippchidatakey.pem -e\"LOAD DATA LOCAL INFILE '"""+infile+"""' INTO TABLE """+outtable+""" FIELDS TERMINATED BY ',';\";
        """
    subprocess.call(load_text, shell=True)



# 4. Execute queries
print("Uploading Assessment Results to Database . . .")
cursor.execute(q_drop_assessments)
mapcon.commit()
cursor.execute(q_create_assessments)
mapcon.commit()
load_data(nwea_rel_dir + "/AssessmentResults_loaddata.csv", t_assessments)

print("Uploading Students to Database . . .")
cursor.execute(q_drop_students)
mapcon.commit()
cursor.execute(q_create_students)
mapcon.commit()
load_data(nwea_rel_dir + "/StudentsBySchool_loaddata.csv", t_students)

print("Uploading Classes to Database . . .")
cursor.execute(q_drop_classes)
mapcon.commit()
cursor.execute(q_create_classes)
mapcon.commit()
load_data(nwea_rel_dir + "/ClassAssignments_loaddata.csv", t_classes)

print("Uploading Programs Assignments to Database . . .")
cursor.execute(q_drop_programs)
mapcon.commit()
cursor.execute(q_create_programs)
mapcon.commit()
load_data(nwea_rel_dir + "/ProgramAssignments_loaddata.csv", t_programs)



print("Done!")
# 5. Clean_up files


