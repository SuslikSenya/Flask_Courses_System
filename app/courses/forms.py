from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AddMaterialForm(FlaskForm):
    title = StringField('Название материала', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    submit = SubmitField('Добавить материал')