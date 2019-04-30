"""
    Gradebook Flask app file. Used to host website, manage server side computations.
"""
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_fresh, login_required, login_user, LoginManager, logout_user
from flask_sqlalchemy import SQLAlchemy
from database.databaseConfig import testDBEndPoint, prodDBEndPoint
from database.appsSharedModels import *
from datetime import datetime
from time import sleep

#app set up
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = testDBEndPoint
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 200
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = False
app.secret_key = "E*2kd+2sMPSt<VgN,26y!"
login_manager = LoginManager()
login_manager.login_view = 'https://is668projectgradebook.pythonanywhere.com/login'
login_manager.init_app(app)
db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@login_manager.user_loader
@dbQuery
def load_user(username):
    return User.query.filter_by(user_name=username).first()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', error=False)
    else:
        user = load_user(request.form['username'])
        if not user or not user.check_password(request.form['password']):
            return render_template('login.html', error=True)
        else:
            login_user(user)
            return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    return 'place holder for logout'

@app.route('/changePassword', methods=['GET', 'POST'])
@login_required
def changePassword():
    return 'place holder for changePassword'

@app.route('/home', methods=["GET", "POST"])
@login_required
def homeView():
    return render_template('home.html')

@app.route('/class', methods=["GET", "POST"])
@login_required
def classView():
    return 'place holder for classView'

@app.route('/gradebook', methods=["GET", "POST"])
@login_required
def gradebookView():
    return 'place holder for gradebookView'

@app.route('/student', methods=["GET", "POST"])
@login_required
def studentView():
    majorData = dbQuery(Major.query.order_by('major_name').all())
    if request.method == "GET":
        if request.args.get('student_id'):
            studentData = getStudentData(request.args.get('student_id'))
        else:
            studentData = Student()
        return render_template('student.html', 
                               studentData=studentData,
                               students=studentData.getStudents(),
                               majorData=majorData)

    if request.form['send'] == "AddStudent":
        insertRow(Student,
                  first_name=request.form['first_name'],
                  last_name=request.form['last_name'],
                  email_address=request.form['email_address'],
                  major_id=request.form['major_id'])

    elif request.form['send'] == "UpdateStudent":
        updateRow(Student, int(request.form['student_id']), 
                  first_name=request.form['first_name'],
                  last_name=request.form['last_name'],
                  email_address=request.form['email_address'],
                  major_id=request.form['major_id'])

    elif request.form['send'] == "DeleteStudent":
        deleteRow(Student, int(request.form['student_id']))
    return redirect(url_for('studentView'))

