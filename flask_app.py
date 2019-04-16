
# A very simple Flask Hello World app for you to get started with...
# this is a test
# this is john's test
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

