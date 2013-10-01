"""
Python Script to pull  data  from Kickboard in csv format
    Need to authenticate to Kickbordm, then navigate to export page and save file with a an appropriate name
    An R script should then be called which culls that last two weeks data and reformat per Kate Mazurek's
    Two lines per student (one line for negative paycheck deductions and another for postive create points (well
    these acutally have zero value)
"""

import mechanize
import cookielib
import shutil
import os
import subprocess
from datetime import datetime

# Browser
print('Setting up browser and cookie jars . . . ')
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
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

print('Opening Kickboard\'s authentication page')
# Open Kickboard's authenticate webpage
r=br.open('https://kippcreate.kickboardforteachers.com')

# Select form
br.select_form(nr=0)

#Add authentication details and submit
print('Authenticating . . . ')
br.form['user_password']='haiKIPP1'
br.form['username']='chaid'
br.submit()
print('Authenticated!')

#navigate to csv page and save file
print('Navigating to and retrieving culture analysis export . . . ')
r=br.open('https://kippcreate.kickboardforteachers.com/culture-analysis/index')
f=br.retrieve('https://kippcreate.kickboardforteachers.com/culture-analysis/export/')[0] #f is path to downloaded file

#Now to save the file
#get current working directory
dest_dir=os.getcwd()

#use to make file name
dest_file=dest_dir+'/culture-analysis_'+datetime.now().strftime('%y%m%d')+'.csv'

# Move and rename file in one line
print('renaming and saving!')
os.rename(f,dest_file)


#Now run R process to create Kate's preferred output
cmd = ['Rscript', dest_dir+'/Kickboard_long_to_2_row_wide_working.R', datetime.now().strftime('%y%m%d')]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
for line in proc.stdout:
        print line

proc.wait()
print proc.returncode

#Finally need to email KB file to recipient
kb_file=dest_dir+'/KB_'+datetime.now().strftime('%y%m%d')+'.csv'

print('Mailing ' +kb_file + ' . . . ')
mail_cmd = 'echo "Here\'s this week\'s KB data!" | mutt -a ' + kb_file + ' -s "Kickboard Data" -c chaid@kippchicago.org -- kmazurek@kippchicago.org'

subprocess.call(mail_cmd, shell=True)
print('Athentication, download, transformation, and mailing complete!')
