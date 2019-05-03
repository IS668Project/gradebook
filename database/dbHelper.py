import functools
from database.appsSharedModels import *
from time import sleep

"""
    mySQL is throwing operational errors quite frequently
    The two functions below are intended as a decorator, takes the sql action
    and tries to complete. If it fails due to session being down
    (OperationalError or InvalidRequestError) rolls back, waits 2 seconds, and then retries. 
    Will try 4 times.
    @param func : function to be run
    @return wrapper: wrapper function containing the execution
    function
"""
def dbTransaction(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        attemptCount=1
        while attemptCount < 4:
            try:
                func(*args, **kwargs)
                db.session.commit()
                return
            except (sqlalchemy.exc.OperationalError,
                    sqlalchemy.exc.InvalidRequestError) as oe:
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
            except (sqlalchemy.exc.OperationalError, 
                    sqlalchemy.exc.InvalidRequestError) as oe:
                db.session.rollback()
                attemptCount += 1
                sleep(2)
                continue
    try:
        return wrapper.__wrapped__
    except AttributeError:
        return wrapper


#generic functions for add, update, delete
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


#model specific functions for add, update, delete
@dbTransaction
def addAssignmentToRoster(assignment_id, classId):
    roster = ClassRoster.query.filter_by(class_id=classId).all()
    for student in roster:
        insert = AssignmentGrade(student_id=student.student_id, \
                                 assignment_id=assignment_id)
        db.session.add(insert)

@dbTransaction
def addAssignmentsNewStudent(studentId, classId):
    classAssignments = Assignment.query.filter_by(class_id=classId).all()
    for assignment in classAssignments:
        insert = AssignmentGrade(student_id=studentId, \
                                 assignment_id=assignment.assignment_id)
        db.session.add(insert)

@dbTransaction
def deleteStudentAssignments(rosterId):
    assignments = ClassRoster.query.filter_by(class_roster_id=rosterId). \
                              join(Assignment).join(AssignmentGrade). \
                              add_columns(AssignmentGrade.assign_grade_id)
    for assignment in assignments:
        deleteRow(AssignmentGrade, assignment.assign_grade_id)


#queries used flask app processing
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
def getAssignmentId(assignmentName, classId):
    results = Assignment.query.filter_by(name=assignmentName, \
                                         class_id=classId).first()
    return results.assignment_id

@dbQuery
def getClassRoster(classId):
    results = ClassRoster.query.filter_by(class_id=classId).join(Student). \
              add_entity(Student).join(Class).add_entity(Class).all()
    subquery = ClassRoster.query.with_entities(ClassRoster.student_id). \
                                               filter_by(class_id=classId).all()
    studentIds = Student.query.filter(Student.student_id. \
                                      notin_(subquery)).all()
    classData = Class.query.get(classId)
    return (results, studentIds, classData)

@dbQuery
def deleteRosterAssignment(rosterId):
    rosterObj = ClassRoster.query.get(rosterId)
    AssignmentsList = AssignmentGrade.query.filter_by(student_id=rosterObj.student_id) \
                                  .join(Student).join(Assignment).filter_by(class_id=rosterObj.class_id) \
                                  .all()
    for assignment in AssignmentsList:
        deleteRow(AssignmentGrade, assignment.assign_grade_id)

@dbQuery
def getClassGrades(classId):
    AssignmentNames = Assignment.query.filter_by(class_id=classId).order_by(Assignment.assignment_due_date).all()
    headerList = []
    totalPoints = 0
    for assignment in AssignmentNames:
        header = {}
        header['name'] = assignment.name
        header['id'] = assignment.assignment_id
        header['dueDate'] = assignment.assignment_due_date
        header['maxPoints'] = assignment.max_points
        totalPoints += assignment.max_points
        headerList.append(header)
    StudentData = Student.query.join(AssignmentGrade). \
                                     join(Assignment).filter_by(class_id=1). \
                                     order_by(Student.last_name, Student.first_name,
                                     Assignment.assignment_due_date).all()
    studentList=[]
    for student in StudentData:
        studentScore = 0
        studentData={}
        studentData['name'] = ' '.join((student.first_name,
                                        student.last_name))
        studentData['studentId'] = student.student_id
        studentGrades = []
        for grades in student.assignment_grades:
            gradesDict ={}
            gradesDict['assign_id'] = grades.assignment_id
            gradesDict['assign_score'] = grades.score
            gradesDict['assign_grade_id'] = grades.assign_grade_id
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
    if gradePercent < 60:
        return 'F'
    grades = ['A', 'A-', 'B', 'B-', 'C', 'C-', 'D', 'D-', 'F']
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
def checkGradeChange(assignGradeId='', score=''):
    check = AssignmentGrade.query.get(assignGradeId)
    if check.assign_grade_id == score:
        return
    updateRow(AssignmentGrade, assignGradeId, score=score)
    return

@dbQuery
def getClassInfo(classId):
    results = Class.query.get(classId)
    return results

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
    fkVal = db.session.query(pk).filter(att_name==value).first()
    if fkVal:
        return fkVal[0]
    else:
        return