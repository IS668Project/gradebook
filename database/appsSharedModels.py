"""
    File for interactions with MySQL database instance in PythonAnywhere.
    We are using flask_sqlalchemy for everything, inlcuding initial build
    and population. See dbInitialBuild.py for 
    table creation and initial data population
    usage: no direct usage, meant for import only
"""
import functools

from flask_sqlalchemy import SQLAlchemy, sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, \
     check_password_hash
from time import sleep

db = SQLAlchemy()

#global transaction helper functions
def dbTransaction(func):
    """
        mySQL is throwing operational errors quite frequenlty
        This is intended as a decorator, takes the sql action
        and tries to complete. If it fails due to session being down
        (OperationalError) waits 2 seconds and then retries. Will try
        4 times.
        @param func : function to be run
        @return wrapper: wrapper funciton containing the executed
        function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        attemptCount=1
        while attemptCount < 4:
            try:
                func(*args, **kwargs)
                return
            #except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.InvalidRequestError) as oe:
            except:
                db.session.rollback()
                attemptCount += 1
                sleep(2)
                continue
    return wrapper

def dbQuery(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        attemptCount=1
        while attemptCount < 4:
            try:
                func(*args, **kwargs)
                return func(*args, **kwargs)
            except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.InvalidRequestError) as oe:
                db.session.rollback()
                attemptCount += 1
                sleep(2)
                continue
    return wrapper.__wrapped__

@dbTransaction
def insertRow(model, **kwargs):
    insert = model(**kwargs)
    db.session.add(insert)
    db.session.commit()

@dbTransaction
def updateRow(model, rowId, **kwargs):
    update = model.query.get(rowId)
    for key, value in kwargs.items():
        setattr(update, key, value)
    db.session.commit()

@dbTransaction
def deleteRow(model, rowId):
    deletion = model.query.get(rowId)
    db.session.delete(deletion)
    db.session.commit()

#queries used by the flask app
@dbQuery
def getStudents():
    results = Student.query.order_by('last_name', 'first_name').all()
    return results

@dbQuery
def getStudentData(studentId):
    result = Student.query.get(studentId)
    return result

@dbQuery
def getClasses():
    results = Class.query.order_by('class_abbrv').all()
    return results

@dbQuery
def getClassAssignments(classId):
    results = Class.query.get(classId)
    return results

@dbQuery
def getClassRoster(classId):
    results = Class.query.get(classId)
    return results

class dbTools:
    def getFkValue(self, table, att_name, value):
        """
            Function to return the primary key id for a table
            meant for use when building foreign key pairing during
            inserts.
            @param table class      : applicable class that we want 
                                      to know the pk for
            @param att_name object  : attribute name whose value we are
                                      going to compare
            @param value int or str : value to look up, could be
                                      string or int depending on
                                      attribute being evaluated
            @return fkVal int       : pk value from parent to be
                                      used as FK value
        """
        pk = table.__mapper__.primary_key[0]
        fkVal = db.session.query(pk).filter(att_name==value).first()
        return fkVal

class Major(db.Model):
    __tablename__ = 'majors'
    major_id = db.Column(db.Integer, primary_key=True)
    major_name = db.Column(db.String(100), nullable=False)
    students = db.relationship('Student', back_populates='majors')

    def __repr__(self):
        return ("<majors('major_id'={}, 'major_name'={},\
                'students'={})>".format(self.major_id,
                                        self.major_name,
                                        self.students))

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    major_id = db.Column(db.Integer, db.ForeignKey('majors.major_id',
                          onupdate='CASCADE', ondelete='RESTRICT'),
                          nullable=False)
    email_address = db.Column(db.String(100), nullable=False)
    assignment_grades = db.relationship('AssignmentGrade',
                                        backref='Student',
                                        lazy=True)
    class_roster = db.relationship('ClassRoster', backref='Student',
                                   lazy=True)
    majors = db.relationship('Major', back_populates='students')

    def __repr__(self):
        return ("<students('first_name'={}, 'last_name'={},\
                 'major_id'={}, 'email_address'={},\
                 'assignment_grades'={}, class_roster={}\
                 'majors'={})>".format(self.first_name,
                                       self.last_name,
                                       self.major_id, 
                                       self.email_address,
                                       self.assignment_grades,
                                       self.class_roster,
                                       self.majors))

class Class(db.Model):
    __tablename__ = 'classes'
    class_id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), nullable=True)
    class_abbrv = db.Column(db.String(20))
    class_description = db.Column(db.String(3000))
    class_semester = db.Column(db.String(50))
    class_year = db.Column(db.Integer)
    assignment = db.relationship('Assignment', backref='Class', lazy=True)
    class_roster = db.relationship('ClassRoster', backref='Class', lazy=True)

    def __repr__(self):
        return ("<classes('class_name'={}, class_abbrv={}, \
                 class_semester={}, class_description={}, 'assignment'={}\
                 'class_roster'={})>".format(self.class_name,
                                                self.class_abbrv, 
                                                self.class_semester,
                                                self.class_description,
                                                self.assignment,
                                                self.class_roster))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(40), nullable=False, unique=True)
    user_password = db.Column(db.String(128), nullable=False)
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    user_access = db.relationship('UserAccess', backref='User',
                                  lazy=True)

    def __init__(self, first_name, last_name, user_name, user_password, email_address):
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name
        self.set_password(user_password)
        self.email_address = email_address

    def set_password(self, password):
        """Takes in string and sets password in salted hash"""
        self.user_password = generate_password_hash(password)

    def check_password(self, password):
        """
            takes in string, converts to salted hash, compares to salted hash in db, 
            returns true/false
        """
        return check_password_hash(self.user_password, password)

    def get_id(self):
        return self.user_name

    def __repr__(self):
        return ("<users('user_id'={}, 'first_name'={}, 'last_name'={},\
                 'user_name'={}, 'user_access' = {}, 'user_password' = {}\
                 'email_address'={},\
                 'user_access'={})>".format(self.user_id, self.first_name,
                                            self.last_name, self.user_name,
                                            self.user_access, 
                                            self.user_password, 
                                            self.email_address, 
                                            self.user_access))

    def canIsee(self, classId):
        """to be used to check user access permission on page level"""
        for access in self.user_access:
            if access.class_id == classId:
                return True
        return False


class ClassRoster(db.Model):
    __tablename__ = 'class_rosters'
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id',
                                                        onupdate='CASCADE',
                                                        ondelete='CASCADE'),
                                                        primary_key=True)
    class_id = db.Column(db.Integer, 
                              db.ForeignKey('classes.class_id',
                                             onupdate='CASCADE',
                                             ondelete='CASCADE'),
                                             primary_key=True)

    def __repr__(self):
        return ("<class_rosters('student_id'={},\
                 'class_id'={})>".format(self.student_id, 
                                             self.class_id))

class Assignment(db.Model):
    __tablename__ = 'assignments'
    assignment_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer,
                         db.ForeignKey('classes.class_id',
                                       onupdate='CASCADE', ondelete='CASCADE'))
    name = db.Column(db.String(40), nullable=False)
    max_points = db.Column(db.Integer, default=0, nullable=False)
    description = db.Column(db.String(400))
    assingment_grade = db.relationship('AssignmentGrade',
                                        backref='Assignment',
                                        lazy = True)

    def __repr__(self):
        return ("<assignments('assignment_id'={}, 'class_id'={},\
                 'name'={},'max_points'={}, 'description'={},\
                 assingment_grade={})>".format(self.assignment_id,
                                               self.class_id, 
                                               self.name, 
                                               self.max_points,
                                               self.description,
                                               self.assingment_grade))

class AssignmentGrade(db.Model):
    __tablename__ = 'assignment_grades'
    student_id = db.Column(db.Integer, 
                            db.ForeignKey('students.student_id',
                                           onupdate='CASCADE',
                                           ondelete='CASCADE'),
                                            primary_key=True)
    assignment_id = db.Column(db.Integer, 
                               db.ForeignKey('assignments.assignment_id',
                                              onupdate='CASCADE',
                                              ondelete='CASCADE'),
                                              primary_key=True)
    comments = db.Column(db.String(400))
    score = db.Column(db.Float(2), default=0, nullable=False)

    def __repr__(self):

        return ("<assignment_grades('student_id'={}, 'assignment_id'={},\
                 'score'={})>".format(self.student_id, self.assignment_id,
                 self.score))

class UserAccess(db.Model):
    __tablename__ = 'user_access'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id',
                                                     onupdate='CASCADE',
                                                     ondelete='CASCADE'),
                                                     primary_key=True)
    class_id = db.Column(db.Integer,
                               db.ForeignKey('classes.class_id',
                               onupdate='CASCADE', ondelete='CASCADE'),
                               primary_key=True)

    def __repr__(self):
        return ("<user_access('user_id'={},\
                 'class_id'={})>".format(self.user_id,
                 self.class_id))
