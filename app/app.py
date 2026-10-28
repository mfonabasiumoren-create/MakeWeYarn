
import os

import psycopg
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from psycopg.rows import dict_row

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    """Connect to the MakeWeYarn PostgreSQL database."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5434"),
        dbname=os.getenv("DB_NAME", "makeweyarn"),
        user=os.getenv("DB_USER", "makeweyarn_user"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
        row_factory=dict_row,
    )


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "application": "MakeWeYarn",
        "message": "Telecom Service Operations Platform",
        "status": "running"
    }), 200


@app.route("/health", methods=["GET"])
def health():
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")

        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    except psycopg.Error:
        app.logger.exception("Database health check failed")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 503


@app.route("/subscribers", methods=["POST"])
def create_subscriber():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required."
        }), 400

    phone_number = data.get("phone_number")
    full_name = data.get("full_name")

    if not isinstance(phone_number, str) or not phone_number.strip():
        return jsonify({
            "error": "phone_number is required."
        }), 400

    if not isinstance(full_name, str) or not full_name.strip():
        return jsonify({
            "error": "full_name is required."
        }), 400

    phone_number = phone_number.strip()
    full_name = full_name.strip()

    if len(phone_number) > 20:
        return jsonify({
            "error": "phone_number must not exceed 20 characters."
        }), 400

    if len(full_name) > 120:
        return jsonify({
            "error": "full_name must not exceed 120 characters."
        }), 400

    try:
        with get_db_connection() as conn:
            subscriber = conn.execute(
                """
                INSERT INTO subscribers (phone_number, full_name)
                VALUES (%s, %s)
                RETURNING id, phone_number, full_name, status, created_at
                """,
                (phone_number, full_name),
            ).fetchone()

        subscriber["created_at"] = subscriber["created_at"].isoformat()

        return jsonify(subscriber), 201

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "error": "A subscriber with this phone number already exists."
        }), 409

    except psycopg.Error:
        app.logger.exception("Failed to create subscriber")
        return jsonify({
            "error": "Unable to create subscriber."
        }), 500


@app.route("/subscribers", methods=["GET"])
def list_subscribers():
    try:
        with get_db_connection() as conn:
            subscribers = conn.execute(
                """
                SELECT id, phone_number, full_name, status, created_at
                FROM subscribers
                ORDER BY id
                """
            ).fetchall()

        for subscriber in subscribers:
            subscriber["created_at"] = subscriber["created_at"].isoformat()

        return jsonify(subscribers), 200

    except psycopg.Error:
        app.logger.exception("Failed to retrieve subscribers")
        return jsonify({
            "error": "Unable to retrieve subscribers."
        }), 500


@app.route("/subscribers/<int:subscriber_id>", methods=["GET"])
def get_subscriber(subscriber_id):
    try:
        with get_db_connection() as conn:
            subscriber = conn.execute(
                """
                SELECT id, phone_number, full_name, status, created_at
                FROM subscribers
                WHERE id = %s
                """,
                (subscriber_id,),
            ).fetchone()

        if subscriber is None:
            return jsonify({
                "error": "Subscriber not found."
            }), 404

        subscriber["created_at"] = subscriber["created_at"].isoformat()

        return jsonify(subscriber), 200

    except psycopg.Error:
        app.logger.exception("Failed to retrieve subscriber")
        return jsonify({
            "error": "Unable to retrieve subscriber."
        }), 500

@app.route("/subscribers/<int:subscriber_id>/status", methods=["PATCH"])
def update_subscriber_status(subscriber_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required."
        }), 400

    status = data.get("status")

    if status not in ("active", "suspended"):
        return jsonify({
            "error": "status must be either 'active' or 'suspended'."
        }), 400

    try:
        with get_db_connection() as conn:
            subscriber = conn.execute(
                """
                UPDATE subscribers
                SET status = %s
                WHERE id = %s
                RETURNING id, phone_number, full_name, status, created_at
                """,
                (status, subscriber_id),
            ).fetchone()

        if subscriber is None:
            return jsonify({
                "error": "Subscriber not found."
            }), 404

        subscriber["created_at"] = subscriber["created_at"].isoformat()

        return jsonify(subscriber), 200

    except psycopg.Error:
        app.logger.exception("Failed to update subscriber status")
        return jsonify({
            "error": "Unable to update subscriber status."
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
