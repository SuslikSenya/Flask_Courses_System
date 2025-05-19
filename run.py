from app import create_app
from app.extensions import db
from flask_migrate import Migrate

app = create_app()  # Создание приложения через Factory
# migrate = Migrate(app, db)  # Инициализация миграций

if __name__ == '__main__':
    app.run(debug=True)  # Запуск сервера
