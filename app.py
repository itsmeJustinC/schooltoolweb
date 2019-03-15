from flask import Flask

app = Flask(__name__)
@app.route('/')
def index():
  return "<h1>hello</h1>"
 

app.run(host="localhost", debug=True, use_reloader=True)
