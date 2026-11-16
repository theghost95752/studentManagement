import os
import random
import bcrypt 
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, timedelta
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt, get_jwt_identity, jwt_required
)
from models import db, Student, Teacher, Course, Assignments, Fees

app = Flask(__name__)
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=20)

CORS(app)
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Student routes
@app.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    students = Student.query.all()
    return jsonify([{
        'id': student.id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'email': student.email,
        'date_of_birth': student.date_of_birth,
        'created_at': student.created_at.isoformat()
    } for student in students]), 200

@app.route('/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    if str(get_jwt_identity()) != str(student_id):
        return jsonify({'error': 'You can only view your own profile'}), 403

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    return jsonify({
        'id': student.id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'email': student.email,
        'date_of_birth': student.date_of_birth,
        'created_at': student.created_at.isoformat()
    }), 200

@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object'}), 400

    required_fields = ('first_name', 'last_name', 'email', 'password')
    missing_fields = [
        field for field in required_fields
        if not isinstance(data.get(field), str) or not data[field].strip()
    ]
    if missing_fields:
        return jsonify({
            'error': 'Required fields are missing or empty',
            'fields': missing_fields
        }), 400

    password = data.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    new_student = Student(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        date_of_birth=data.get('date_of_birth'),
        password_hash=hashed_password.decode('utf-8')
    )
    db.session.add(new_student)
    db.session.commit()

    return jsonify({
        'id': new_student.id,
        'first_name': new_student.first_name,
        'last_name': new_student.last_name,
        'email': new_student.email,
        'date_of_birth': new_student.date_of_birth,
        'created_at': new_student.created_at.isoformat()
    }), 201

@app.route('/students/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json()
    student.first_name = data.get('first_name', student.first_name)
    student.last_name = data.get('last_name', student.last_name)
    student.email = data.get('email', student.email)
    student.date_of_birth = data.get('date_of_birth', student.date_of_birth)

    db.session.commit()

    return jsonify({
        'id': student.id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'email': student.email,
        'date_of_birth': student.date_of_birth,
        'created_at': student.created_at.isoformat()
    }), 200

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    db.session.delete(student)
    db.session.commit()

    return jsonify({'message': 'Student deleted successfully'}), 200

@app.route('/students/<int:student_id>/courses', methods=['GET'])
@jwt_required()
def get_student_courses(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    courses = student.courses
    return jsonify([{
        'id': course.id,
        'name': course.name,
        'description': course.description,
        'created_at': course.created_at.isoformat(),
        'teacher_id': course.teacher_id
    } for course in courses]), 200

@app.route('/students/<int:student_id>/fees', methods=['GET'])
@jwt_required()
def get_student_fees(student_id):
    if str(get_jwt_identity()) != str(student_id):
        return jsonify({'error': 'You can only view your own fees'}), 403

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    fees = student.fees
    return jsonify([{
        'id': fee.id,
        'amount': fee.amount,
        'due_date': fee.due_date.isoformat(),
        'status': fee.status,
        'student_id': fee.student_id
    } for fee in fees]), 200

@app.route('/students/<int:student_id>/assignments', methods=['GET'])
@jwt_required()
def get_student_assignments(student_id):
    if str(get_jwt_identity()) != str(student_id):
        return jsonify({'error': 'You can only view your own assignments'}), 403

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    return jsonify([{
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'file_url': assignment.file_url,
        'due_date': assignment.due_date.isoformat(),
        'course_id': assignment.course_id,
        'marks': assignment.marks
    } for assignment in student.assignments]), 200

@app.route('/students/login', methods=['POST'])
def student_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    student = Student.query.filter_by(email=email).first()
    if not student or not bcrypt.checkpw(password.encode('utf-8'), student.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(
        identity=str(student.id),
        additional_claims={'role': 'student'}
    )
    return jsonify({'access_token': access_token, 'id': student.id}), 200

@app.route('/students/signup', methods=['POST'])
def student_signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if Student.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    student = Student(
        email=email,
        password_hash=hashed_password.decode('utf-8'),
        first_name=first_name,
        last_name=last_name
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({'message': 'Student created successfully'}), 201

@app.route('/teachers/login', methods=['POST'])
def teacher_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    teacher = Teacher.query.filter_by(email=email).first()
    if not teacher or not bcrypt.checkpw(password.encode('utf-8'), teacher.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(
        identity=str(teacher.id),
        additional_claims={'role': 'teacher'}
    )
    return jsonify({'access_token': access_token, 'id': teacher.id}), 200

@app.route('/teachers/signup', methods=['POST'])
def teacher_signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if Teacher.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    teacher = Teacher(
        email=email,
        password_hash=hashed_password.decode('utf-8'),
        first_name=first_name,
        last_name=last_name
    )
    db.session.add(teacher)
    db.session.commit()

    return jsonify({'message': 'Teacher created successfully'}), 201

@app.route('/teachers/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_teacher(teacher_id):
    if str(get_jwt_identity()) != str(teacher_id):
        return jsonify({'error': 'You can only view your own profile'}), 403

    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404

    return jsonify({
        'id': teacher.id,
        'first_name': teacher.first_name,
        'last_name': teacher.last_name,
        'email': teacher.email
    }), 200

@app.route('/teachers/<int:teacher_id>/courses', methods=['GET'])
@jwt_required()
def get_teacher_courses(teacher_id):
    if (
        get_jwt().get('role') != 'teacher'
        or str(get_jwt_identity()) != str(teacher_id)
    ):
        return jsonify({'error': 'You can only view your own courses'}), 403

    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404

    return jsonify([{
        'id': course.id,
        'name': course.name,
        'description': course.description,
        'students': [{
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email
        } for student in course.students],
        'assignments': [{
            'id': assignment.id,
            'title': assignment.title,
            'description': assignment.description,
            'file_url': assignment.file_url,
            'due_date': assignment.due_date.isoformat(),
            'marks': assignment.marks,
            'student': {
                'id': assignment.student.id,
                'first_name': assignment.student.first_name,
                'last_name': assignment.student.last_name
            }
        } for assignment in course.assignments]
    } for course in teacher.courses]), 200

@app.route('/teachers/<int:teacher_id>', methods=['PUT'])
@jwt_required()
def update_teacher(teacher_id):
    if str(get_jwt_identity()) != str(teacher_id):
        return jsonify({'error': 'You can only update your own profile'}), 403

    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404

    data = request.get_json()
    teacher.first_name = data.get('first_name', teacher.first_name)
    teacher.last_name = data.get('last_name', teacher.last_name)

    db.session.commit()

    return jsonify({
        'id': teacher.id,
        'first_name': teacher.first_name,
        'last_name': teacher.last_name,
        'email': teacher.email
    }), 200

@app.route('/teachers/<int:teacher_id>', methods=['DELETE'])
@jwt_required()
def delete_teacher(teacher_id):
    if str(get_jwt_identity()) != str(teacher_id):
        return jsonify({'error': 'You can only delete your own profile'}), 403

    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404

    db.session.delete(teacher)
    db.session.commit()

    return jsonify({'message': 'Teacher deleted successfully'}), 200

@app.route('/courses/<int:course_id>/assignments', methods=['GET'])
@jwt_required()
def get_course_assignments(course_id):
    assignments = Assignments.query.filter_by(course_id=course_id).all()

    return jsonify([{
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'file_url': assignment.file_url,
        'due_date': assignment.due_date.isoformat(),
        'marks': assignment.marks
    } for assignment in assignments]), 200

@app.route('/fees', methods=['GET'])
@jwt_required()
def get_fees():
    fees = Fees.query.all()

    return jsonify([{
        'id': fee.id,
        'student_name': f'{fee.student.first_name} {fee.student.last_name}',
        'amount': fee.amount,
        'due_date': fee.due_date.isoformat(),
        'status': fee.status,
    } for fee in fees]), 200

@app.route('/fees/<int:fee_id>', methods=['GET'])
@jwt_required()
def get_fee(fee_id):
    fee = Fees.query.get(fee_id)
    if not fee:
        return jsonify({'error': 'Fee not found'}), 404

    return jsonify({
        'id': fee.id,
        'student_name': f'{fee.student.first_name} {fee.student.last_name}',
        'amount': fee.amount,
        'due_date': fee.due_date.isoformat(),
        'status': fee.status,
    }), 200

@app.route('/fees/<int:fee_id>', methods=['POST'])
@jwt_required()
def update_fee(fee_id):
    fee = Fees.query.get(fee_id)
    if not fee:
        return jsonify({'error': 'Fee not found'}), 404

    data = request.get_json()
    fee.amount = data.get('amount', fee.amount)
    fee.due_date = data.get('due_date', fee.due_date)
    fee.status = data.get('status', fee.status)

    db.session.commit()

    return jsonify({
        'id': fee.id,
        'student_name': f'{fee.student.first_name} {fee.student.last_name}',
        'amount': fee.amount,
        'due_date': fee.due_date.isoformat(),
        'status': fee.status,
    }), 200

@app.route('/fees/<int:fee_id>', methods=['PATCH'])
@jwt_required()
def patch_fee(fee_id):
    fee = Fees.query.get(fee_id)
    if not fee:
        return jsonify({'error': 'Fee not found'}), 404

    data = request.get_json()
    fee.amount = data.get('amount', fee.amount)
    fee.due_date = data.get('due_date', fee.due_date)
    fee.status = data.get('status', fee.status)

    db.session.commit()

    return jsonify({
        'id': fee.id,
        'student_name': f'{fee.student.first_name} {fee.student.last_name}',
        'amount': fee.amount,
        'due_date': fee.due_date.isoformat(),
        'status': fee.status,
    }), 200

@app.route('/fees/<int:fee_id>', methods=['DELETE'])
@jwt_required()
def delete_fee(fee_id):
    fee = Fees.query.get(fee_id)
    if not fee:
        return jsonify({'error': 'Fee not found'}), 404

    db.session.delete(fee)
    db.session.commit()

    return jsonify({'message': 'Fee deleted successfully'}), 200

@app.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    courses = Course.query.all()

    return jsonify([{
        'id': course.id,
        'name': course.name,
        'description': course.description,
        'students': [
            f'{student.first_name} {student.last_name}'
            for student in course.students
        ],
    } for course in courses]), 200

@app.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    return jsonify({
        'id': course.id,
        'name': course.name,
        'description': course.description,
        'students': [
            f'{student.first_name} {student.last_name}'
            for student in course.students
        ],
    }), 200

@app.route('/courses/<int:course_id>/students', methods=['GET'])
@jwt_required()
def get_course_students(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    students = course.students
    return jsonify([{
        'id': student.id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'email': student.email,
        'date_of_birth': student.date_of_birth,
        'created_at': student.created_at.isoformat()
    } for student in students]), 200

@app.route('/courses/<int:course_id>', methods=['POST'])
@jwt_required()
def update_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    data = request.get_json()
    course.name = data.get('name', course.name)
    course.description = data.get('description', course.description)

    db.session.commit()

    return jsonify({
        'id': course.id,
        'name': course.name,
        'description': course.description,
        'students': [
            f'{student.first_name} {student.last_name}'
            for student in course.students
        ],
    }), 200

@app.route('/courses/<int:course_id>', methods=['PATCH'])
@jwt_required()
def patch_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    data = request.get_json()
    course.name = data.get('name', course.name)
    course.description = data.get('description', course.description)

    db.session.commit()

    return jsonify({
        'id': course.id,
        'name': course.name,
        'description': course.description,
        'students': [
            f'{student.first_name} {student.last_name}'
            for student in course.students
        ],
    }), 200

@app.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    db.session.delete(course)
    db.session.commit()

    return jsonify({'message': 'Course deleted successfully'}), 200 


@app.route('/assignments', methods=['GET'])
@jwt_required()
def get_assignments():
    assignments = Assignments.query.all()

    return jsonify([{
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'file_url': assignment.file_url,
        'due_date': assignment.due_date.isoformat(),
        'course_name': assignment.course.name,
        'students': [
            f'{student.first_name} {student.last_name}'
            for student in assignment.course.students
        ],
        'marks': assignment.marks,
    } for assignment in assignments]), 200

@app.route('/assignments/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment(assignment_id):
    assignment = Assignments.query.get(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    return jsonify({
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'file_url': assignment.file_url,
        'due_date': assignment.due_date.isoformat(),
        'course_name': assignment.course.name,
        'students': [
            f'{student.first_name} {student.last_name}'
            for student in assignment.course.students
        ],
        'marks': assignment.marks,
    }), 200

@app.route('/assignments/<int:assignment_id>', methods=['POST'])
@jwt_required()
def update_assignment(assignment_id):
    assignment = Assignments.query.get(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    data = request.get_json()
    assignment.title = data.get('title', assignment.title)
    assignment.description = data.get('description', assignment.description)
    assignment.file_url = data.get('file_url', assignment.file_url)
    assignment.due_date = data.get('due_date', assignment.due_date)
    assignment.marks = data.get('marks', assignment.marks)

    db.session.commit()

    return jsonify({
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'file_url': assignment.file_url,
        'due_date': assignment.due_date.isoformat(),
        'course_name': assignment.course.name,
        'students': [
            f'{student.first_name} {student.last_name}'
            for student in assignment.course.students
        ],
        'marks': assignment.marks,
    }), 200

@app.route('/assignments/<int:assignment_id>', methods=['PATCH'])
@jwt_required()
def patch_assignment(assignment_id):
    assignment = Assignments.query.get(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    data = request.get_json()
    assignment.title = data.get('title', assignment.title)
    assignment.description = data.get('description', assignment.description)
    assignment.file_url = data.get('file_url', assignment.file_url)
    assignment.due_date = data.get('due_date', assignment.due_date)
    assignment.marks = data.get('marks', assignment.marks)

    db.session.commit()

    return jsonify({
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'file_url': assignment.file_url,
        'due_date': assignment.due_date.isoformat(),
        'course_name': assignment.course.name,
        'students': [
            f'{student.first_name} {student.last_name}'
            for student in assignment.course.students
        ],
        'marks': assignment.marks,
    }), 200

@app.route('/assignments/<int:assignment_id>', methods=['DELETE'])
@jwt_required()
def delete_assignment(assignment_id):
    assignment = Assignments.query.get(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    db.session.delete(assignment)
    db.session.commit()

    return jsonify({'message': 'Assignment deleted successfully'}), 200

@app.route('/students/<student_id>/courses/<course_id>', methods=['POST'])
@jwt_required()
def enroll_student_in_course(student_id, course_id):
    student = Student.query.get(student_id)
    course = Course.query.get(course_id)

    if not student or not course:
        return jsonify({'error': 'Student or Course not found'}), 404

    if course in student.courses:
        return jsonify({'error': 'Student already enrolled in this course'}), 400

    student.courses.append(course)
    db.session.commit()

    return jsonify({'message': f'Student {student.first_name} {student.last_name} enrolled in course {course.name} successfully'}), 200

@app.route('/students/<student_id>/courses/<course_id>', methods=['DELETE'])
@jwt_required()
def unenroll_student_from_course(student_id, course_id):
    student = Student.query.get(student_id)
    course = Course.query.get(course_id)

    if not student or not course:
        return jsonify({'error': 'Student or Course not found'}), 404

    if course not in student.courses:
        return jsonify({'error': 'Student is not enrolled in this course'}), 400

    student.courses.remove(course)
    db.session.commit()

    return jsonify({'message': f'Student {student.first_name} {student.last_name} unenrolled from course {course.name} successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)