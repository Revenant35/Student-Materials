import pytest

import System

courses = ['comp_sci', 'databases', 'cloud_computing', 'software_engineering']

studentUsername = 'akend3'
studentPassword = '123454321'
studentCourse = 'databases'

taUsername = 'cmhbf5'
taPassword = 'bestTA'

professorUsername = "goggins"
professorPassword = "augurrox"
professorCourse = "software_engineering"

validAssignment = 'assignment1'
validGrade = 96

oldAssignment = 'assignment1'
newAssignment = 'Assignment3'
newDueDate = '5/12/14'

invalidUsername = 'AYOWADDUPMYBOY'
invalidPassword = 'beans'
invalidCourse = 'FortniteClass'


# 1. login - System.py
# The login function takes a name and password and sets the user for the program. Verify that the
# correct user is created with this test, and use the json files to check that it adds the correct data to the user.
def test_login_valid(grading_system):

    # Check Student Login
    grading_system.login(studentUsername, studentPassword)
    assert grading_system.usr.name == studentUsername
    assert grading_system.usr.password == studentPassword

    # Check TA Login
    grading_system.login(taUsername, taPassword)
    assert grading_system.usr.name == taUsername
    assert grading_system.usr.password == taPassword

    # Check Professor Login
    grading_system.login(professorUsername, professorPassword)
    assert grading_system.usr.name == professorUsername
    assert grading_system.usr.password == professorPassword


# 2. check_password - System.py
# This function checks that the password is correct. Enter several formats of passwords to verify that the
# password returns correctly if the passwords are the same.
def test_check_password_valid(grading_system):

    # Check Student Password
    assert grading_system.check_password(studentUsername, studentPassword)
    assert not grading_system.check_password(studentUsername, invalidPassword)

    # Check TA Password
    assert grading_system.check_password(taUsername, taPassword)
    assert not grading_system.check_password(taUsername, invalidPassword)

    # Check Professor Password
    assert grading_system.check_password(professorUsername, professorPassword)
    assert not grading_system.check_password(professorUsername, invalidPassword)

    # Check invalid username
    assert not grading_system.check_password(invalidUsername, invalidPassword)


# 3. change_grade - Staff.py
# This function will change the grade of a student and updates the database.
# Verify that the correct grade is changed on the correct user in the database.
def test_change_grade(staff_login):

    # Ensure validGrade is in the range [0, 100]
    assert 0 <= validGrade <= 100

    # Save the original grade from database
    originalGrade = staff_login.usr.check_grades(studentUsername, studentCourse)[0][1]

    # Handle the case that validGrade == originalGrade by changing the value stored in DB
    if validGrade == originalGrade:
        staff_login.usr.check_grades(studentUsername, studentCourse)[0][1] = -1
        assert staff_login.usr.check_grades(studentUsername, studentCourse)[0][1] == -1

    # Test the change_grade() function, ensure it works correctly
    staff_login.usr.change_grade(studentUsername, studentCourse, validAssignment, validGrade)
    assert staff_login.usr.check_grades(studentUsername, studentCourse)[0][1] == validGrade

    # Restore original grade to database
    staff_login.usr.check_grades(studentUsername, studentCourse)[0][1] = originalGrade


# 4. create_assignment Staff.py
# This function allows the staff to create a new assignment. Verify that an assignment is
# created with the correct due date in the correct course in the database.
def test_create_assignment(staff_login):

    # Ensure the new assignment doesn't already exist
    if newAssignment in staff_login.usr.all_courses[studentCourse]['assignments']:
        del staff_login.usr.all_courses[studentCourse]['assignments'][newAssignment]

    # Test the create_user function
    staff_login.usr.create_assignment(newAssignment, newDueDate, studentCourse)

    # Check that the function created the new assignment and that the due date is correct
    assert staff_login.usr.all_courses[studentCourse]['assignments'][newAssignment]
    assert staff_login.usr.all_courses[studentCourse]['assignments'][newAssignment]['due_date'] == newDueDate

    # Remove this new assignment from the database
    del staff_login.usr.all_courses[studentCourse]['assignments'][newAssignment]


