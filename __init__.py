import os
from flask import Flask
import db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev',
                            DATABASE=(app.instance_path, 'moneykeeper.sql'),
                            )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load test config if exists
        app.config.from_mapping(test_config)

    # ensure that directory is exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # simple webpage
    @app.route('/welcome')
    def welcome() -> str:
        return 'Welcome to Moneykeeper'

    db.init_app(app)

    return app
