"""
Project 3: minimal "payment" API demonstrating the same defenses as Project 1:
- SQL injection: only parameterized queries (psycopg %s placeholders).
- XSS: API returns JSON; the client uses innerText (see index.html), not innerHTML.

This is a teaching demo, not PCI-compliant card processing (no real PAN/CVV).
"""

import hashlib
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

import psycopg

DB_CONFIG = {
    "host": "127.0.0.1",
    "dbname": "project3db",
    "user": "postgres",
    "password": "sreesh1998",
}


def get_db_connection():
    return psycopg.connect(**DB_CONFIG)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def send_json(handler, status: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class PaymentHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            send_json(self, 400, {"error": "Invalid JSON"})
            return

        routes = {
            "/register": self.handle_register,
            "/login": self.handle_login,
            "/pay": self.handle_pay,
            "/history": self.handle_history,
        }
        handler = routes.get(self.path)
        if not handler:
            send_json(self, 404, {"error": "Not found"})
            return
        handler(data)

    def handle_register(self, data):
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            send_json(self, 400, {"error": "Missing fields"})
            return
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hash_password(password)),
            )
            conn.commit()
            cur.close()
            conn.close()
            send_json(self, 201, {"ok": True, "message": "User registered"})
        except Exception as e:
            print("register:", e)
            send_json(self, 500, {"error": "Registration failed"})

    def _verify_user(self, username, password):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash FROM users WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return None
        user_id, stored = row
        if stored != hash_password(password):
            return None
        return user_id

    def handle_login(self, data):
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            send_json(self, 400, {"error": "Missing fields"})
            return
        if self._verify_user(username, password) is None:
            send_json(self, 401, {"error": "Invalid credentials"})
            return
        send_json(self, 200, {"ok": True, "message": "Login successful"})

    def handle_pay(self, data):
        username = data.get("username")
        password = data.get("password")
        amount = data.get("amount_cents")
        note = data.get("merchant_note") or ""
        if not username or not password or amount is None:
            send_json(self, 400, {"error": "Missing fields"})
            return
        try:
            amount_cents = int(amount)
        except (TypeError, ValueError):
            send_json(self, 400, {"error": "amount_cents must be an integer"})
            return
        if amount_cents <= 0:
            send_json(self, 400, {"error": "amount_cents must be positive"})
            return

        user_id = self._verify_user(username, password)
        if user_id is None:
            send_json(self, 401, {"error": "Invalid credentials"})
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO payments (user_id, amount_cents, merchant_note)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (user_id, amount_cents, note),
            )
            payment_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            send_json(
                self,
                200,
                {
                    "ok": True,
                    "payment_id": payment_id,
                    "message": "Payment recorded (demo only — no real card charge).",
                },
            )
        except Exception as e:
            print("pay:", e)
            send_json(self, 500, {"error": "Payment failed"})

    def handle_history(self, data):
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            send_json(self, 400, {"error": "Missing fields"})
            return
        user_id = self._verify_user(username, password)
        if user_id is None:
            send_json(self, 401, {"error": "Invalid credentials"})
            return
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, amount_cents, merchant_note, created_at
                FROM payments
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            payments = [
                {
                    "id": r[0],
                    "amount_cents": r[1],
                    "merchant_note": r[2] or "",
                    "created_at": r[3].isoformat() if r[3] else None,
                }
                for r in rows
            ]
            send_json(self, 200, {"ok": True, "payments": payments})
        except Exception as e:
            print("history:", e)
            send_json(self, 500, {"error": "Could not load history"})


if __name__ == "__main__":
    port = 8444
    httpd = HTTPServer(("127.0.0.1", port), PaymentHandler)
    print(f"Project 3 payment demo: http://127.0.0.1:{port}")
    print("Configure DB_CONFIG in server.py and run schema.sql against project3db.")
    httpd.serve_forever()
