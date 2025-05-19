import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'alexslkarate@gmail.com'
    MAIL_PASSWORD = 'hzhmmodmticnpwxl'  # Используйте app password, если Gmail
    MAIL_DEFAULT_SENDER = 'alexslkarate@gmail.com'