# 5. add_student - Professor.py
# This function allows the professor to add a student to a course.
# Verify that a student will be added to the correct course in the database.
def test_add_student(professor_login):

    # bool to store if the student was enrolled in this course prior to test running
    if professorCourse in professor_login.usr.users[studentUsername]['courses']:
        is_enrolled = 1
    else:
        is_enrolled = 0

    # If the student is already in the test_course, drop them
    if is_enrolled:
        professor_login.usr.drop_student(studentUsername, professorCourse)
        assert professorCourse not in professor_login.usr.users[studentUsername]['courses']

    # Test the add_student() function
    professor_login.usr.add_student(studentUsername, professorCourse)
    assert professorCourse in professor_login.usr.users[studentUsername]['courses']

    # If the student was not already enrolled, drop them
    if not is_enrolled:
        professor_login.usr.drop_student(studentUsername, professorCourse)
        assert professorCourse not in professor_login.usr.users[studentUsername]['courses']


# 6. drop_student Professor.py
# This function allows the professor to drop a student in a course.
# Verify that the student is added and dropped from the correct course in the database.
def test_drop_student(professor_login):

    is_enrolled = False
    originalCourse = None

    # bool to store if the student was enrolled in this course prior to test running
    if studentCourse not in professor_login.usr.users[studentUsername]['courses']:
        # Add Student to course
        assignments = professor_login.usr.all_courses[studentCourse]['assignments']
        for assignment in assignments:
            assignments[assignment]['grade'] = "N/A"
            assignments[assignment]['submission_date'] = "N/A"
            assignments[assignment]['submission'] = "N/A"
            assignments[assignment]['ontime'] = "N/A"
            del assignments[assignment]['due_date']
        professor_login.usr.users[studentUsername]['courses'][studentCourse] = assignments
        professor_login.usr.update_user_db()
    else:
        is_enrolled = True
        originalCourse = professor_login.usr.users[studentUsername]['courses'][studentCourse]

    assert studentCourse in professor_login.usr.users[studentUsername]['courses']

    # Test the drop_student() function
    professor_login.usr.drop_student(studentUsername, studentCourse)
    assert studentCourse not in professor_login.usr.users[studentUsername]['courses']

    # If the user was enrolled prior to testing, drop them
    if is_enrolled:
        professor_login.usr.users[studentUsername]['courses'][studentCourse] = originalCourse
        professor_login.usr.update_user_db()
        assert studentCourse in professor_login.usr.users[studentUsername]['courses']


# 7. submit_assignment - Student.py
# This function allows a student to submit an assignment.
# Verify that the database is updated with the correct assignment,
#  submission, submission date and in the correct course.
def test_submit_assignment(student_login):

    # Variable to hold any data of a previous submission
    assignmentData = None

    # If there is a previous submission, store it in assignmentData and delete it from DB
    if oldAssignment in student_login.usr.courses[studentCourse]:
        assignmentData = student_login.usr.courses[studentCourse][oldAssignment]
        del student_login.usr.courses[studentCourse][oldAssignment]

    # Ensure the previous submission data is removed
    assert oldAssignment not in student_login.usr.courses[studentCourse]

    # Test submit_assignment() function
    student_login.usr.submit_assignment(studentCourse, oldAssignment, 'blah blah blah', newDueDate)
    assert oldAssignment in student_login.usr.courses[studentCourse]

    # If there was a previous submission, restore it in DB
    if assignmentData:
        student_login.usr.courses[studentCourse][oldAssignment] = assignmentData


# 8. check_ontime - Student.py
# This function checks if an assignment is submitted on time.
# Verify that it will return true if the assignment is on time, and false if the assignment is late.
def test_check_ontime(student_login):

    # Ensure a submission date before due date returns True
    assert student_login.usr.check_ontime("12/5/22", "12/12/22")

    # Ensure a submission date after due date returns False
    assert not student_login.usr.check_ontime("12/19/22", "12/12/22")


# 9. check_grades - Student.py
# This function returns the users grades for a specific course.
# Verify the correct grades are returned for the correct user.
def test_check_grades(student_login):

    # Get a list of all grades the user has recorded in DB
    assignments = student_login.usr.courses[studentCourse]
    grades = []
    for key in assignments:
        grades.append([key, assignments[key]['grade']])

    # Ensure that check_grades() function's return matches this list
    assert student_login.usr.check_grades(studentCourse) == grades


