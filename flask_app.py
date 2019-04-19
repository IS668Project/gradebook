
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

testDBEndPoint ='mysql://IS668ProjectGrad:youGetAnA2019!@IS668ProjectGradeBook.mysql.pythonanywhere-services.com/IS668ProjectGrad$gradebook_test'
prodDBEndPoint = 'mysql://IS668ProjectGrad:youGetAnA2019!@IS668ProjectGradeBook.mysql.pythonanywhere-services.com/IS668ProjectGrad$gradebook'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = testDBEndPoint
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 200
db = SQLAlchemy(app)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

