
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

@app.route("/plans", methods=["POST"])
def create_plan():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required."
        }), 400

    name = data.get("name")
    plan_type = data.get("plan_type")
    price_ngn = data.get("price_ngn")
    data_allowance_mb = data.get("data_allowance_mb", 0)
    voice_minutes = data.get("voice_minutes", 0)

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "name is required."}), 400

    name = name.strip()

    if len(name) > 100:
        return jsonify({
            "error": "name must not exceed 100 characters."
        }), 400

    if plan_type not in ("data", "voice", "combo"):
        return jsonify({
            "error": "plan_type must be data, voice, or combo."
        }), 400

    if (
        isinstance(price_ngn, bool)
        or not isinstance(price_ngn, (int, float))
        or price_ngn < 0
    ):
        return jsonify({
            "error": "price_ngn must be a non-negative number."
        }), 400

    if (
        isinstance(data_allowance_mb, bool)
        or not isinstance(data_allowance_mb, int)
        or data_allowance_mb < 0
    ):
        return jsonify({
            "error": "data_allowance_mb must be a non-negative integer."
        }), 400

    if (
        isinstance(voice_minutes, bool)
        or not isinstance(voice_minutes, int)
        or voice_minutes < 0
    ):
        return jsonify({
            "error": "voice_minutes must be a non-negative integer."
        }), 400

    try:
        with get_db_connection() as conn:
            plan = conn.execute(
                """
                INSERT INTO plans (
                    name, plan_type, price_ngn,
                    data_allowance_mb, voice_minutes
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, name, plan_type, price_ngn,
                          data_allowance_mb, voice_minutes,
                          is_active, created_at
                """,
                (
                    name, plan_type, price_ngn,
                    data_allowance_mb, voice_minutes
                ),
            ).fetchone()

        plan["price_ngn"] = float(plan["price_ngn"])
        plan["created_at"] = plan["created_at"].isoformat()

        return jsonify(plan), 201

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "error": "A plan with this name already exists."
        }), 409

    except psycopg.Error:
        app.logger.exception("Failed to create service plan")
        return jsonify({
            "error": "Unable to create service plan."
        }), 500


@app.route("/plans", methods=["GET"])
def list_plans():
    try:
        with get_db_connection() as conn:
            plans = conn.execute(
                """
                SELECT id, name, plan_type, price_ngn,
                       data_allowance_mb, voice_minutes,
                       is_active, created_at
                FROM plans
                ORDER BY id
                """
            ).fetchall()

        for plan in plans:
            plan["price_ngn"] = float(plan["price_ngn"])
            plan["created_at"] = plan["created_at"].isoformat()

        return jsonify(plans), 200

    except psycopg.Error:
        app.logger.exception("Failed to retrieve service plans")
        return jsonify({
            "error": "Unable to retrieve service plans."
        }), 500

@app.route("/plans/<int:plan_id>", methods=["GET"])
def get_plan(plan_id):
    try:
        with get_db_connection() as conn:
            plan = conn.execute(
                """
                SELECT id, name, plan_type, price_ngn,
                       data_allowance_mb, voice_minutes,
                       is_active, created_at
                FROM plans
                WHERE id = %s
                """,
                (plan_id,),
            ).fetchone()

        if plan is None:
            return jsonify({
                "error": "Service plan not found."
            }), 404

        plan["price_ngn"] = float(plan["price_ngn"])
        plan["created_at"] = plan["created_at"].isoformat()

        return jsonify(plan), 200

    except psycopg.Error:
        app.logger.exception("Failed to retrieve service plan")
        return jsonify({
            "error": "Unable to retrieve service plan."
        }), 500

