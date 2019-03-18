from flask import Flask, request
from flask import jsonify
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

quarter = "3"
# username = "Pb272098"
# passwd = "Jan010203"

app = Flask(__name__)
@app.route('/', methods=["GET", "POST"])
def index():
  json = request.get_json()
  username = json['username']
  passwd = json['password']
  
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  prefs = {"profile.managed_default_content_settings.images": 2}
  chrome_options.add_experimental_option("prefs", prefs)
  
  driver = webdriver.Chrome(chrome_options=chrome_options)
  
  driver.get("https://schooltool.pinebushschools.org/schooltoolweb/")
  
  driver.find_element_by_id('Template1_MenuList1_TextBoxUsername').send_keys(username)
  driver.find_element_by_id('Template1_MenuList1_TextBoxPassword').send_keys(passwd)
  driver.find_element_by_name("Template1$MenuList1$ButtonLogin").click()
  
  driver.find_element_by_name('Template1$Control0$IconButtonSelect').click()


  driver.find_element_by_id('Template1_Control0_TabHeader2_Menutabs1_MenuTabGrades').click()
  select = Select(driver.find_element_by_name('Template1$Control0$StudentGradesView1$ViewDropDownList'))
  select.select_by_value('3')

  selectQuarter = Select(driver.find_element_by_name('Template1$Control0$StudentGradesView1$MarkingPeriodDropDown'))
  selectQuarter.select_by_value('15'+ quarter)

  soup = BeautifulSoup(driver.page_source, "html.parser")
  table = soup.find('table', id="Template1_Control0_StudentGradesView1_GradeTypeMultiView_StudentGradesMPAvgView_DataGrid1")
  tr = table.tbody.find_all('tr', class_=['DataGridItemStyle', 'DataGridAlternateItemStyle'])
  return_grades = {}
  for i in tr:
    course = i.td.span.text.split(',')[0]
    grade = i.td.next_sibling.span.text
    return_grades[course] = grade
      
  driver.quit()
  return jsonify(return_grades)

@app.errorhandler(500)
def internal_server_error(error):
  return "401 error", 401


if __name__ == "__main__":
  app.run(debug=True, use_reloader=True)
