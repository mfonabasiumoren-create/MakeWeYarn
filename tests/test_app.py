
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

if __name__ == "__main__":
    unittest.main()
