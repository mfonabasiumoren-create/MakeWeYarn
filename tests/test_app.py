
import unittest
from unittest.mock import patch

from app.app import app


class MakeWeYarnAPITests(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_endpoint(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["application"], "MakeWeYarn")
        self.assertEqual(response.get_json()["status"], "running")

    @patch("app.app.get_db_connection")
    def test_health_endpoint(self, mock_connection):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "healthy")
        self.assertEqual(response.get_json()["database"], "connected")
        mock_connection.assert_called_once()

    def test_create_subscriber_missing_phone_number(self):
        response = self.client.post(
            "/subscribers",
            json={"full_name": "Test Subscriber"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("phone_number", response.get_json()["error"])

    def test_create_subscriber_missing_full_name(self):
        response = self.client.post(
            "/subscribers",
            json={"phone_number": "+2348012345678"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("full_name", response.get_json()["error"])

    def test_create_subscriber_invalid_json(self):
        response = self.client.post(
            "/subscribers",
            data="not-json",
            content_type="text/plain"
        )

        self.assertEqual(response.status_code, 400)

    @patch("app.app.get_db_connection")
    def test_create_subscriber_success(self, mock_connection):
        from datetime import datetime, timezone
        from unittest.mock import MagicMock

        subscriber = {
            "id": 1,
            "phone_number": "+2348012345678",
            "full_name": "Test Subscriber",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
        }

        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = subscriber
        mock_connection.return_value.__enter__.return_value = mock_conn

        response = self.client.post(
            "/subscribers",
            json={
                "phone_number": "+2348012345678",
                "full_name": "Test Subscriber"
            }
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["id"], 1)
        self.assertEqual(response.get_json()["status"], "active")
        mock_conn.execute.assert_called_once()

    @patch("app.app.get_db_connection")
    def test_create_subscriber_duplicate_phone_number(self, mock_connection):
        import psycopg
        from unittest.mock import MagicMock

        mock_conn = MagicMock()
        mock_conn.execute.side_effect = psycopg.errors.UniqueViolation(
            "duplicate phone number"
        )
        mock_connection.return_value.__enter__.return_value = mock_conn

        response = self.client.post(
            "/subscribers",
            json={
                "phone_number": "+2348012345678",
                "full_name": "Test Subscriber"
            }
        )

        self.assertEqual(response.status_code, 409)
        self.assertIn("already exists", response.get_json()["error"])

    @patch("app.app.get_db_connection")
    def test_list_subscribers_success(self, mock_connection):
        from datetime import datetime, timezone
        from unittest.mock import MagicMock

        subscribers = [
            {
                "id": 1,
                "phone_number": "+2348012345678",
                "full_name": "Test Subscriber",
                "status": "active",
                "created_at": datetime.now(timezone.utc),
            }
        ]

        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = subscribers
        mock_connection.return_value.__enter__.return_value = mock_conn

        response = self.client.get("/subscribers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)
        self.assertEqual(
            response.get_json()[0]["phone_number"],
            "+2348012345678"
        )

    @patch("app.app.get_db_connection")
    def test_list_subscribers_empty(self, mock_connection):
        from unittest.mock import MagicMock

        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = []
        mock_connection.return_value.__enter__.return_value = mock_conn

        response = self.client.get("/subscribers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])


    @patch("app.app.get_db_connection")
    def test_get_subscriber_success(self, mock_connection):
        from datetime import datetime, timezone
        from unittest.mock import MagicMock

        subscriber = {
            "id": 1,
            "phone_number": "+2348012345678",
            "full_name": "Test Subscriber",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
        }

        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = subscriber
        mock_connection.return_value.__enter__.return_value = mock_conn

        response = self.client.get("/subscribers/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], 1)
        self.assertEqual(response.get_json()["status"], "active")

    @patch("app.app.get_db_connection")
    def test_get_subscriber_not_found(self, mock_connection):
        from unittest.mock import MagicMock

        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_connection.return_value.__enter__.return_value = mock_conn

        response = self.client.get("/subscribers/9999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json()["error"],
            "Subscriber not found."
        )

    @patch("app.app.get_db_connection")
    def test_suspend_subscriber_success(self, mock_connection):
        from datetime import datetime, timezone
        from unittest.mock import MagicMock

        subscriber = {
            "id": 1,
            "phone_number": "+2348012345678",
            "full_name": "Test Subscriber",
            "status": "suspended",
            "created_at": datetime.now(timezone.utc),
        }

        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = subscriber
        mock_connection.return_value.__enter__.return_value = mock_conn

        response = self.client.patch(
            "/subscribers/1/status",
            json={"status": "suspended"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "suspended")

    @patch("app.app.get_db_connection")
    def test_reactivate_subscriber_success(self, mock_connection):
        from datetime import datetime, timezone
        from unittest.mock import MagicMock

        subscriber = {
            "id": 1,
            "phone_number": "+2348012345678",
            "full_name": "Test Subscriber",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
        }

        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = subscriber
        mock_connection.return_value.__enter__.return_value = mock_conn

        response = self.client.patch(
            "/subscribers/1/status",
            json={"status": "active"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "active")

    def test_update_subscriber_invalid_status(self):
        response = self.client.patch(
            "/subscribers/1/status",
            json={"status": "blocked"}
        )

        self.assertEqual(response.status_code, 400)

    @patch("app.app.get_db_connection")
    def test_update_subscriber_not_found(self, mock_connection):
        from unittest.mock import MagicMock

        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_connection.return_value.__enter__.return_value = mock_conn

        response = self.client.patch(
            "/subscribers/9999/status",
            json={"status": "suspended"}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json()["error"],
            "Subscriber not found."
        )
    @patch("app.app.get_db_connection")
    def test_create_plan_success(self, mock_get_db_connection):
        from datetime import datetime, timezone
        from decimal import Decimal
        from unittest.mock import MagicMock

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            "id": 1,
            "name": "Starter Data Plan",
            "plan_type": "data",
            "price_ngn": Decimal("1500.00"),
            "data_allowance_mb": 2048,
            "voice_minutes": 0,
            "is_active": True,
            "created_at": datetime(2026, 10, 28, tzinfo=timezone.utc),
        }

        response = self.client.post(
            "/plans",
            json={
                "name": "Starter Data Plan",
                "plan_type": "data",
                "price_ngn": 1500,
                "data_allowance_mb": 2048,
                "voice_minutes": 0,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "Starter Data Plan")
        self.assertEqual(response.json["plan_type"], "data")
        self.assertEqual(response.json["price_ngn"], 1500.0)
    def test_create_plan_invalid_plan_type(self):
        response = self.client.post(
            "/plans",
            json={
                "name": "Invalid Plan",
                "plan_type": "unlimited",
                "price_ngn": 1500,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["error"],
            "plan_type must be data, voice, or combo."
        )
    @patch("app.app.get_db_connection")
    def test_create_plan_duplicate_name(self, mock_get_db_connection):
        import psycopg

        mock_conn = mock_get_db_connection.return_value.__enter__.return_value
        mock_conn.execute.side_effect = psycopg.errors.UniqueViolation(
            "duplicate plan name"
        )

        response = self.client.post(
            "/plans",
            json={
                "name": "Starter Data Plan",
                "plan_type": "data",
                "price_ngn": 1500,
                "data_allowance_mb": 2048,
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json["error"],
            "A plan with this name already exists."
        )
    def test_create_plan_negative_price(self):
        response = self.client.post(
            "/plans",
            json={
                "name": "Negative Price Plan",
                "plan_type": "data",
                "price_ngn": -500,
                "data_allowance_mb": 1024,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["error"],
            "price_ngn must be a non-negative number."
        )
    def test_create_plan_negative_data_allowance(self):
        response = self.client.post(
            "/plans",
            json={
                "name": "Invalid Data Plan",
                "plan_type": "data",
                "price_ngn": 1000,
                "data_allowance_mb": -100,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["error"],
            "data_allowance_mb must be a non-negative integer."
        )
    def test_create_plan_negative_voice_minutes(self):
        response = self.client.post(
            "/plans",
            json={
                "name": "Invalid Voice Plan",
                "plan_type": "voice",
                "price_ngn": 500,
                "voice_minutes": -30,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["error"],
            "voice_minutes must be a non-negative integer."
        )
    @patch("app.app.get_db_connection")
    def test_list_plans_success(self, mock_get_db_connection):
        from datetime import datetime, timezone
        from decimal import Decimal
        from unittest.mock import MagicMock

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {
                "id": 1,
                "name": "Starter Data Plan",
                "plan_type": "data",
                "price_ngn": Decimal("1500.00"),
                "data_allowance_mb": 2048,
                "voice_minutes": 0,
                "is_active": True,
                "created_at": datetime(2026, 10, 28, tzinfo=timezone.utc),
            }
        ]

        response = self.client.get("/plans")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["name"], "Starter Data Plan")
        self.assertEqual(response.json[0]["price_ngn"], 1500.0)
        self.assertEqual(response.json[0]["data_allowance_mb"], 2048)
    @patch("app.app.get_db_connection")
    def test_list_plans_empty(self, mock_get_db_connection):
        from unittest.mock import MagicMock

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        response = self.client.get("/plans")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    @patch("app.app.get_db_connection")
    def test_get_plan_success(self, mock_get_db_connection):
        from datetime import datetime, timezone
        from decimal import Decimal
        from unittest.mock import MagicMock

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            "id": 1,
            "name": "Starter Data Plan",
            "plan_type": "data",
            "price_ngn": Decimal("1500.00"),
            "data_allowance_mb": 2048,
            "voice_minutes": 0,
            "is_active": True,
            "created_at": datetime(2026, 10, 28, tzinfo=timezone.utc),
        }

        response = self.client.get("/plans/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], 1)
        self.assertEqual(response.json["name"], "Starter Data Plan")
        self.assertEqual(response.json["price_ngn"], 1500.0)
        self.assertEqual(response.json["data_allowance_mb"], 2048)

    @patch("app.app.get_db_connection")
    def test_get_plan_not_found(self, mock_get_db_connection):
        from unittest.mock import MagicMock

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        response = self.client.get("/plans/9999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json["error"],
            "Service plan not found."
        )

if __name__ == "__main__":
    unittest.main()
