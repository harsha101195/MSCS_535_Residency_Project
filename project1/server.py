import ssl
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import psycopg
import hashlib

DB_CONFIG = {
    "host": "127.0.0.1",
    "dbname": "companydb",
    "user": "sreeharsha",
    "password": ""
}

def get_db_connection():
    return psycopg.connect(**DB_CONFIG)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class SimpleHandler(BaseHTTPRequestHandler):

    #Handle CORS preflight
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    #Handle POST requests
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except:
            self.send_response(400)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        if self.path == "/register":
            self.handle_register(data)

        elif self.path == "/login":
            self.handle_login(data)

        else:
            self.send_response(404)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

    #Register user
    def handle_register(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            self.send_response(400)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"Missing fields")
            return

        password_hash = hash_password(password)

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )

            conn.commit()
            cur.close()
            conn.close()

            self.send_response(201)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"User registered")

        except Exception as e:
            print("ERROR:", e)
            self.send_response(500)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"Error")

    #Login user
    def handle_login(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            self.send_response(400)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"Missing fields")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            #Parameterized query -> prevents SQL injection
            cur.execute(
                "SELECT password_hash FROM users WHERE username = %s",
                (username,)
            )

            result = cur.fetchone()
            cur.close()
            conn.close()

            if not result:
                self.send_response(401)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b"Invalid credentials")
                return

            stored_hash = result[0]

            if stored_hash == hash_password(password):
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b"Login successful")
            else:
                self.send_response(401)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b"Invalid credentials")

        except Exception as e:
            print("ERROR:", e)
            self.send_response(500)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"Error")


#Start HTTPS server
httpd = HTTPServer(("0.0.0.0", 8443), SimpleHandler)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("Secure server running on https://localhost:8443")
httpd.serve_forever()