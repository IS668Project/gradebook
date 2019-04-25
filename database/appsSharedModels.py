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

    def dbTransaction(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attemptCount=1
            while attemptCount < 4:
                try:
                    func(*args, **kwargs)
                    return
                except sqlalchemy.exc.OperationalError as oe:
                    db.session.rollback()
                    attemptCount += 1
                    sleep(2)
                    continue
        return wrapper

    @dbTransaction
    def insertRow(model, **kwargs):
        insert = model(**kwargs)
        db.session.add(insertRow)
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


class Major(db.Model):
    __tablename__ = 'majors'
    major_id = db.Column(db.Integer, primary_key=True)
    major_name = db.Column(db.String(100), nullable=False)
    students = db.relationship('Student', backref='Major',
                               lazy=True)

    def __repr__(self):
        return ("<majors('major_name'={0})>".format(self.major_name))

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

    def __repr__(self):
        return ("<students('first_name'={}, 'last_name'={},\
                 'major_id'={},\
                 'email_address'={})>".format(self.first_name, self.last_name,
                                              self.major_id, 
                                              self.email_address))

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
                 class_semester={},\
                 class_description={})>".format(self.class_name,
                                                self.class_abbrv, 
                                                self.class_semester,
                                                self.class_description))

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
        self.user_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.user_password, password)

    def get_id(self):
        return self.user_name

    def __repr__(self):
        return ("<users('user_id'={}, 'first_name'={}, 'last_name'={},\
                 'user_name'={}, 'user_type'={}, 'user_password' = {}\
                 'email_address'={})>".format(self.user_id, self.first_name,
                 self.last_name, self.user_name,
                 self.user_type, self.user_password, self.email_address))



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
        return ("<assignments('assignment_id'={}, 'term_class_id'={},\
                 'name'={},'max_points'={},\
                 'description'={})>".format(self.assignment_id,
                 self.term_class_id, self.name, self.max_points, self.description))

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
