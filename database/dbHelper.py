import functools
from database.appsSharedModels import *
from flask_sqlalchemy import sqlalchemy

from datetime import datetime
from random import randint
from time import sleep

from logs import gradebookLog

"""
    mySQL is throwing operational errors quite frequently
    The two functions below are intended as a decorator, takes the sql action
    and tries to complete. If it fails due to session being down
    (OperationalError or InvalidRequestError) rolls back,
    waits 2 seconds, and then retries.
    Will try 4 times.
    @param func : function to be run
    @return wrapper: wrapper function containing the execution
    function
"""


def dbTransaction(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        attemptCount = 1
        while attemptCount < 4:
            try:
                func(*args, **kwargs)
                db.session.commit()
                return
            except (sqlalchemy.exc.OperationalError,
                    sqlalchemy.exc.InvalidRequestError) as e:
                gradebookLog.simpleLog('{}'.format(e))
                db.session.rollback()
                attemptCount += 1
                sleep(2)
                continue
    return wrapper


def dbQuery(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        attemptCount = 1
        while attemptCount < 4:
            try:
                func(*args, **kwargs)
                return func(*args, **kwargs)
            except (sqlalchemy.exc.OperationalError,
                    sqlalchemy.exc.InvalidRequestError) as e:
                gradebookLog.simpleLog('{}'.format(e))
                db.session.rollback()
                attemptCount += 1
                sleep(2)
                continue
    try:
        return wrapper.__wrapped__
    except AttributeError:
        return wrapper


# generic functions for add, update, delete
@dbTransaction
def insertRow(model, **kwargs):
    insert = model(**kwargs)
    db.session.add(insert)


@dbTransaction
def updateRow(model, rowId, **kwargs):
    update = model.query.get(rowId)
    for key, value in kwargs.items():
        setattr(update, key, value)


@dbTransaction
def deleteRow(model, rowId):
    deletion = model.query.get(rowId)
    db.session.delete(deletion)


""" model specific functions for add, update, delete """
@dbTransaction
def addAssignmentToRoster(assignment_id, classId):
    roster = ClassRoster.query.filter_by(class_id=classId).all()
    for student in roster:
        insert = AssignmentGrade(student_id=student.student_id, \
                                 assignment_id=assignment_id)
        db.session.add(insert)


@dbTransaction
def addAssignmentsNewStudent(studentId, classId, dbInit=False):
    classAssignments = Assignment.query.filter_by(class_id=classId).all()
    for assignment in classAssignments:
        if dbInit:
            grade = randint(13,25)
        else:
            grade = 0
        insert = AssignmentGrade(student_id=studentId,
                                 assignment_id=assignment.assignment_id,
                                 score=grade)
        db.session.add(insert)


@dbTransaction
def deleteStudentAssignments(rosterId):
    """
        Used when removing a student from a class.
        Deletes all assignments for the student in the applicable class.
        @param rosterId int     : id representing a single student
                                  in a single class
    """
    assignments = ClassRoster.query.filter_by(class_roster_id=rosterId). \
                              join(Class).join(Assignment).join(AssignmentGrade). \
                              add_columns(AssignmentGrade.assign_grade_id).all()
    for assignment in assignments:
        deleteRow(AssignmentGrade, assignment[-1])


""" queries used in flask app processing """
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
    for assignment in results.assignment:
        assignment.assignment_due_date = assignment.assignment_due_date.strftime('%m/%d/%Y')
    return results


@dbQuery
def getAssignmentId(assignmentName, classId):
    results = Assignment.query.filter_by(name=assignmentName,
                                         class_id=classId).first()
    return results.assignment_id


@dbQuery
def getClassRoster(classId):
    """
        Used to provide data for classroster template generation.
        @param classId int                   : PK for classes
        @return results db.model             : list of db model __repr__
                                               object containing data needed
                                               for template for each student
        @return studentsNotEnrolled db.model : list of db model __repr__
                                               object containing data needed
                                               for template for each student not enrolled
        @return classData db.model           : db model __repr__ object
                                               for applicable class being viewed.
    """
    results = ClassRoster.query.filter_by(class_id=classId).join(Student). \
              add_entity(Student).join(Class).add_entity(Class).all()
    subquery = ClassRoster.query.with_entities(ClassRoster.student_id) \
                                .filter_by(class_id=classId).all()
    studentsNotEnrolled = Student.query.filter(Student.student_id.
                                      notin_(subquery)).order_by(Student.last_name, Student.first_name).all()
    classData = Class.query.get(classId)
    return (results, studentsNotEnrolled, classData)


@dbQuery
def getClassGrades(classId):
    """
        Given class id get objects related to grades for display in
        gradebook template.
        @param classId int                      : id for a specific class
        @return headerList list of dicts        : each dict contains data
                                                  for an assignment in the class
        @return studentList list obj            : contains student info  and
                                                  nested list of dicts containing
                                                  assignment grade info
    """

    AssignmentNames = Assignment.query.filter_by(class_id=classId).order_by(Assignment.assignment_due_date).all()
    headerList = []
    totalPoints = 0
    for assignment in AssignmentNames:
        header = {}
        header['name'] = assignment.name
        header['id'] = assignment.assignment_id
        header['dueDate'] = assignment.assignment_due_date.strftime('%m/%d/%Y')
        header['maxPoints'] = assignment.max_points
        totalPoints += assignment.max_points
        headerList.append(header)
    StudentData = Student.query.join(AssignmentGrade). \
                                join(Assignment).filter_by(class_id=classId). \
                                order_by(Student.last_name, Student.first_name,
                                Assignment.assignment_due_date).all()
    studentList = []
    for student in StudentData:
        studentScore = 0
        studentData = {}
        studentData['name'] = ' '.join((student.first_name,
                                        student.last_name))
        studentData['studentId'] = student.student_id
        studentGrades = []
        for grades in student.assignment_grades:
            gradesDict = {}
            gradesDict['assign_id'] = grades.assignment_id
            gradesDict['assign_score'] = grades.score
            gradesDict['assign_grade_id'] = grades.assign_grade_id
            gradesDict['assign_max_points'] = grades.Assignment.max_points
            studentGrades.append(gradesDict)
            studentScore += grades.score
        studentData['scores'] = studentGrades
        studentData['totalPoints'] = totalPoints
        studentData['studentScore'] = studentScore
        try:
            percent = float(studentScore) / totalPoints * 100
        except ZeroDivisionError:
            percent = 0
        studentData['gradePercent'] = percent
        studentData['letterGrade'] = getLetterGrade(studentData['gradePercent'])
        studentList.append(studentData)
    return headerList, studentList


def getLetterGrade(gradePercent):
    """
        Simplistic way to get letter grade based on class percent.
        @param gradePercent float   : student grade in percentage
        @return string              : letter grade
    """
    if gradePercent < 60:
        return 'F'
    grades = ['A', 'A-', 'B', 'B-', 'C', 'C-', 'D', 'D-']
    threshold = 100
    mode = 1
    for grade in grades:
        if mode == 1:
            threshold -= 6
            mode = 2
        else:
            threshold -= 4
            mode = 1
        if gradePercent >= threshold:
            return grade


@dbQuery
def getClassInfo(classId):
    results = Class.query.get(classId)
    return results

# dbInitialBuild function only
def getFkValue(table, att_name, value):
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
    fkVal = db.session.query(pk).filter(att_name == value).first()
    if fkVal:
        return fkVal[0]
    else:
        return
