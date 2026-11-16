from app import app
from models import db, Student, Teacher, Course, Assignments, Admin, Fees, student_courses
from faker import Faker
from faker_vehicle import VehicleProvider
import bcrypt

fake = Faker()
fake.add_provider(VehicleProvider)

with app.app_context():
    Assignments.query.delete()
    Fees.query.delete()
    db.session.execute(student_courses.delete())
    Course.query.delete()
    Student.query.delete()
    Teacher.query.delete()
    Admin.query.delete()

    # Students section
    students = []
    for _ in range(10):
        password = 'password123' 
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        student = Student(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=100).strftime('%Y-%m-%d'),
            password_hash=hashed_password.decode('utf-8')
        )
        students.append(student)
        db.session.add(student)
        db.session.commit()  # Commit after adding each student to ensure IDs are generated

        print("Students created successfully.")

    # Teachers section
    teachers = []
    for _ in range(5):
        password = 'password123'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        teacher = Teacher(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            password_hash=hashed_password.decode('utf-8')
        )
        teachers.append(teacher)
        db.session.add(teacher)
        db.session.commit()  # Commit after adding each teacher to ensure IDs are generated

        print("Teachers created successfully.")

    # Courses section
    courses = []
    for _ in range(10):
        course = Course(
            name=fake.bs().title(),
            description=fake.text(max_nb_chars=200),
            teacher_id=fake.random_element(elements=[teacher.id for teacher in teachers]),
            total_fees=fake.random_int(min=1000, max=5000)
        )
        courses.append(course)
        db.session.add(course)
        db.session.commit()  # Commit after adding each course to ensure IDs are generated
        print("Courses created successfully.")
    
    # Assignments section
    assignments = []
    for _ in range(20):
        assignment = Assignments(
            title=fake.catch_phrase(),
            student_id=fake.random_element(elements=[student.id for student in students]),
            description=fake.text(max_nb_chars=200),
            file_url=fake.file_path(depth=3, category='office'),
            due_date=fake.date_time_this_year(),
            course_id=fake.random_element(elements=[course.id for course in courses]),
            marks=fake.random_int(min=0, max=100)
        )
        assignments.append(assignment)
        db.session.add(assignment)
        db.session.commit()  # Commit after adding each assignment to ensure IDs are generated

        print("Assignments created successfully.")
    
    # Fees section
    fees = []
    for student in students:
        fee = Fees(
            student_id=student.id,
            amount=fake.random_int(min=1000, max=5000),
            due_date=fake.date_time_this_year(),
            status=fake.random_element(elements=['Paid', 'Unpaid'])
        )
        fees.append(fee)
        db.session.add(fee)
        db.session.commit()  # Commit after adding each fee to ensure IDs are generated

        print("Fees created successfully.")
    
    # Admin section
    admins = []
    for _ in range(2):
        password = 'password123'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        admin = Admin(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            password_hash=hashed_password.decode('utf-8')
        )
        admins.append(admin)
        db.session.add(admin)
        db.session.commit()  # Commit after adding each admin to ensure IDs are generated

        print("Admins created successfully.")
