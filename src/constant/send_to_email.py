from flask_mail import Message,Mail
import os


def send_to_mail():
    msg = Message('Hello', sender='yourId@gmail.com', recipients=['someone1@gmail.com'])
    msg.body = "Hello Flask message sent from Flask-Mail"
    Mail.send_message()
    return "Sent"