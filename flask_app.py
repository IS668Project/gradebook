
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, LoginManager, logout_user
from flask_sqlalchemy import SQLAlchemy
from database.databaseConfig import testDBEndPoint, prodDBEndPoint
from database.appsSharedModels import *
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = testDBEndPoint
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 200
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.secret_key = "E*2kd+2sMPSt<VgN,26y!"
login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(user_name=user_id).first()

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
            return redirect(url_for('dashboardView'))

@app.route('/login', methods=['GET', 'POST'])
def checkLogin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

@app.route('/logout', methods=['GET'])
def logout():
    return 'place holder for logout'

@app.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    return 'place holder for changePassword'

@app.route('/dashboard', methods=["GET", "POST"])
def dashboardView():
    return 'place holder for dashboardView'

@app.route('/class', methods=["GET", "POST"])
def classView():
    return 'place holder for classView'

@app.route('/gradebook', methods=["GET", "POST"])
def gradebookView():
    return 'place holder for gradebookView'

@app.route('/student', methods=["GET", "POST"])
def studentView():
    checkLogin()
    if request.method == "GET":
        majorData = Major.query.order_by(Major.major_name.desc()).all()
        if request.args.get('student_id'):
            studentData = Student.query.filter_by(student_id=request.args.get('student_id')).first()
        else:
            studentData = Student()
        return render_template('student.html', studentData=studentData, majorData=majorData)
    else:
        requestContents.append(request.form['contents'])
        return redirect(url_for('studentView'))