@app.route("/plans/<int:plan_id>/status", methods=["PATCH"])
def update_plan_status(plan_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required."
        }), 400

    is_active = data.get("is_active")

    if not isinstance(is_active, bool):
        return jsonify({
            "error": "is_active must be either true or false."
        }), 400

    try:
        with get_db_connection() as conn:
            plan = conn.execute(
                """
                UPDATE plans
                SET is_active = %s
                WHERE id = %s
                RETURNING id, name, plan_type, price_ngn,
                          data_allowance_mb, voice_minutes,
                          is_active, created_at
                """,
                (is_active, plan_id),
            ).fetchone()

        if plan is None:
            return jsonify({
                "error": "Service plan not found."
            }), 404

        plan["price_ngn"] = float(plan["price_ngn"])
        plan["created_at"] = plan["created_at"].isoformat()

        return jsonify(plan), 200

    except psycopg.Error:
        app.logger.exception("Failed to update service plan status")
        return jsonify({
            "error": "Unable to update service plan status."
        }), 500

@app.route("/plans/<int:plan_id>", methods=["PATCH"])
def update_plan(plan_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "A non-empty JSON object is required."
        }), 400

    allowed_fields = {
        "name",
        "plan_type",
        "price_ngn",
        "data_allowance_mb",
        "voice_minutes",
    }

    if not set(data).issubset(allowed_fields):
        return jsonify({
            "error": "One or more fields are not allowed."
        }), 400

    updates = {}

    if "name" in data:
        name = data["name"]

        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "name is required."}), 400

        name = name.strip()

        if len(name) > 100:
            return jsonify({
                "error": "name must not exceed 100 characters."
            }), 400

        updates["name"] = name

    if "plan_type" in data:
        if data["plan_type"] not in ("data", "voice", "combo"):
            return jsonify({
                "error": "plan_type must be data, voice, or combo."
            }), 400

        updates["plan_type"] = data["plan_type"]

    if "price_ngn" in data:
        price = data["price_ngn"]

        if (
            isinstance(price, bool)
            or not isinstance(price, (int, float))
            or price < 0
        ):
            return jsonify({
                "error": "price_ngn must be a non-negative number."
            }), 400

        updates["price_ngn"] = price

    if "data_allowance_mb" in data:
        allowance = data["data_allowance_mb"]

        if (
            isinstance(allowance, bool)
            or not isinstance(allowance, int)
            or allowance < 0
        ):
            return jsonify({
                "error": "data_allowance_mb must be a non-negative integer."
            }), 400

        updates["data_allowance_mb"] = allowance

    if "voice_minutes" in data:
        minutes = data["voice_minutes"]

        if (
            isinstance(minutes, bool)
            or not isinstance(minutes, int)
            or minutes < 0
        ):
            return jsonify({
                "error": "voice_minutes must be a non-negative integer."
            }), 400

        updates["voice_minutes"] = minutes

    fields_sql = ", ".join(
        f"{field} = %s" for field in updates
    )
    values = list(updates.values()) + [plan_id]

    try:
        with get_db_connection() as conn:
            plan = conn.execute(
                f"""
                UPDATE plans
                SET {fields_sql}
                WHERE id = %s
                RETURNING id, name, plan_type, price_ngn,
                          data_allowance_mb, voice_minutes,
                          is_active, created_at
                """,
                values,
            ).fetchone()

        if plan is None:
            return jsonify({
                "error": "Service plan not found."
            }), 404

        plan["price_ngn"] = float(plan["price_ngn"])
        plan["created_at"] = plan["created_at"].isoformat()

        return jsonify(plan), 200

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "error": "A plan with this name already exists."
        }), 409

    except psycopg.Error:
        app.logger.exception("Failed to update service plan")
        return jsonify({
            "error": "Unable to update service plan."
        }), 500

