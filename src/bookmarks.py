from os import access
from src.constant.http_status_code import *
from flask import Blueprint, app, request, jsonify
from src.database import Bookmark,db
from flask_jwt_extended import jwt_required ,get_jwt_identity
import validators
from flasgger import swag_from

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_bookmarks():
    curent_user = get_jwt_identity()
    if request.method =="POST":
        body =  request.json["body"]
        url = request.json["url"]

        if not validators.url(url):
            return jsonify({
                "error" : "Enter a valid url"
            }),HTTP_400_BAD_REQUEST
        """if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                "error" : "Email is exist"
            }),HTTP_409_CONFLICT"""

        bookmarks = Bookmark(body=body,url=url ,user_id = curent_user)
        db.session.add(bookmarks)
        db.session.commit()

        return jsonify({
            "id" : bookmarks.id,
            "body" : bookmarks.body,
            "url" : bookmarks.url,
            "short_url" : bookmarks.short_url,
            "user_id" :  bookmarks.user_id,
            "visits": bookmarks.visits,
            "create_date" : bookmarks.created_at,
            "updated_at" : bookmarks.updated_at
        }),HTTP_201_CREATED


@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmarks = Bookmark.query.filter(user_id = current_user , id=id).first()

    if not bookmarks:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
        "id": bookmarks.id,
        "body": bookmarks.body,
        "url": bookmarks.url,
        "short_url": bookmarks.short_url,
        "user_id": bookmarks.user_id,
        "visits": bookmarks.visits,
        "create_date": bookmarks.created_at,
        "updated_at": bookmarks.updated_at
    }), HTTP_201_CREATED

@bookmarks.delete("/delete/<int:id>")
@jwt_required()
def bookmarks_delete(id):
    current_user = get_jwt_identity()
    bookmarks= Bookmark.query.filter_by(user_id=current_user,id=id).first()
    if not bookmarks:
        return jsonify({"Item nnot found"}),HTTP_404_NOT_FOUND

    db.session.delete(bookmarks)
    db.session.commit()
    return jsonify({"message": "delete succes"}),HTTP_204_NO_CONTENT

@bookmarks.put("/put/<int:id>")
@bookmarks.patch("/patch/<int:id>")
@jwt_required()
def edit_bookmark(id):
    current_user = get_jwt_identity()

    body = request.json["body"]
    url = request.json["url"]

    if not validators.url("url"):
        return jsonify({"error" : "Enter a valid url"})
    bookmark = Bookmark.query.filter_by(user_id = current_user,id=id).first()
    bookmark.body = body
    bookmark.url = url
    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), HTTP_200_OK


@bookmarks.get("/stats")
@jwt_required()
@swag_from("./doc/bookmarks/stats.yaml")
def get_stats():
    current_user = get_jwt_identity()
    items = Bookmark.query.filter_by(user_id=current_user).all()

    data = []
    for item in items:
        new_link = {
           "visits" :  item.visits,
            "url" : item.url,
            "id" : item.id,
            "short_url" : item.short_url
        }
        data.append(new_link)

    return jsonify({"data": data}),HTTP_200_OK
