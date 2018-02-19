from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from ..email import send_email
from .. import db


@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed \
			and request.endpoint \
			and request.blueprint != 'auth' \
			and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(to=current_user.email, 
			   template='auth/email/confirm', 
			   subject='Confirm Your Account', 
			   user=current_user, token=token)
	flash('A new confirmation email has been sent to you.')
	return redirect(url_for('main.index'))

@auth.route('/login', methods=('GET', 'POST'))
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			next = request.args.get('next')
			if next is None or not next.startswith("/"):
				next = url_for('main.index')
			return redirect(next)
			# return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid Username or Password')
	return render_template("auth/login.html", form=form)


@auth.route('/register', methods=('GET','POST'))
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data, 
					username=form.username.data, 
					password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(to=user.email, 
				   subject="Confirm Your Account.", 
				   template='auth/email/confirm', 
				   user=user, token=token)
		flash('An Account Confirmation link has been sent to your email.')
		return redirect(url_for('auth.login'))
	return render_template("auth/register.html", form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		db.session.commit()
		flash('You have confirmed your account, Thanks!')
	else:
		flash("The confirmation link is invalid or has expired.")
	return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out')
	return redirect(url_for('main.index'))


@auth.route('/change-password', methods=('GET', 'POST'))
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			db.session.commit()
			flash("Your password has been updated.")
			return redirect(url_for('main.index'))
		else:
			flash("Invalid Password")
	return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=('GET','POST'))
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_token
			send_email(to=user.email, 
					   subject="Reset your password", 
					   template="auth/email/reset_password", 
					   user=user, token=token, next=request.args.get('next'))
		flash("An email with instructions to reset your password has been sent to you.")
		return redirect(url_for('auth.login'))
	return render_template("auth/reset_password.html", form=form)


@auth.route('/token/<token>', methods=('GET', 'POST'))
def reset_password(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		if User.reset_password(token, form.password.data):
			db.session.commit()
			flash("Your password has been updated.")
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template("auth/reset_password.html", form=form)


@auth.route('/change_email', methods=('GET','POST'))
@login_required
def change_email_request():
	form = ChangeEmailForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.password.data):
			new_email = form.email.data
			token = current_user.generate_email_change_token(new_email)
			send_email(to=new_email,
					   subject="Confirm your email address",
					   template="auth/email/change_email",
					   user=current_user, token=token)
			flash("An Email with instructions to confirm your email address has been sent to you.")
			return redirect(url_for('main.index'))
		else:
			flash("Invalid Email or Password.")
	return render_template("auth/change_email.html", form=form)

@auth.route('/change_email/<token>')
@login_required
def change_email(token):
	if current_user.change_email(token):
		db.session.commit()
		flash('Your email address has been updated.')
	else:
		flash('Invalid request')
	return redirect(url_for('main.index'))