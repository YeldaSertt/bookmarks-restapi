from flask import Flask,jsonify,redirect,config
import os
from src.constant.http_status_code import *
from src.bookmarks import bookmarks
from src.auth import auth
from src.database import db, Bookmark
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.confing.swagger import swagger_config,template
from flask_mail import Mail,Message

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY"),
            MAIL_SERVER =  os.environ.get("MAIL_SERVER"),
            MAIL_PORT = os.environ.get("MAIL_PORT"),
            MAIL_USERNAME = os.environ.get("MAIL_USERNAME"),
            MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS"),
            MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL"),

            SWAGGER={
                'title': "Bookmarks API",
                'uiversion': 3
            }
        )
    else:
        app.config.from_mapping(test_config)

    @app.route("/hello")
    def say_hello():
        text = "hello word"
        return jsonify({"message": f"{text}"})


    app.db = app
    db.init_app(app)
    JWTManager(app)
    Mail(app)

    Swagger(app,config=swagger_config,template=template)

    app.register_blueprint(bookmarks)
    app.register_blueprint(auth)


    @app.get('/<short_url>')
    @swag_from('./doc/short_url.yaml')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visits = bookmark.visits+1
            db.session.commit()
            return redirect(bookmark.url)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR




    return app