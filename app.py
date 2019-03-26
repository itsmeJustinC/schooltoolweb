from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Timer
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


QUARTERS = {
  "1" : "155",
  "2" : "154",
  "3" : "153",
  "4" : "152"
}

URL = "https://schooltool.pinebushschools.org/schooltoolweb/"

content_dict = {}

def delete_content(username):
  if (username in content_dict):
    del content_dict[username]
    print("Deleted " + username + " from the list")
  else:
    print("No cached data with that username")

app = Flask(__name__)
CORS(app)

def set_chrome_options():
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  prefs = {"profile.managed_default_content_settings.images": 2}
  chrome_options.add_experimental_option("prefs", prefs)
  return chrome_options

def get_grades(url, username, password, quarter):
  driver = webdriver.Chrome(chrome_options=set_chrome_options())
  
  driver.get(url)
  
  driver.find_element_by_id('Template1_MenuList1_TextBoxUsername').send_keys(username)
  driver.find_element_by_id('Template1_MenuList1_TextBoxPassword').send_keys(password)
  driver.find_element_by_name("Template1$MenuList1$ButtonLogin").click()
  
  driver.find_element_by_name('Template1$Control0$IconButtonSelect').click()


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

def add_to_content_dict(username, quarter):
  username_dict = username + quarter
  content_dict[username_dict] = return_grades
  print("Added " + username + " to the list")
  Timer(300, delete_content, [username_dict]).start()
  return jsonify(return_grades)

@app.route('/', methods=["GET", "POST"])
def index():
  json = request.get_json()
  username = json['username']
  passwd = json['password']
  quarter = QUARTERS[json['quarter']]
  if (username + quarter in content_dict):
    return content_dict[username + quarter]
  
  return jsonify(get_grades(URL, username, passwd, quarter))

@app.errorhandler(500)
def internal_server_error(error):
  return "401 error", 401


if __name__ == "__main__":
  app.run(debug=True, use_reloader=True)