# 10. view_assignments - Student.py
# This function returns assignments and their due dates for a specific course.
# Verify that the correct assignments for the correct course are returned.
def test_view_assignments(student_login):
    # Iterate through each course
    for course in courses:
        # Get a list of all assignments in said course
        assignments_raw = student_login.usr.all_courses[course]['assignments']
        assignments_formatted = []
        # Iterate through each assignment
        for assignment in assignments_raw:
            # Format and append to assignments_formatted
            assignments_formatted.append([assignment, assignments_raw[assignment]['due_date']])
        # Ensure view_assignments() matches the above list
        assert student_login.usr.view_assignments(course) == assignments_formatted


# 11. test_login_invalid_username - System.py
# This function ensures that should a user attempt to check a password
# with an invalid username, the system returns false
def test_login_invalid_username(grading_system):
    assert not grading_system.login(invalidUsername, invalidPassword)


# 12. test_check_grade_different_course - Staff.py
# This function ensures that a Staff Member cannot check the grade
# of a student in a course that is not theirs
def test_Staff_check_grade_different_course(staff_login):
    for course in courses:
        if course not in staff_login.usr.courses:
            assert not staff_login.usr.check_grades(studentUsername, course)


# 13. test_check_grade - Student.py
# This function ensures that should a user attempt to check a grade on
# an invalid course, the function should raise an error/return NIL
def test_Student_check_grade_invalid_course(student_login):
    assert not student_login.usr.check_grades(invalidCourse)


# 14. add_student - Professor.py
# This function ensures that a professor cannot add a student
# to a course that is not theirs
def test_add_student_different_course(professor_login):
    for course in courses:
        if course not in professor_login.usr.courses:
            # bool to store if the student was enrolled in this course prior to test running
            if professorCourse in professor_login.usr.users[studentUsername]['courses']:
                is_enrolled = 1
            else:
                is_enrolled = 0

            # If the student is already in the test_course, drop them
            if is_enrolled:
                professor_login.usr.drop_student(studentUsername, professorCourse)
                assert professorCourse not in professor_login.usr.users[studentUsername]['courses']

            # Test the add_student() function
            professor_login.usr.add_student(studentUsername, professorCourse)
            success = professorCourse in professor_login.usr.users[studentUsername]['courses']

            # If the student was not already enrolled, drop them
            if not is_enrolled:
                professor_login.usr.drop_student(studentUsername, professorCourse)
                assert professorCourse not in professor_login.usr.users[studentUsername]['courses']

            assert success


# 15. drop_student - Professor.py
# This function ensures that a professor cannot drop a student
# from a course that is not theirs
def test_drop_student_different_course(professor_login):
    for course in courses:
        if course not in professor_login.usr.courses:
            is_enrolled = False
            originalCourse = None

            # bool to store if the student was enrolled in this course prior to test running
            if studentCourse not in professor_login.usr.users[studentUsername]['courses']:
                # Add Student to course
                assignments = professor_login.usr.all_courses[studentCourse]['assignments']
                for assignment in assignments:
                    assignments[assignment]['grade'] = "N/A"
                    assignments[assignment]['submission_date'] = "N/A"
                    assignments[assignment]['submission'] = "N/A"
                    assignments[assignment]['ontime'] = "N/A"
                    del assignments[assignment]['due_date']
                professor_login.usr.users[studentUsername]['courses'][studentCourse] = assignments
                professor_login.usr.update_user_db()
                assert studentCourse in professor_login.usr.users[studentUsername]['courses']
            else:
                is_enrolled = True
                originalCourse = professor_login.usr.users[studentUsername]['courses'][studentCourse]

            # Test the drop_student() function
            professor_login.usr.drop_student(studentUsername, studentCourse)
            success = not studentCourse not in professor_login.usr.users[studentUsername]['courses']

            # If the user was enrolled prior to testing, drop them
            if is_enrolled:
                professor_login.usr.users[studentUsername]['courses'][studentCourse] = originalCourse
                professor_login.usr.update_user_db()
                assert studentCourse in professor_login.usr.users[studentUsername]['courses']

            assert success



def init_system():
    system = System.System()
    system.load_data()
    return system


@pytest.fixture
def grading_system():
    return init_system()


@pytest.fixture
def staff_login():
    system = init_system()
    system.login(taUsername, taPassword)
    return system


@pytest.fixture
def professor_login():
    system = init_system()
    system.login(professorUsername, professorPassword)
    return system


@pytest.fixture
def student_login():
    system = init_system()
    system.login(studentUsername, studentPassword)
    return system
