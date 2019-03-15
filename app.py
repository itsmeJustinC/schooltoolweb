from flask import Flask

app = Flask(__name__)
@app.route('/')
def index():
  return "<h1>hello</h1>"
 

PORT = os.environ.get("PORT", 80)
app.run(host="localhost", port=PORT)
