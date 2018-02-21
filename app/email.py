from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail
import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY', "SENDGRID_API_KEY"))


def send_async_email(app, mail):
	with app.app_context():
		response = sg.client.mail.send.post(request_body=mail.get())
		print(response.status_code)
		print(response.body)
		print(response.headers) 


def send_email(to, subject, template, **kwargs):
	app = current_app._get_current_object()
	from_email = Email(app.config['FLASKY_MAIL_SENDER'])
	to_email = Email(to)
	content = Content('text/html', render_template(template + '.html', **kwargs))
	mail = Mail(from_email, subject, to_email, content)
	thr = Thread(target=send_async_email, args=[app, mail])
	thr.start()
	return thr