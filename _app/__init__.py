from flask import Flask

app = Flask(__name__)

@app.route('/')
def app():
  return {'message': 'Hello world'}, 200
