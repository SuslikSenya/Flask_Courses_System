from flask import Flask, url_for, redirect

from .config import Config
from .extensions import db, login_manager, mail, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'

    # Регистрация Blueprints
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.courses.routes import courses_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(courses_bp, url_prefix='/courses')

    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

    with app.app_context():
        # db.drop_all()
        db.create_all()

    return app
