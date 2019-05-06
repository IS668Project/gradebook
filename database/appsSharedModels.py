"""
    File for interactions with MySQL database instance in PythonAnywhere.
    We are using flask_sqlalchemy for everything, including initial build
    and population. See dbInitialBuild.py for
    table creation and initial data population
    usage: no direct usage, meant for import only
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, \
     check_password_hash


db = SQLAlchemy()


class Major(db.Model):
    __tablename__ = 'majors'
    major_id = db.Column(db.Integer, primary_key=True)
    major_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return ("<majors('major_id'={}, \
                'major_name'={},>".format(self.major_id, 
                                          self.major_name))


class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    major_id = db.Column(db.Integer, db.ForeignKey('majors.major_id',
                                                   onupdate='CASCADE',
                                                   ondelete='RESTRICT'),
                         nullable=False)
    email_address = db.Column(db.String(100), nullable=False)
    student_archived = db.Column(db.Integer, nullable=False, default=0)
    assignment_grades = db.relationship('AssignmentGrade',
                                        backref='Student',
                                        lazy=True)
    class_roster = db.relationship('ClassRoster', backref='Student',
                                   lazy=True)
    majors = db.relationship('Major', backref='Student')

    def __repr__(self):
        return ("<students('student_id'={}, 'first_name'={}, \
                 'last_name'={}, 'major_id'={}, \
                 'email_address'={}, 'student_archived'={} \
                 'assignment_grades'={}, class_roster={}\
                 'majors'={})>".format(self.student_id,
                                       self.first_name,
                                       self.last_name,
                                       self.major_id,
                                       self.email_address,
                                       self.student_archived,
                                       self.assignment_grades,
                                       self.class_roster,
                                       self.majors))


class Class(db.Model):
    __tablename__ = 'classes'
    class_id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100))
    class_abbrv = db.Column(db.String(20))
    class_description = db.Column(db.String(3000))
    class_semester = db.Column(db.String(50))
    class_year = db.Column(db.Integer)
    class_archived = db.Column(db.Integer, nullable=False, default=0)
    assignment = db.relationship('Assignment', backref='Class', lazy=True)
    class_roster = db.relationship('ClassRoster', backref='Class', lazy=True)

    def __repr__(self):
        return ("<classes('class_name'={}, class_abbrv={}, \
                 class_semester={}, class_description={}, \
                 'class_archived'={} 'assignment'={}\
                 'class_roster'={})>".format(self.class_name,
                                             self.class_abbrv,
                                             self.class_semester,
                                             self.class_description,
                                             self.class_archived,
                                             self.assignment,
                                             self.class_roster))


class User(UserMixin, db.Model):
    """
        User is both model and UserMixin from flask_login.
        Custom __init__ for password hash/salt
    """
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(40), nullable=False, unique=True)
    user_password = db.Column(db.String(128), nullable=False)
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    user_access = db.relationship('UserAccess', backref='User',
                                  lazy=True)

    def __init__(self, first_name, last_name, user_name,
                 user_password, email_address):
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
            takes in string, converts to salted hash,
            compares to salted hash in db,
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
    class_roster_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id',
                                                     onupdate='CASCADE',
                                                     ondelete='CASCADE'))
    class_id = db.Column(db.Integer,
                         db.ForeignKey('classes.class_id',
                                       onupdate='CASCADE',
                                       ondelete='CASCADE'))
    student = db.relationship(Student, backref=ClassRoster)
    course = db.relationship(Class, backref=ClassRoster)

    def __repr__(self):
        return ("<class_rosters('class_roster_id'={}, \
                 'student_id'={}, 'first_name'={}, 'last_name'={},\
                 'email_address'={}, 'class_id'={}, 'class_name'={}, \
                 'class_abbrv'={} \
                 'class_description'={}, class_semester={}, \
                 'class_year'={})>".format(self.class_roster_id,
                                           self.student_id,
                                           self.student.first_name,
                                           self.student.last_name,
                                           self.student.email_address,
                                           self.class_id,
                                           self.course.class_name,
                                           self.course.class_abbrv,
                                           self.course.class_description,
                                           self.course.class_semester,
                                           self.course.class_year))


class Assignment(db.Model):
    __tablename__ = 'assignments'
    assignment_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer,
                         db.ForeignKey('classes.class_id',
                                       onupdate='CASCADE', ondelete='CASCADE'))
    name = db.Column(db.String(40), nullable=False)
    max_points = db.Column(db.Integer, default=0, nullable=False)
    description = db.Column(db.String(400))
    assignment_due_date = db.Column(db.DateTime)
    assignment_grade = db.relationship('AssignmentGrade',
                                       backref='Assignment',
                                       lazy=True)

    def __repr__(self):
        return ("<assignments('assignment_id'={}, 'class_id'={},\
                 'name'={},'max_points'={}, 'description'={},\
                 assignment_grade={}, \
                 assignment_due_date={})>".format(self.assignment_id,
                                                  self.class_id,
                                                  self.name,
                                                  self.max_points,
                                                  self.description,
                                                  self.assignment_grade,
                                                  self.assignment_due_date))


class AssignmentGrade(db.Model):
    __tablename__ = 'assignment_grades'
    assign_grade_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,
                           db.ForeignKey('students.student_id',
                                         onupdate='CASCADE',
                                         ondelete='CASCADE'))
    assignment_id = db.Column(db.Integer,
                              db.ForeignKey('assignments.assignment_id',
                                            onupdate='CASCADE',
                                            ondelete='CASCADE'))
    comments = db.Column(db.String(400))
    score = db.Column(db.Float(2), default=0, nullable=False)
    assignment = db.relationship('Assignment',
                                 backref='AssignmentGrade')

    def __repr__(self):
        return ("<assignment_grades('assign_grade_id'={}, \
                 student_id'={}, 'assignment_id'={},\
                 'score'={}, 'assignment_name'={}, \
                 'max_points'={})>".format(self.assign_grade_id, 
                                           self.student_id,
                                           self.assignment_id,
                                           self.score,
                                           self.assignment.name,
                                           self.assignment.max_points))


class UserAccess(db.Model):
    __tablename__ = 'user_access'
    user_access_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'))
    class_id = db.Column(db.Integer,
                         db.ForeignKey('classes.class_id',
                                       onupdate='CASCADE', ondelete='CASCADE'))

    def __repr__(self):
        return ("<user_access('user_id'={},\
                 'class_id'={})>".format(self.user_id,
                                         self.class_id))
