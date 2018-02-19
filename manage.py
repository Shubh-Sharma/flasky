#!/usr/bin/env python
import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
	import coverage
	COV = coverage.coverage(branch=True, include='app/*')
	COV.start()

from app import create_app, db
from app.models import User, Role, Post
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand, upgrade

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

# @app.shell_context_processor
def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role, Post=Post)
	# return dict(db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

# @app.cli.command
@manager.command
def test(coverage=False):
	"""Run the unit tests."""
	if coverage and not os.environ.get('FLASK_COVERAGE'):
		import sys
		os.environ['FLASK_COVERAGE'] = '1'
		os.execvp(sys.executable, [sys.executable] + sys.argv)
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)
	if COV:
		COV.stop()
		COV.save()
		print('Coverage summary:')
		COV.report()
		basedir = os.path.abspath(os.path.dirname(__name__))
		covdir = os.path.join(basedir, 'tmp/coverage')
		COV.html_report(directory=covdir)
		print("HTML version: file://%s/index.html" % covdir)
		COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
	"""Start the application under the code profiler."""
	from werkzeug.contrib.profiler import ProfilerMiddleware
	app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
													profile_dir=profile_dir)
	app.run()


@manager.command
def deploy():
	"""Run deployment tasks."""

	# migrate database to latest version
	upgrade()

	# create user roles
	Role.insert_roles()

	# create self follow for all users
	User.add_self_follows()

if __name__ == '__main__':
	manager.run()