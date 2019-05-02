import sys
sys.path.insert(0, '/home/IS668ProjectGradeBook/mysite')
from dbHelper import addAssignmentsNewStudent, dbTransaction, getFkValue
from datetime import datetime
from flask import Flask
from appsSharedModels import *
from databaseConfig import testDBEndPoint, prodDBEndPoint

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = testDBEndPoint
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 200
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def createInitialData():
        db.session.add_all([
            Major(major_name='Information Systems'),
            Major(major_name='Computer Science'),
            Major(major_name='Computer Engineering'),
            Major(major_name='Cyber Security'),
            ])
        db.session.commit()
        db.session.add_all([
            Student(first_name='John', last_name='Sullivan',
                     major_id=getFkValue(Major, Major.major_name,
                                                'Information Systems'),
                     email_address='johnsu1@umbc'),
            Student(first_name='Jessica', last_name='Stack',
                     major_id=getFkValue(Major, Major.major_name,
                                                'Information Systems'),
                     email_address='dg89092@umbc.edu'),
            Student(first_name='Jacob', last_name='Rosario',
                     major_id=getFkValue(Major,
                                                Major.major_name,
                                                'Computer Science'),
                     email_address='crusader@umbc.edu'),
            Student(first_name='Anabelle', last_name='Warner',
                     major_id=getFkValue(Major, Major.major_name,
                                                'Computer Science'),
                                                email_address='claypool@umbc.edu'),
            Student(first_name='Clay', last_name='Thompson',
                     major_id=getFkValue(Major, Major.major_name,
                                                'Computer Engineering'),
                                                email_address='claytom@umbc.edu'),
            Student(first_name='Tom', last_name='Beagle',
                     major_id=getFkValue(Major, Major.major_name,
                                                'Computer Engineering'),
                                                email_address='TomBeag@umbc.edu'),
            Student(first_name='Sally', last_name='Shoemaker',
                     major_id=getFkValue(Major, Major.major_name,
                                                'Cyber Security'),
                     email_address='salshoe@umbc.edu'),
            Student(first_name='Brittany', last_name='Hacker',
                     major_id=getFkValue(Major, Major.major_name,
                                                'Cyber Security'),
                     email_address='brithack@umbc.edu')])
        db.session.commit()
        db.session.add_all([
            Class(class_name='Enterprise Computing', class_abbrv='IS668',
                    class_semester='Spring', class_year=2019,
                    class_description='Class on distributed systems and\
                                      the technology used to implement it')])
        db.session.commit()
        db.session.add_all([
            User(first_name='John', last_name='Sullivan',
                  user_name='johnsu1', user_password='test',
                  email_address='johnsu1@umbc.edu'),
            User(first_name='Jessica', last_name='Stack',
                  user_name='jessstack', user_password='test',
                  email_address='dg89092@umbc.edu'),
            User(first_name='test', last_name='user',
                  user_name='test', user_password='test',
                  email_address='test@umbc.edu')])
        db.session.commit()
        rosterAdd = []
        for student in Student.query.all():
            rosterAdd.append(ClassRoster(student_id=student.student_id,
                        class_id=1))
        db.session.add_all(rosterAdd)
        db.session.commit()
        db.session.add_all([
            Assignment(class_id=1, name='Discussion',
                       max_points=25, description='Discussions',
                       assignment_due_data=datetime.strptime('05/19/2019', '%m/%d/%Y')),
            Assignment(class_id=1, name='Midterm', max_points=25,
                       description='Midterm',
                       assignment_due_data=datetime.strptime('04/16/2019', '%m/%d/%Y')),
            Assignment(class_id=1, name='Project', max_points=25,
                       description='Project',
                       assignment_due_data=datetime.strptime('05/22/2019', '%m/%d/%Y')),
            Assignment(class_id=1 ,name='Final', max_points=25,
                       description='Final',
                       assignment_due_data=datetime.strptime('05/19/2019', '%m/%d/%Y'))])
        db.session.commit()
        db.session.add_all([
            UserAccess(user_id=getFkValue(User, User.first_name, 'John'),
                        class_id=getFkValue(Class,
                                                 Class.class_abbrv,
                                                 'IS668')),
            UserAccess(user_id=getFkValue(User, User.first_name, 'Jessica'),
                        class_id=getFkValue(Class,
                                                 Class.class_abbrv,
                                                 'IS668')),
            UserAccess(user_id=getFkValue(User, User.first_name, 'test'),
                        class_id=getFkValue(Class,
                                                 Class.class_abbrv,
                                                 'IS668'))])
        db.session.commit()

def populateGrades():
    rosters = ClassRoster.query.all()
    for student in rosters:
        addAssignmentsNewStudent(student.student_id, student.class_id)

if __name__ == '__main__':
    print('WARNING, this script wipes out everything in the db before \n \
          recreating tables and populating with initial data found\n \
          in this file, think before you proceed.')
    proceed = int(input('Do you want to proceed with the wipe and rebuild?\n \
                        (type 1 for yes): '))
    if proceed == 1:
        create_app().app_context().push()
        db.drop_all()
        db.create_all()
        createInitialData()
        populateGrades()

    print('Script has completed, please review current DB and logs')
