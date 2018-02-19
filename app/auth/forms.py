from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from ..models import User

class LoginForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	remember_me = BooleanField("Keep me logged in")
	submit = SubmitField("Log In")

class RegistrationForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
	username = StringField("Username", validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'username must have only letters, numbers, dots or underscores.')])
	password = PasswordField("Password", validators=[DataRequired(), EqualTo("password2", message="Passwords must match.")])
	password2 = PasswordField("Confirm Password", validators=[DataRequired()])
	submit = SubmitField("Register")

	def validate_email(self,  field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError("Email already registered.")

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError("Username already in use.")

class ChangePasswordForm(FlaskForm):
	old_password = PasswordField("Old Password", validators=[DataRequired()])
	password = PasswordField("New Password", validators=[DataRequired(), EqualTo("password2", message="Passwords must match.")])
	password2 = PasswordField("Confirm Password", validators=[DataRequired()])
	submit = SubmitField("Change Password")

class PasswordResetRequestForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
	submit = SubmitField("Reset Password")

class PasswordResetForm(FlaskForm):
	password = PasswordField("Password", validators=[DataRequired(), EqualTo("password2", message="Passwords must match.")])
	password2 = PasswordField("Confirm Password", validators=[DataRequired()])
	submit = SubmitField("Reset Password")

class ChangeEmailForm(FlaskForm):
	email = StringField("New Email", validators=[DataRequired(), Length(1, 64), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Update Email Address")

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError("This Email is already registered.")
