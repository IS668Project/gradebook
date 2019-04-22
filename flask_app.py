
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from database.databaseConfig import testDBEndPoint, prodDBEndPoint
from database.appsSharedModels import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = testDBEndPoint
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 200
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/student', methods=["GET", "POST"])
def studentView():
    if request.method == "GET":
        majorData = majors.query.order_by(majors.major_name.desc()).all()
        if request.args.get('student_id'):
            studentData = students.query.filter_by(student_id=request.args.get('student_id')).first()
        else:
            studentData = students()
        return render_template('student.html', studentData=studentData, majorData=majorData)
    else:
        requestContents.append(request.form['contents'])
        return redirect(url_for('students'))

