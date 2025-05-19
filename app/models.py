from flask_login import UserMixin
from .extensions import login_manager, db

# Таблица для связи многие-ко-многим (студенты-курсы)
enrollments = db.Table('enrollments',
                     db.Column('student_id', db.Integer, db.ForeignKey('users.id')),
                     db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
                     )


class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Таблица называется 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # teacher/student

    # Отношения
    profile = db.relationship('Profile', back_populates='user', uselist=False)
    courses_taught = db.relationship('Course', back_populates='teacher')
    courses_enrolled = db.relationship(
        'Course',
        secondary=enrollments,
        back_populates='students'
    )


class Profile(db.Model):
    __tablename__ = 'profiles'  # Изменил на 'profiles' для единообразия

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Теперь ссылается на 'users.id'
    user = db.relationship('User', back_populates='profile')


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Теперь ссылается на 'users.id'
    teacher = db.relationship('User', back_populates='courses_taught')
    materials = db.relationship('Material', back_populates='course')
    students = db.relationship(
        'User',
        secondary=enrollments,
        back_populates='courses_enrolled'
    )


class Material(db.Model):
    __tablename__ = 'materials'  # Изменил на 'materials'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))  # Ссылается на 'courses.id'
    course = db.relationship('Course', back_populates='materials')  # Исправлено на 'materials'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))