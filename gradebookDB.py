"""
    File for interactions with MySQL database instance in PythonAnywhere.
    We are using sqlalchemy for everything, inlcuding initial build
    and population. See dbInitialBuild.py for 
    table creation and initial data population
    usage: no direct usage, meant for import only
"""
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

sql = sqlalchemy
base = declarative_base()

testDBEndPoint ='mysql://IS668ProjectGrad:youGetAnA2019!@IS668ProjectGradeBook.mysql.pythonanywhere-services.com/IS668ProjectGrad$gradebook_test'
prodDBEndPoint = 'mysql://IS668ProjectGrad:youGetAnA2019!@IS668ProjectGradeBook.mysql.pythonanywhere-services.com/IS668ProjectGrad$gradebook'

"""still to do:
1. figure out alchemy relationships
2. create functions in class db for all insert, deletes, updates
3. figure out a way to handle connection pooling.
   MySql is set to a max pool of 3 and connects are being left hanging,
   address through exception handling"""

class db():
    def __init__(self):
        self.sql = sqlalchemy
        self.engine = sql.create_engine(testDBEndPoint,
                                        echo=True)
        self.connection = self.engine.connect()
        self.Session = self.sql.orm.sessionmaker(bind=self.engine)
        self.session = self.Session()

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
        fkVal = self.session.query(pk).filter(att_name==value).first()
        return fkVal


class majors(base):
    __tablename__ = 'majors'

    major_id = sql.Column(sql.Integer, primary_key=True)
    major_name = sql.Column(sql.String(100), nullable=False)

    def __repr__(self):
        return ("<majors('major_name'={0})>".format(self.major_name))

    #students = sql.orm.relationship('students', back_populates='majors')

class students(base):
    __tablename__ = 'students'

    student_id = sql.Column(sql.Integer, primary_key=True)
    first_name = sql.Column(sql.String(100), nullable=False)
    last_name = sql.Column(sql.String(100), nullable=False)
    major_id = sql.Column(sql.Integer, sql.ForeignKey('majors.major_id',
                          onupdate='CASCADE', ondelete='RESTRICT'),
                          nullable=False)
    email_address = sql.Column(sql.String(100), nullable=False)

    #major = sql.orm.relationship('majors', back_populates='students')
    def __repr__(self):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
        return ("<students('first_name'={}, 'last_name'={},\
                 'major_id'={},\
                 'email_address'={})>".format(self.first_name, self.last_name,
                                       self.major_id, self.email_address))

class classes(base):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
    __tablename__ = 'classes'

    class_id = sql.Column(sql.Integer, primary_key=True)
    class_name = sql.Column(sql.String(100), nullable=True)
    class_abbrv = sql.Column(sql.String(20))
    class_description = sql.Column(sql.String(3000))

    def __repr__(self):
        """
            representational object from the class.
            Optional per documentation but provides a nice output
            for when the class is called.
        """
        return ("<classes('class_name'={}, class_abbrv={}, \
                 class_description={})>".format(self.class_name,
                 self.class_abbrv, self.class_description))

class semesters(base):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
    __tablename__ = 'semesters'

    semester_id = sql.Column(sql.Integer, primary_key=True)
    semester = sql.Column(sql.String(40), nullable=False)
    year = sql.Column(sql.Integer, nullable=False)

    def __repr__(self):
        return ("<semesters('semester_id'={}, semester={},\
                 'year'={})>".format(self.semester_id, self.semester,
                  self.year))

class user_types(base):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
    __tablename__ = 'user_types'
    user_type_id = sql.Column(sql.Integer, primary_key=True)
    user_role = sql.Column(sql.String(50), nullable=False)

    def __repr__(self):
        return ("<user_types('user_type_id'={},\
                 'user_role'={})>".format(self.user_type_id, self.user_role))
class users(base):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
    __tablename__ = 'users'

    user_id = sql.Column(sql.Integer, primary_key=True)
    first_name = sql.Column(sql.String(100), nullable=False)
    last_name = sql.Column(sql.String(100), nullable=False)
    user_name = sql.Column(sql.String(40), nullable=False, unique=True)
    user_password = sql.Column(sql.String(40), nullable=False)
    user_type = sql.Column(sql.Integer, sql.ForeignKey('user_types.user_type_id',
                                                       onupdate='CASCADE',
                                                       ondelete='RESTRICT'))
    email_address = sql.Column(sql.String(100), nullable=False, unique=True)

    def __repr__(self):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
        return ("<users('user_id'={}, 'first_name'={}, 'last_name'={},\
                 'user_name'={}, 'user_password'={}, 'user_type'={}\
                 'email_address'={})>".format(self.user_id, self.first_name,
                 self.last_name, self.user_name, self.user_password,
                 self.user_type, self.email_address))

