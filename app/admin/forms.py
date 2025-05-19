from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, SelectField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User  # Импортируем модель User для проверки teacher_id


class AdminUserForm(FlaskForm):
    full_name = StringField('Полное имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Повторите пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    role = SelectField('Роль', choices=[
        ('student', 'Студент'),
        ('teacher', 'Преподаватель')
    ], validators=[DataRequired()])
    submit = SubmitField('Создать пользователя')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email уже занят')


class CreateCourseForm(FlaskForm):
    title = StringField('Название курса', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Описание курса', validators=[DataRequired()])
    teacher_id = SelectField('Преподаватель', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Создать курс')

    def __init__(self, *args, **kwargs):
        super(CreateCourseForm, self).__init__(*args, **kwargs)
        self.teacher_id.choices = [
            (teacher.id, f"{teacher.profile.full_name} ({teacher.email})")
            for teacher in User.query.filter_by(role='teacher').all()
        ]


class SendEmailForm(FlaskForm):
    user_id = HiddenField()
    subject = StringField('Тема', validators=[DataRequired()])
    body = TextAreaField('Сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')
