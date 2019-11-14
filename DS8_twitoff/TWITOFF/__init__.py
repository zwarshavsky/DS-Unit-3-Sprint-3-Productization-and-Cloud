"""Entry point for our twitoff flask app"""

from .app import create_app

#APP is global variable
APP = create_app()

#run this in terminal with FLASK_APP=TWITOFF:APP flask run
