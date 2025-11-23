from flask import Flask, request, jsonify
import os
import jwt
import datetime
import time
from dotenv import load_dotenv

load_dotenv()
SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")

app = Flask(__name__)

users = [
    {"id": 1, "email": "admin@example.com", "password": "admin123", "role": "admin"},
    {"id": 2, "email": "user@example.com", "password": "user123", "role": "user"}
]


def require_auth(f):

    def wrap(*a, **kw):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        token = auth[7:]
        try:
            request.user = jwt.decode(token, SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except Exception:
            return jsonify({"error": "Invalid token"}), 401

        return f(*a, **kw)

    wrap.__name__ = f.__name__
    return wrap


def check_role(roles):

    def deco(f):
        @require_auth
        def wrap(*a, **kw):
            if request.user.get("role") not in roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*a, **kw)

        wrap.__name__ = f.__name__
        return wrap

    return deco


@app.post("/login")
def login():
    b = request.get_json() or {}

    u = next((x for x in users if x["email"] == b.get("email") and x["password"] == b.get("password")), None)

    if not u:
        return jsonify({"error": "Invalid credentials"}), 401

    exp_timestamp = time.time() + 900

    token_payload = {
        "sub": u["id"],
        "role": u["role"],
        "exp": exp_timestamp
    }

    token = jwt.encode(token_payload, SECRET, algorithm="HS256")

    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 900
    }


@app.get("/profile")
@require_auth
def profile():
    return {
        "user_id": request.user["sub"],
        "role": request.user["role"]
    }


@app.delete("/users/<int:id>")
@check_role(["admin"])
def delete_user(id):
    return {"message": f"User {id} deleted (demo)"}


if __name__ == "__main__":
    app.run(port=3000, debug=True)
