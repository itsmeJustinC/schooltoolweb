#######################################################################################
# This program awaits a request from a website then, given the proper credentials,
# will get the grades from our school grading system and return them to the requesting
# website so that it can be displayed nicely for the user
#######################################################################################

# Imports of various libraries that run the Flask server, webdriver, Timers and CORS
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Timer
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Translate the actual quarter to the value used on schooltool
QUARTERS = {
  "1" : "213",
  "2" : "212",
  "3" : "211",
  "4" : "210"
}

# The URL that selenium get pointed to (The schooltool website)
URL = "https://schooltool.pinebushschools.org/schooltoolweb/"

# This dictionary is what holds the cached users info fo five minutes 
content_dict = {}

# This function deletes a users info from "content_dict" if it is present in the dictionary
# Otherwise it prints "No cached data with that username"
def delete_content(username):
  if (username in content_dict):
    del content_dict[username]
    print("Deleted " + username + " from the list")
  else:
    print("No cached data with that username")

# This instantiates the flask app
app = Flask(__name__)
# This activates cross origin resource sharing for the flask app so that the
# front end can make requests to the flask app
CORS(app)

# This sets the chrome options for the webdriver
# It does a couple of things
# 1)It puts the webdriver into headless mode to save a little time with not having to display
# the webbrowser since it wouldn't been seen by the user anyway
# 2)It tells the webdriver not to load images because that takes up a significant amount of time
# when running the program (About 10 seconds which is alot!).
def set_chrome_options():
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  prefs = {"profile.managed_default_content_settings.images": 2}
  chrome_options.add_experimental_option("prefs", prefs)
  return chrome_options

# This function takes in the username, password, and quarter as parameters and then uses
# these to sign into the user schooltool and extract their averages in each of their
# classes for the specified quarter in a dictionary
def get_grades(url, username, password, quarter):
  driver = webdriver.Chrome(chrome_options=set_chrome_options())
  
  driver.get(url)
  
  driver.find_element_by_id('Template1_MenuList1_TextBoxUsername').send_keys(username)
  driver.find_element_by_id('Template1_MenuList1_TextBoxPassword').send_keys(password)
  driver.find_element_by_name("Template1$MenuList1$ButtonLogin").click()
  
  driver.find_element_by_xpath('//*[@title="View Student Record"]').click()


  driver.find_element_by_id('Template1_Control0_TabHeader2_Menutabs1_MenuTabGrades').click()
  select = Select(driver.find_element_by_name('Template1$Control0$StudentGradesView1$ViewDropDownList'))
  select.select_by_value('3')

  selectQuarter = Select(driver.find_element_by_name('Template1$Control0$StudentGradesView1$MarkingPeriodDropDown'))
  selectQuarter.select_by_value(quarter)

  soup = BeautifulSoup(driver.page_source, "html.parser")
  table = soup.find('table', id="Template1_Control0_StudentGradesView1_GradeTypeMultiView_StudentGradesMPAvgView_DataGrid1")
  tr = table.tbody.find_all('tr', class_=['DataGridItemStyle', 'DataGridAlternateItemStyle'])
  return_grades = {}
  for i in tr:
    course = i.td.span.text.split(',')[0]
    grade = i.td.next_sibling.span.text
    return_grades[course] = grade
  
  driver.quit()
    
  return return_grades

# Given a username and quarter as parameters, this function adds the user's info to the content dictionary
# So that it could be retrieved very fast if the user requsted them again in the span of five minutes
def add_to_content_dict(username, quarter):
  username_dict = username + quarter
  content_dict[username_dict] = return_grades
  print("Added " + username + " to the list")
  Timer(300, delete_content, [username_dict]).start()
  return jsonify(return_grades)

# This is a function decorator that specifies the route that the flask server is located at
# it also specifies the methods in which it can be accessed. This route can only be accessed via a POST
# request and couldn't be accessed typing its URL into google
@app.route('/', methods=["POST"])
# This function dictates what to do when a POST request is received
def index():
  # This bit gets the username, password, and quarter number of the user
  # The if statement checks if the user has cached data that could be returned instead of running
  # the get_grades function which takes a little bit of time
  json = request.get_json()
  username = json['username']
  passwd = json['password']
  quarter = QUARTERS[json['quarter']]
  if (username + quarter in content_dict):
    return content_dict[username + quarter]
  
  # Return the grades of the user as a JSON object for the front end to use
  Timer(300, delete_content, [username])
  return jsonify(get_grades(URL, username, passwd, quarter))

# This handles a 500 error which could occur if the username and password is incorrect
# If this happens it instead returns a 401 error that is returned to the front end
@app.errorhandler(500)
def internal_server_error(error):
  return "401 error", 401

# This just runs the program
if __name__ == "__main__":
  app.run(debug=True, use_reloader=True)
