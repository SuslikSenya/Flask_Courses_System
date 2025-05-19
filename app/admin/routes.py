from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.models import Course, User, Profile
from app.extensions import db, mail
from .forms import CreateCourseForm, SendEmailForm
from .forms import AdminUserForm

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
@login_required
def check_admin():
    if current_user.email != 'alexslkarate@gmail.com':
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('auth.login'))


@admin_bp.route('/')
def dashboard():
    users = User.query.all()
    courses = Course.query.all()
    user_form = AdminUserForm()
    course_form = CreateCourseForm()

    course_form.teacher_id.choices = [
        (t.id, f"{t.profile.full_name} ({t.email})")
        for t in User.query.filter_by(role='teacher').all()
    ]
    return render_template('admin/dashboard.html',
                           users=users,
                           courses=courses,
                           user_form=user_form,
                           course_form=course_form)


@admin_bp.route('/send_email/<int:user_id>', methods=['GET', 'POST'])
def send_email(user_id):
    user = User.query.get_or_404(user_id)
    form = SendEmailForm()

    if form.validate_on_submit():
        try:
            msg = Message(subject=form.subject.data,
                          recipients=[user.email],
                          body=form.body.data)
            mail.send(msg)
            flash('Сообщение отправлено', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash(f'Ошибка при отправке письма: {str(e)}', 'danger')

    form.user_id.data = user.id
    return render_template('admin/send_email.html', user=user, form=form)


@admin_bp.route('/create_user', methods=['POST'])
def create_user():
    form = AdminUserForm()
    if form.validate_on_submit():
        try:
            user = User(
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                role=form.role.data
            )
            db.session.add(user)
            db.session.flush()

            profile = Profile(
                full_name=form.full_name.data,
                user_id=user.id
            )
            db.session.add(profile)
            db.session.commit()
            flash('Пользователь создан', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'danger')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь удалён', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/create_course', methods=["POST"])
def create_course():
    form = CreateCourseForm()
    form.teacher_id.choices = [  # Обновляем список преподавателей
        (t.id, f"{t.profile.full_name} ({t.email})")
        for t in User.query.filter_by(role='teacher').all()
    ]

    if form.validate_on_submit():
        try:
            course = Course(
                title=form.title.data,
                description=form.description.data,  # Исправлено на form.description.data
                teacher_id=form.teacher_id.data
            )
            db.session.add(course)
            db.session.commit()
            flash('Курс успешно создан', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Ошибка при создании курса (возможно, такой курс уже существует)', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')

    return redirect(url_for('admin.dashboard'))
