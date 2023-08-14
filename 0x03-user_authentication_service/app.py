#!/usr/bin/env python3
"""
Main file
"""
from flask import Flask, jsonify, request
from auth import Auth

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