class term_classes(base):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
    __tablename__ = 'term_classes'

    term_class_id = sql.Column(sql.Integer, primary_key=True)
    class_id = sql.Column(sql.Integer, sql.ForeignKey('classes.class_id',
                                                      onupdate='CASCADE',
                                                      ondelete='RESTRICT'))
    semester_id = sql.Column(sql.Integer, 
                             sql.ForeignKey('semesters.semester_id',
                                            onupdate='CASCADE',
                                            ondelete='RESTRICT'))
    subsection = sql.Column(sql.String(30))
    comments = sql.Column(sql.String(3000))

    def __repr__(self):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
        return ("<term_classes('term_class_id'={}, 'class_id'={}\
                 'semester_id'={}, 'subsection'={},\
                 'comments'={})>".format(self.term_class_id, self.class_id,
                 self.semester_id, self.subsection, self.comments))

class class_rosters(base):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
    __tablename__ = 'class_rosters'

    student_id = sql.Column(sql.Integer, sql.ForeignKey('students.student_id',
                                                        onupdate='CASCADE',
                                                        ondelete='RESTRICT'),
                                                        primary_key=True)
    term_classes = sql.Column(sql.Integer, 
                              sql.ForeignKey('term_classes.term_class_id',
                                             onupdate='CASCADE',
                                             ondelete='RESTRICT'),
                                             primary_key=True)

    def __repr__(self):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
        return ("<class_rosters('student_id'={},\
                 'term_classes'={})>".format(self.student_id, 
                                             self.term_classes))

class assignments(base):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
    __tablename__ = 'assignments'

    assignment_id = sql.Column(sql.Integer, primary_key=True)
    term_class_id = sql.Column(sql.Integer,
                               sql.ForeignKey('term_classes.term_class_id',
                               onupdate='CASCADE', ondelete='RESTRICT'))
    max_points = sql.Column(sql.Integer, default=0, nullable=False)
    description = sql.Column(sql.String(400))

    def __repr__(self):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
        return ("<assignments('assignment_id'={}, 'term_class_id'={}\
                 'max_points'={},\
                 'description'={})>".format(self.assignment_id,
                 self.term_class_id, self.max_points, self.description))

class assignment_grades(base):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
    __tablename__ = 'assignment_grades'
    student_id = sql.Column(sql.Integer, 
                            sql.ForeignKey('students.student_id',
                                           onupdate='CASCADE',
                                           ondelete='RESTRICT'),
                                            primary_key=True)
    assignment_id = sql.Column(sql.Integer, 
                               sql.ForeignKey('assignments.assignment_id',
                                              onupdate='CASCADE',
                                              ondelete='RESTRICT'),
                                              primary_key=True)
    score = sql.Column(sql.Float(2), default=0, nullable=False)

    def __repr__(self):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
        return ("<assignment_grades('student_id'={}, 'assignment_id'={},\
                 'score'={})>".format(self.student_id, self.assignment_id,
                 self.score))

class user_access(base):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
    __tablename__ = 'user_access'

    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.user_id',
                                                     onupdate='CASCADE',
                                                     ondelete='RESTRICT'),
                                                     primary_key=True)
    term_class_id = sql.Column(sql.Integer,
                               sql.ForeignKey('term_classes.term_class_id',
                               onupdate='CASCADE', ondelete='RESTRICT'),
                               primary_key=True)

    def __repr__(self):
    """
        sqlalchemy.ext.declarative.declarative_base object
        These objects are used to build out the meta table
        on the table structure. Variable names corrospond
        to column names, variable definitions corrospond to
        the column structure (data type, keys if any,
        constraints)
        @return string      : showing the object with object values
                              in the attributes
    """
        return ("<user_access('user_id'={},\
                 'term_class_id'={})>".format(self.user_id,
                 self.term_class_id))
