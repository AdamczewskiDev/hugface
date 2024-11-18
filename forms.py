from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class IncomeForm(FlaskForm):
    amount = FloatField('Kwota', validators=[DataRequired(), NumberRange(min=0)])
    date = DateField('Data', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Dodaj')

class ExpenseForm(FlaskForm):
    category = StringField('Kategoria', validators=[DataRequired()])
    amount = FloatField('Kwota', validators=[DataRequired(), NumberRange(min=0)])
    date = DateField('Data', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Dodaj')