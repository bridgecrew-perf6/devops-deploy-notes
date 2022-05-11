# This file is one way to use gunicorn for a factory pattern flask app
# I personally prefer this pattern for its ability to define production level flask app instances
# SOLUTION: https://stackoverflow.com/questions/25319690/how-do-i-run-a-flask-app-in-gunicorn-if-i-used-the-application-factory-pattern
from app import create_app

application = create_app()
