# application.__init__.py
"""Initialize app."""

from flask import Flask, jsonify, request, session
from flask_login import login_user, LoginManager
from flask_bootstrap import Bootstrap
from flask_marshmallow import Marshmallow
from config import DevelopmentConfig, ProductionConfig, TestingConfig
import os
 
ma = Marshmallow()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from flask import session
    from .model.sessions import Session
    return Session( name=session.get('name'), email=session.get('email'), role=session.get('role'), user_id=session.get('user_id'))


def create_app():
    """
    Construct the core app object.
    """
    app = Flask(__name__, instance_relative_config=False)


    env_config = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }.get(os.getenv('FLASK_ENV', 'development'), DevelopmentConfig)

    # Load the configuration based on the environment
    config_name = os.getenv('FLASK_CONFIG', 'DevelopmentConfig')  # Default to DevelopmentConfig
    app.config.from_object(f'config.{config_name}')

    # Error handling for 404 and 405
    @app.errorhandler(404)
    def not_found_404(error=None):
        message = {
            'status': 404,
            'message': 'Not found! This URL: ' + request.url + ' is not provided!'
        }
        return jsonify(message), 404

    @app.errorhandler(405)
    def not_found_405(error=None):
        message = {
            'status': 405,
            'message': 'Method not allowed at: ' + request.url
        }
        return jsonify(message), 405

    login_manager.init_app(app)
    login_manager.login_view = 'site.loginPage'
    Bootstrap(app)

    with app.app_context():
        from .api_user import user_api
        from .api_chat import chat_api as chatsite
        from .homesite import site 

        # Register Blueprints
        app.register_blueprint(site)
        app.register_blueprint(user_api)
        app.register_blueprint(chatsite)

    return app
