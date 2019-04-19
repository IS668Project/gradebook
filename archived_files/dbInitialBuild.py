import gradebookDB

dbtest = db()

def dropAllTables():
    base.metadata.drop_all(dbtest.engine)

def createAllTables():
    base.metadata.create_all(dbtest.engine)

def createInitialData():
        dbtest.session.add_all([
            majors(major_name='Information Systems'),
            majors(major_name='Computer Science'),
            majors(major_name='Computer Engineering'),
            majors(major_name='Cyber Security'),
            ])
        dbtest.session.commit()
        dbtest.session.add_all([
            students(first_name='John', last_name='Sullivan',
                     major_id=dbtest.getFkValue(majors, majors.major_name,
                                                'Information Systems'),
                     email_address='johnsu1@umbc'),
            students(first_name='Jessica', last_name='Stack',
                     major_id=dbtest.getFkValue(majors, majors.major_name,
                                                'Information Systems'),
                     email_address='dg89092@umbc.edu'),
            students(first_name='Jacob', last_name='Rosario',
                     major_id=dbtest.getFkValue(majors,
                                                majors.major_name,
                                                'Computer Science'),
                     email_address='crusader@umbc.edu'),
            students(first_name='Anabelle', last_name='Warner',
                     major_id=dbtest.getFkValue(majors, majors.major_name,
                                                'Computer Science'),
                                                email_address='claypool@umbc.edu'),
            students(first_name='Clay', last_name='Thompson',
                     major_id=dbtest.getFkValue(majors, majors.major_name,
                                                'Computer Engineering'),
                                                email_address='claytom@umbc.edu'),
            students(first_name='Tom', last_name='Beagle',
                     major_id=dbtest.getFkValue(majors, majors.major_name,
                                                'Computer Engineering'),
                                                email_address='TomBeag@umbc.edu'),
            students(first_name='Sally', last_name='Shoemaker',
                     major_id=dbtest.getFkValue(majors, majors.major_name,
                                                'Cyber Security'),
                     email_address='salshoe@umbc.edu'),
            students(first_name='Brittany', last_name='Hacker',
                     major_id=dbtest.getFkValue(majors, majors.major_name,
                                                'Cyber Security'),
                     email_address='brithack@umbc.edu')])
        dbtest.session.commit()
        dbtest.session.add_all([
            classes(class_name='Enterprise Computing', class_abbrv='IS668',
                    class_description='Class on distributed systems and\
                                      the technology used to implement it')])
        dbtest.session.commit()
        dbtest.session.add_all([
            semesters(semester='Spring', year=2019)])
        dbtest.session.commit()
        dbtest.session.add_all([
            user_types(user_role='User'),
            user_types(user_role='Admin')])
        dbtest.session.commit()
        dbtest.session.add_all([
            users(first_name='John', last_name='Sullivan',
                  user_name='johnsu1', user_password='test',
                  user_type=dbtest.getFkValue(user_types, user_types.user_role,
                                              'Admin'),
                  email_address='johnsu1@umbc.edu'),
            users(first_name='Jessica', last_name='Stack',
                  user_name='jessstack', user_password='test',
                  user_type=dbtest.getFkValue(user_types, user_types.user_role,
                                              'Admin'),
                  email_address='dg89092@umbc.edu'),
            users(first_name='test', last_name='user',
                  user_name='test', user_password='test',
                  user_type=dbtest.getFkValue(user_types, user_types.user_role,
                                              'User'),
                  email_address='test@umbc.edu')])
        dbtest.session.commit()
        dbtest.session.add_all([
            term_classes(class_id=dbtest.getFkValue(classes, classes.class_abbrv,
                                                    'IS668'),
                         semester_id=dbtest.getFkValue(semesters, semesters.semester,
                                                       'Spring'),
                         subsection='001',
                         comments='This is our first class in the test db')])
        dbtest.session.commit()
        dbtest.session.add_all([
            class_rosters(student_id=dbtest.getFkValue(students,
                                                       students.first_name, 'Jessica'),
                          term_classes=dbtest.getFkValue(term_classes,
                                                         term_classes.subsection,
                                                         '001')),
            class_rosters(student_id=dbtest.getFkValue(students, students.first_name,
                                                       'Jacob'),
                          term_classes=dbtest.getFkValue(term_classes,
                                                         term_classes.subsection,
                                                         '001')),
            class_rosters(student_id=dbtest.getFkValue(students, students.first_name,
                                                       'Anabelle'),
                          term_classes=dbtest.getFkValue(term_classes,
                                                         term_classes.subsection,
                                                         '001')),
            class_rosters(student_id=dbtest.getFkValue(students, students.first_name,
                                                       'Clay'),
                          term_classes=dbtest.getFkValue(term_classes,
                                                         term_classes.subsection,
                                                         '001')),
            class_rosters(student_id=dbtest.getFkValue(students, students.first_name,
                                                       'Tom'),
                          term_classes=dbtest.getFkValue(term_classes,
                                                         term_classes.subsection,
                                                         '001')),
            class_rosters(student_id=dbtest.getFkValue(students, students.first_name,
                                                       'Sally'),
                          term_classes=dbtest.getFkValue(term_classes,
                                                         term_classes.subsection,
                                                         '001')),
            class_rosters(student_id=dbtest.getFkValue(students, students.first_name,
                                                       'Brittany'),
                          term_classes=dbtest.getFkValue(term_classes,
                                                         term_classes.subsection,
                                                         '001')),
            class_rosters(student_id=dbtest.getFkValue(students, students.first_name,
                                                       'John'),
                          term_classes=dbtest.getFkValue(term_classes,
                                                         term_classes.subsection,
                                                         '001'))])
        dbtest.session.commit()
        dbtest.session.add_all([
            assignments(term_class_id=dbtest.getFkValue(term_classes,
                                                        term_classes.subsection,
                                                        '001'),
                        name='Discussion', max_points=25, description='Discussions'),
            assignments(term_class_id=dbtest.getFkValue(term_classes,
                                                        term_classes.subsection,
                                                        '001'),
                        name='Midterm', max_points=25, description='Midterm'),
            assignments(term_class_id=dbtest.getFkValue(term_classes,
                                                        term_classes.subsection,
                                                        '001'),
                        name='Project', max_points=25, description='Project'),
            assignments(term_class_id=dbtest.getFkValue(term_classes,
                                                        term_classes.subsection,
                                                        '001'),
                        name='Final', max_points=25, description='Final')])
        dbtest.session.commit()
        dbtest.session.add_all([
            user_access(user_id=dbtest.getFkValue(users, users.first_name, 'John'),
                        term_class_id=dbtest.getFkValue(term_classes,
                                                        term_classes.subsection,
                                                        '001')),
            user_access(user_id=dbtest.getFkValue(users, users.first_name, 'Jessica'),
                        term_class_id=dbtest.getFkValue(term_classes,
                                                        term_classes.subsection,
                                                        '001')),
            user_access(user_id=dbtest.getFkValue(users, users.first_name, 'test'),
                        term_class_id=dbtest.getFkValue(term_classes,
                                                        term_classes.subsection,
                                                        '001'))])
        dbtest.session.commit()

if __name__ == '__main__':
    print('WARNING, this script wipes out everything in the db before\
          recreating tables and populating with initial data found\
          in this file, think before you proceed.')
    proceed = int(input('Do you want to proceed with the wipe and rebuild?\
                        (type 1 for yes): '))
    if proceed == 1:
        dropAllTables()
        createAllTables()
        createInitialData()

    print('Script has completed, please review current DB and logs')
