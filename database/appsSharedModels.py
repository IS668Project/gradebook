"""
    File for interactions with MySQL database instance in PythonAnywhere.
    We are using flask_sqlalchemy for everything, inlcuding initial build
    and population. See dbInitialBuild.py for 
    table creation and initial data population
    usage: no direct usage, meant for import only
"""
import functools

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, \
     check_password_hash
from time import sleep

db = SQLAlchemy()

class OperationalError(Exception):
    pass

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
                    db.session.commit()
                    return
                except OperationalError as oe:
                    db.session.rollback()
                    attemptCount += 1
                    sleep(2)
                    continue
        return wrapper

    @dbTransaction
    def insertRow(model, **kwargs):
        insert = model(**kwargs)
        db.session.add(insertRow)

    @dbTransaction
    def updateRow(model, rowId, **kwargs):
        update = model.query.get(rowId)
        for key, value in kwargs.items():
            setattr(update, key, value)

    @dbTransaction
    def deleteRow(model, rowId):
        deletion = model.query.get(rowId)
        db.session.delete(deletion)


class majors(db.Model):
    major_id = db.Column(db.Integer, primary_key=True)
    major_name = db.Column(db.String(100), nullable=False)
    students = db.relationship('students', backref='majors',
                               lazy=True)

    def __repr__(self):
        return ("<majors('major_name'={0})>".format(self.major_name))

class students(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    major_id = db.Column(db.Integer, db.ForeignKey('majors.major_id',
                          onupdate='CASCADE', ondelete='RESTRICT'),
                          nullable=False)
    email_address = db.Column(db.String(100), nullable=False)
    assignment_grades = db.relationship('assignment_grades',
                                        backref='students',
                                        lazy=True)
    class_roster = db.relationship('class_rosters', backref='students',
                                   lazy=True)

    def __repr__(self):
        return ("<students('first_name'={}, 'last_name'={},\
                 'major_id'={},\
                 'email_address'={})>".format(self.first_name, self.last_name,
                                              self.major_id, 
                                              self.email_address))

class classes(db.Model):
    class_id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), nullable=True)
    class_abbrv = db.Column(db.String(20))
    class_description = db.Column(db.String(3000))
    term_classes = db.relationship('term_classes', backref='classes',
                                   lazy=True)

    def __repr__(self):
        return ("<classes('class_name'={}, class_abbrv={}, \
                 class_description={})>".format(self.class_name,
                 self.class_abbrv, self.class_description))

class semesters(db.Model):
    semester_id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(40), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    term_classes = db.relationship('term_classes', backref='semesters',
                                   lazy=True)

    def __repr__(self):
        return ("<semesters('semester_id'={}, semester={},\
                 'year'={})>".format(self.semester_id, self.semester,
                  self.year))

class user_types(db.Model):
    user_type_id = db.Column(db.Integer, primary_key=True)
    user_role = db.Column(db.String(50), nullable=False)
    user = db.relationship('users', backref='user_types', lazy=True)

    def __repr__(self):
        return ("<user_types('user_type_id'={},\
                 'user_role'={})>".format(self.user_type_id, self.user_role))
class users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(40), nullable=False, unique=True)
    user_password = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.Integer, db.ForeignKey('user_types.user_type_id',
                                                       onupdate='CASCADE',
                                                       ondelete='RESTRICT'))
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    user_access = db.relationship('user_access', backref='users',
                                  lazy=True)
    def __init__(self, first_name, last_name, user_name, user_password, user_type, email_address):
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name
        self.set_password(user_password)
        self.user_type = user_type
        self.email_address = email_address

    def set_password(self, password):
        self.user_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.user_password, password)

    def __repr__(self):
        return ("<users('user_id'={}, 'first_name'={}, 'last_name'={},\
                 'user_name'={}, 'user_type'={}, 'user_password' = {}\
                 'email_address'={})>".format(self.user_id, self.first_name,
                 self.last_name, self.user_name,
                 self.user_type, self.user_password, self.email_address))

class term_classes(db.Model):
    term_class_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id',
                                                      onupdate='CASCADE',
                                                      ondelete='CASCADE'))
    semester_id = db.Column(db.Integer, 
                             db.ForeignKey('semesters.semester_id',
                                            onupdate='CASCADE',
                                            ondelete='CASCADE'))
    subsection = db.Column(db.String(30))
    comments = db.Column(db.String(3000))
    assignments = db.relationship('assignments', backref='term_classes',
                                  lazy=True)

    def __repr__(self):

        return ("<term_classes('term_class_id'={}, 'class_id'={}\
                 'semester_id'={}, 'subsection'={},\
                 'comments'={})>".format(self.term_class_id, self.class_id,
                 self.semester_id, self.subsection, self.comments))

class class_rosters(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id',
                                                        onupdate='CASCADE',
                                                        ondelete='CASCADE'),
                                                        primary_key=True)
    term_classes = db.Column(db.Integer, 
                              db.ForeignKey('term_classes.term_class_id',
                                             onupdate='CASCADE',
                                             ondelete='CASCADE'),
                                             primary_key=True)

    def __repr__(self):

        return ("<class_rosters('student_id'={},\
                 'term_classes'={})>".format(self.student_id, 
                                             self.term_classes))

class assignments(db.Model):
    assignment_id = db.Column(db.Integer, primary_key=True)
    term_class_id = db.Column(db.Integer,
                               db.ForeignKey('term_classes.term_class_id',
                               onupdate='CASCADE', ondelete='CASCADE'))
    name = db.Column(db.String(40), nullable=False)
    max_points = db.Column(db.Integer, default=0, nullable=False)
    description = db.Column(db.String(400))
    assignment_grades = db.relationship('assignment_grades',
                                        backref='assignments',
                                        lazy = True)

    def __repr__(self):
        return ("<assignments('assignment_id'={}, 'term_class_id'={},\
                 'name'={},'max_points'={},\
                 'description'={})>".format(self.assignment_id,
                 self.term_class_id, self.name, self.max_points, self.description))

class assignment_grades(db.Model):
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
    score = db.Column(db.Float(2), default=0, nullable=False)

    def __repr__(self):

        return ("<assignment_grades('student_id'={}, 'assignment_id'={},\
                 'score'={})>".format(self.student_id, self.assignment_id,
                 self.score))

class user_access(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id',
                                                     onupdate='CASCADE',
                                                     ondelete='CASCADE'),
                                                     primary_key=True)
    term_class_id = db.Column(db.Integer,
                               db.ForeignKey('term_classes.term_class_id',
                               onupdate='CASCADE', ondelete='CASCADE'),
                               primary_key=True)
    term_classes = db.relationship('term_classes', backref='user_access',
                                   lazy=True)

    def __repr__(self):
        return ("<user_access('user_id'={},\
                 'term_class_id'={})>".format(self.user_id,
                 self.term_class_id))
