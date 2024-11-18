from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')  # Load configurations

    # Import and register blueprints
    from routes.routes import main
    app.register_blueprint(main)

    return app
