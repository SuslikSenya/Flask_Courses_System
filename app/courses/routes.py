from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from .forms import AddMaterialForm
from ..admin.forms import CreateCourseForm
from app.models import Course, User, db, Material

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/')
@login_required
def index():
    if current_user.role == 'teacher':
        # Преподаватель видит свои курсы
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        form = CreateCourseForm()
        form.teacher_id.data = current_user.id  # Автоподстановка преподавателя
        return render_template('courses/teacher_index.html', courses=courses, form=form)
    else:
        # Студент видит все курсы
        courses = Course.query.all()
        enrolled_courses = [c.id for c in current_user.courses_enrolled]
        return render_template('courses/student_index.html',
                               courses=courses,
                               enrolled_courses=enrolled_courses)


@courses_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # Проверяем, что пользователь - преподаватель
    if current_user.role != 'teacher':
        flash('Только преподаватели могут создавать курсы', 'danger')
        return redirect(url_for('courses.index'))

    form = CreateCourseForm()

    # Для преподавателя автоматически подставляем его ID
    if current_user.role == 'teacher':
        form.teacher_id.data = current_user.id

    if form.validate_on_submit():
        try:
            # Проверяем, что преподаватель существует
            teacher = User.query.get(form.teacher_id.data)
            if not teacher or teacher.role != 'teacher':
                flash('Указанный преподаватель не найден', 'danger')
                return redirect(url_for('courses.create'))

            # Создаем курс
            course = Course(
                title=form.title.data,
                description=form.description.data,
                teacher_id=form.teacher_id.data
            )
            db.session.add(course)
            db.session.commit()
            flash('Курс успешно создан!', 'success')
            return redirect(url_for('courses.view', course_id=course.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании курса: {str(e)}', 'danger')

    # Если GET запрос или ошибки валидации
    return render_template('courses/create_course.html',
                           form=form,
                           current_user=current_user)


@courses_bp.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll(course_id):
    if current_user.role != 'student':
        flash('Только студенты могут записываться на курсы', 'danger')
        return redirect(url_for('courses.index'))

    course = Course.query.get_or_404(course_id)
    if course not in current_user.courses_enrolled:
        current_user.courses_enrolled.append(course)
        db.session.commit()
        flash(f'Вы записаны на курс "{course.title}"', 'success')
    else:
        flash('Вы уже записаны на этот курс', 'info')

    return redirect(url_for('courses.index'))


@courses_bp.route('/<int:course_id>')
@login_required
def view(course_id):
    course = Course.query.get_or_404(course_id)
    is_enrolled = course in current_user.courses_enrolled

    if current_user.role == 'teacher' and course.teacher_id != current_user.id:
        flash('Это не ваш курс', 'danger')
        return redirect(url_for('courses.index'))

    if current_user.role == 'student' and not is_enrolled:
        flash('Вы не записаны на этот курс', 'danger')
        return redirect(url_for('courses.index'))

    return render_template('courses/view.html',
                           course=course,
                           is_enrolled=is_enrolled)


@courses_bp.route('/<int:course_id>/add_material', methods=['GET', 'POST'])
@login_required
def add_material(course_id):
    course = Course.query.get_or_404(course_id)

    # Проверяем, что текущий пользователь - учитель этого курса
    if current_user.id != course.teacher_id:
        flash('Вы не можете добавлять материалы в этот курс', 'danger')
        return redirect(url_for('courses.view', course_id=course_id))

    form = AddMaterialForm()

    if form.validate_on_submit():
        material = Material(
            title=form.title.data,
            content=form.content.data,
            course_id=course_id
        )
        db.session.add(material)
        db.session.commit()
        flash('Материал успешно добавлен', 'success')
        return redirect(url_for('courses.view', course_id=course_id))

    return render_template('courses/add_material.html',
                           course=course,
                           form=form)


@courses_bp.route('/material/<int:material_id>/delete', methods=['POST'])
@login_required
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    course = material.course

    if current_user.id != course.teacher_id:
        flash('Вы не можете удалять материалы этого курса', 'danger')
        return redirect(url_for('courses.view', course_id=course.id))

    db.session.delete(material)
    db.session.commit()
    flash('Материал удален', 'success')
    return redirect(url_for('courses.view', course_id=course.id))


@courses_bp.route('/my')
@login_required
def my_courses():
    if current_user.role != 'teacher':
        flash('Эта страница доступна только преподавателям', 'danger')
        return redirect(url_for('courses.index'))

    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return render_template('courses/teacher_courses.html', courses=courses)
