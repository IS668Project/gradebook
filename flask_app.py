
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from database.databaseConfig import testDBEndPoint, prodDBEndPoint


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = testDBEndPoint
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 200
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

