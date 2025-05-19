from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from .forms import RegistrationForm, LoginForm
from app.models import User, Profile
from .. extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Проверка на существующего пользователя
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered!', 'danger')
                return redirect(url_for('auth.register'))

            user = User(
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                role='student'
            )

            profile = Profile(full_name=form.full_name.data)
            user.profile = profile

            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Registration error: {str(e)}', 'danger')

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        if not user:
            flash('Email not found', 'danger')
            return redirect(url_for('auth.login'))
        elif check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('User Logged successfully')
            return redirect(url_for('courses.index'))
        else:
            flash('Incorrect password', 'danger')
            return redirect(url_for('auth.login'))
    elif form.errors:
        flash('Please correct the errors in the form', 'warning')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

