import smtplib
from os import access
from src.constant.http_status_code import *
from flask import Blueprint, app, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database import User, db
from flask_jwt_extended import create_access_token ,create_refresh_token ,jwt_required ,get_jwt_identity
from flasgger import swag_from
from flask_mail import Mail,Message as MailMessage
from src.constant.send_to_email import send_to_mail
import yagmail


auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post('/register')
@swag_from("./doc/auth/register.yaml")
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if len(password) < 6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': "User is too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)

    user = User(username=username, password=pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': "User created",
        'user': {
            'username': username, "email": email
        }

    }), HTTP_201_CREATED


@auth.post("/login")
@swag_from("./doc/auth/login.yaml")
def login():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password,password)
        if is_pass_correct:
            reflesh_token = create_refresh_token(user.id)
            access =  create_access_token(user.id)

            return jsonify(
                {
                    "access" : access,
                    "reflesh" : reflesh_token,
                    "username" : user.username,
                    "email" :  user.email
                }
            ),HTTP_200_OK

        else:
            return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED

@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    print(user_id)
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        "username" : user.username,
        "email" : user.email
    }),HTTP_200_OK



