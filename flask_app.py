"""
    Gradebook Flask app file. Used to host website, manage server side computations.
"""
import json
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
@login_required
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
    logout_user()
    return redirect(url_for('login'))

@app.route('/changePassword', methods=['GET', 'POST'])
@login_required
def changePassword():
    return 'place holder for changePassword'

@app.route('/home', methods=["GET", "POST"])
@login_required
def homeView():
    return render_template('home.html')

@app.route('/contact_information', methods=["GET", "POST"])
@login_required
def contact_informationView():
    return render_template('contact_information.html')

@app.route('/training', methods=["GET", "POST"])
@login_required
def trainingView():
    return render_template('training.html')

@app.route('/class', methods=["GET", "POST"])
@login_required
def classView():
    if request.method == "GET":
        return render_template('class.html',
                               classes=getClasses())
    elif request.form['send'] == "AddClass":
        insertRow(Class, class_name=request.form['class_name'],
                  class_abbrv=request.form['class_abbrv'],
                  class_description=request.form['class_description'],
                  class_semester=request.form['class_semester'],
                  class_year=request.form['class_year'])
    elif request.form['send'] == "UpdateClass":
        updateRow(Class, int(request.form['class_id']),
                  class_name=request.form['class_name'],
                  class_abbrv=request.form['class_abbrv'],
                  class_description=request.form['class_description'],
                  class_semester=request.form['class_semester'],
                  class_year=request.form['class_year'])
    elif request.form['send'] == "DeleteClass":
        deleteRow(Class, int(request.form['class_id']))
    return redirect(url_for('classView'))

@app.route('/gradebook', methods=["GET", "POST"])
@login_required
def gradebookView():
    return 'place holder for gradebookView'

@app.route('/student', methods=["GET", "POST"])
@login_required
def studentView():
    majorData = dbQuery(Major.query.order_by('major_name').all())
    if request.method == "GET":
        return render_template('student.html',
                               students=getStudents(),
                               majorData=majorData)

    elif request.form['send'] == "AddStudent":
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

@app.route('/assignments', methods=["GET", "POST"])
@login_required
def assignmentView(classId=''):
    if request.method == "GET":
        data = getClassAssignments(request.args.get('class_id'))
        return render_template('classAssignments.html', assignments=data)
    elif request.form['send'] == "AddAssignment":
        insertRow(Assignment,
                  class_id=int(request.form['class_id']),
                  name=request.form['assignment_name'],
                  max_points=float(request.form['max_points']),
                  description=request.form['assignment_description'])

    elif request.form['send'] == "UpdateAssignment":
        updateRow(Assignment, int(request.form['assignment_id']),
                  class_id=int(request.form['class_id']),
                  name=request.form['assignment_name'],
                  max_points=float(request.form['max_points']),
                  description=request.form['assignment_description'])
    elif request.form['send'] == "DeleteAssignment":
        deleteRow(Assignment, int(request.form['assignment_id']))
    return redirect(url_for('assignmentView', class_id=request.form['class_id']))

@app.route('/class_roster', methods=["GET", "POST"])
@login_required
def classRosterView(classId=''):
    if request.method == "GET":
        roster, notEnrolledStudents, classData = getClassRoster(request.args.get('class_id'))
        return render_template('classRoster.html', roster=roster, notEnrolledStudents=notEnrolledStudents, classData=classData) 
    elif request.form['send'] == "AddStudents":
        for student in request.form.getlist('studentSelect'):
            insertRow(ClassRoster, student_id=student, class_id=request.form['classId'])
    elif request.form['send'] == "DeleteStudents":
        for student in request.form['studentRemove']:
            deleteRow(ClassRoster, request.form['class_roster_id'])
    return redirect(url_for('classRosterView', class_id=request.form['classId']))


