
from flask import Flask, flash, redirect, render_template, request, session, url_for
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user = users.query.filter_by(user_name=request.args.get('username')).first
        if user.check_password(request.args.get('password')):
            session['logged_in'] = True
            #redirect to user dashboard here
        else:
            flash('Incorrect password, please try again')

@app.route('/login', methods=['GET', 'POST'])
def checkLogin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

@app.route('/student', methods=["GET", "POST"])
def studentView():
    checkLogin()
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

