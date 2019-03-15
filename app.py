from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options




app = Flask(__name__)
@app.route('/')
def index():
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  driver = webdriver.Chrome(chrome_options=chrome_options)
  driver.get("https://google.com")
  return driver.title
 
if __name__ == "__main__":
  app.run(debug=True, use_reloader=True)