@app.route("/subscriptions", methods=["POST"])
def create_subscription():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required."
        }), 400

    subscriber_id = data.get("subscriber_id")
    plan_id = data.get("plan_id")

    if (
        isinstance(subscriber_id, bool)
        or not isinstance(subscriber_id, int)
        or subscriber_id <= 0
    ):
        return jsonify({
            "error": "subscriber_id must be a positive integer."
        }), 400

    if (
        isinstance(plan_id, bool)
        or not isinstance(plan_id, int)
        or plan_id <= 0
    ):
        return jsonify({
            "error": "plan_id must be a positive integer."
        }), 400

    try:
        with get_db_connection() as conn:
            subscriber = conn.execute(
                "SELECT id FROM subscribers WHERE id = %s",
                (subscriber_id,),
            ).fetchone()

            if subscriber is None:
                return jsonify({
                    "error": "Subscriber not found."
                }), 404

            plan = conn.execute(
                "SELECT id, is_active FROM plans WHERE id = %s",
                (plan_id,),
            ).fetchone()

            if plan is None:
                return jsonify({
                    "error": "Service plan not found."
                }), 404

            if not plan["is_active"]:
                return jsonify({
                    "error": "Cannot subscribe to an inactive service plan."
                }), 400

            subscription = conn.execute(
                """
                INSERT INTO subscriptions (subscriber_id, plan_id)
                VALUES (%s, %s)
                RETURNING id, subscriber_id, plan_id, status, created_at
                """,
                (subscriber_id, plan_id),
            ).fetchone()

        subscription["created_at"] = (
            subscription["created_at"].isoformat()
        )

        return jsonify(subscription), 201

    except psycopg.Error:
        app.logger.exception("Failed to create subscription")
        return jsonify({
            "error": "Unable to create subscription."
        }), 500

@app.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    try:
        with get_db_connection() as conn:
            subscriptions = conn.execute(
                """
                SELECT
                    s.id,
                    s.subscriber_id,
                    sub.full_name AS subscriber_name,
                    sub.phone_number,
                    s.plan_id,
                    p.name AS plan_name,
                    s.status,
                    s.created_at
                FROM subscriptions AS s
                JOIN subscribers AS sub
                    ON s.subscriber_id = sub.id
                JOIN plans AS p
                    ON s.plan_id = p.id
                ORDER BY s.id
                """
            ).fetchall()

        for subscription in subscriptions:
            subscription["created_at"] = (
                subscription["created_at"].isoformat()
            )

        return jsonify(subscriptions), 200

    except psycopg.Error:
        app.logger.exception("Failed to retrieve subscriptions")
        return jsonify({
            "error": "Unable to retrieve subscriptions."
        }), 500

@app.route("/subscriptions/<int:subscription_id>", methods=["GET"])
def get_subscription(subscription_id):
    try:
        with get_db_connection() as conn:
            subscription = conn.execute(
                """
                SELECT
                    s.id,
                    s.subscriber_id,
                    sub.full_name AS subscriber_name,
                    sub.phone_number,
                    s.plan_id,
                    p.name AS plan_name,
                    s.status,
                    s.created_at
                FROM subscriptions AS s
                JOIN subscribers AS sub
                    ON s.subscriber_id = sub.id
                JOIN plans AS p
                    ON s.plan_id = p.id
                WHERE s.id = %s
                """,
                (subscription_id,),
            ).fetchone()

        if subscription is None:
            return jsonify({
                "error": "Subscription not found."
            }), 404

        subscription["created_at"] = (
            subscription["created_at"].isoformat()
        )

        return jsonify(subscription), 200

    except psycopg.Error:
        app.logger.exception("Failed to retrieve subscription")
        return jsonify({
            "error": "Unable to retrieve subscription."
        }), 500

@app.route(
    "/subscriptions/<int:subscription_id>/status",
    methods=["PATCH"],
)
def update_subscription_status(subscription_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required."
        }), 400

    status = data.get("status")

    if status not in ("active", "cancelled"):
        return jsonify({
            "error": "status must be either 'active' or 'cancelled'."
        }), 400

    try:
        with get_db_connection() as conn:
            subscription = conn.execute(
                """
                UPDATE subscriptions
                SET status = %s
                WHERE id = %s
                RETURNING id, subscriber_id, plan_id, status, created_at
                """,
                (status, subscription_id),
            ).fetchone()

        if subscription is None:
            return jsonify({
                "error": "Subscription not found."
            }), 404

        subscription["created_at"] = (
            subscription["created_at"].isoformat()
        )

        return jsonify(subscription), 200

    except psycopg.Error:
        app.logger.exception("Failed to update subscription status")
        return jsonify({
            "error": "Unable to update subscription status."
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
