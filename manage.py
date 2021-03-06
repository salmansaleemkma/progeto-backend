#!/usr/bin/env python
import os
from app import create_app, db
from flask_script import Manager, Shell
from flask_cors import CORS

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')

manager = Manager(app)


def make_shell_context():
    return dict(app=app)


@manager.command
def test():
    """Run Unit test"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
