#!/usr/bin/env python3
"""
Main file
"""
from flask import Flask, request, jsonify, make_response, abort, redirect
from auth import Auth


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home() -> str:
    return jsonify({"message": "Bienvenue"})


AUTH = Auth()


@app.route("/users", methods=["POST"])
def register_user():
    try:
        email = request.form.get("email")
        password = request.form.get("password")

        user = AUTH.register_user(email, password)
        return jsonify({"email": user.email, "message": "user created"}), 200

    except ValueError as e:
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if AUTH.valid_login(email, password):
        session_id = AUTH.create_session(email)
        response = make_response(
                    jsonify({"email": email, "message": "logged in"}), 200)
        response.set_cookie("session_id", session_id)
        return response
    else:
        abort(401)


@app.route("/sessions", methods=["DELETE"])
def logout():
    session_id = request.cookies.get("session_id", None)
    if session_id is None:
        abort(403)
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        AUTH.destroy_session(user.id)
        return redirect("/")
    else:
        abort(403)


@app.route("/profile", methods=["GET"])
def profile():
    session_id = request.cookies.get("session_id", None)
    if session_id is None:
        abort(403)
    user = AUTH.get_user_from_session_id(session_id)

    if user:
        return jsonify({"email": user.email}), 200
    else:
        abort(403)


@app.route("/reset_password", methods=["POST"])
def get_reset_password_token():
    """returns email and password reset token"""
    try:
        email = request.form.get("email")
    except KeyError:
        abort(403)
    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)
    return jsonify({"email": email, "reset_token": reset_token}), 200


@app.route("/reset_password", methods=["PUT"])
def update_password():
    """Updates users password
    """
    try:
        email = request.form.get("email")
        reset_token = request.form.get("reset_token")
        new_password = request.form.get("new_password")
    except KeyError:
        abort(403)
    try:
        AUTH.update_password(reset_token, new_password)
        return jsonify({"email": email, "message": "Password updated"}), 200
    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
