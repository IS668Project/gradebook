--delete all user defined tables
set foreign_key_checks=0;
drop table assignment;
drop table assignment_grade;
drop table class_roster;
drop table classes;
drop table majors;
drop table semester;
drop table student;
drop table term_classes;
drop table user;
drop table user_access;
drop table user_type;
set foreign_key_checks=1;
commit;


CREATE TABLE If not exists majors(
    major_id int not null auto_increment primary key,
    major_name varchar(100));

CREATE TABLE If not exists student(
    student_id int not null auto_increment primary key,
    first_name varchar(100),
    last_name varchar(100),
    major_id int,
    email_address varchar(100),
    FOREIGN KEY fk_major(major_id)
    REFERENCES majors(major_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT);

CREATE TABLE If not exists classes(
    class_id int not null auto_increment primary key,
    class_name varchar(100),
    class_abbrv varchar(20),
    class_description varchar(3000));

CREATE TABLE If not exists semester(
    semester_id int not null auto_increment primary key,
    semester varchar(50),
    year int(4));

CREATE TABLE If not exists user_types(
    user_type_id int not null auto_increment primary key,
    user_role varchar(50));

CREATE TABLE If not exists user(
    user_id int not null auto_increment primary key,
    first_name varchar(100),
    last_name varchar(100),
    user_name varchar(40),
    user_password varchar(40),
    user_type int not null,
    email_address varchar(100),
    FOREIGN KEY fk_utype(user_type)
    REFERENCES user_types(user_type)
    ON UPDATE CASCADE
    ON DELETE RESTRICT);

CREATE TABLE If not exists term_classes(
    term_class_id int not null auto_increment primary key,
    class_id int,
    semester_id int,
    subsection varchar(30),
    comments varchar(3000),
    FOREIGN KEY fk_classes(class_id)
    REFERENCES classes(class_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
    FOREIGN KEY fk_semester(semester_id)
    REFERENCES semester(semester_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT);

CREATE TABLE If not exists class_roster(
    student_id int not null,
    term_class_id int not null,
    PRIMARY KEY (student_id, term_class_id),
    FOREIGN KEY fk_student(student_id)
    REFERENCES student(student_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
    FOREIGN KEY fk_term_classes(term_class_id)
    REFERENCES term_classes(term_class_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT);

CREATE TABLE If not exists assignment(
    assignment_id int not null auto_increment primary key,
    term_class_id int not null,
    max_points int,
    description varchar(400),
    FOREIGN KEY fk_term_classes(term_class_id)
    REFERENCES term_classes(term_class_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT);

CREATE TABLE If not exists assignment_grade(
    student_id int not null,
    assignment_id int not null,
    score float(2),
    PRIMARY KEY (student_id, assignment_id),
    FOREIGN KEY fk_student(student_id)
    REFERENCES student(student_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
    FOREIGN KEY fk_assignment(assignment_id)
    REFERENCES assignment(assignment_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT);

CREATE TABLE If not exists user_access(
    user_id int not null,
    term_class_id int not null,
    PRIMARY KEY (user_id, term_class_id),
    FOREIGN KEY fk_user(user_id)
    REFERENCES user(user_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
    FOREIGN KEY fk_term_classes(term_class_id)
    REFERENCES term_classes(term_class_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT);