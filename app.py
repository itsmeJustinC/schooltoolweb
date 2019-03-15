from flask import Flask
from selenium import webdriver




app = Flask(__name__)
@app.route('/')
def index():
  driver = webdriver.Firefox()
  driver.get("https://google.com")
  return driver.title
 
if __name__ == "__main__":
  app.run(debug=True, use_reloader=True)
