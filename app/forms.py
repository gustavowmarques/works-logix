from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TelField
from wtforms.validators import DataRequired, Email, Length

class RegisterUserForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    telephone = TelField('Telephone', validators=[Length(max=50)])

    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    company_id = SelectField('Company', coerce=int, validators=[DataRequired()])
    business_type_id = SelectField('Business Type', coerce=int)

    submit = SubmitField('Register')
