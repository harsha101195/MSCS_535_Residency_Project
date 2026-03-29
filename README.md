# Residency Project

## Project 1

### Requirements
- Python 3.9+
- PostgreSQL
- psycopg

### Setup Database
1. Create database:
createdb companydb

2. Run schema:
psql -d companydb -f schema.sql

3. Update DB_CONFIG in server.py if needed

### Generate SSL Certificate
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes

### Run Server
python server.py

Server runs at:
https://localhost:8443

### Test APIs

#### Register
curl -k -X POST https://localhost:8443/register \
-H "Content-Type: application/json" \
-d '{"username":"user1","password":"pass123"}'

#### Login
curl -k -X POST https://localhost:8443/login \
-H "Content-Type: application/json" \
-d '{"username":"user1","password":"pass123"}'

### WEB UI

Registration and Login can also be done through the UI. To interact with the UI,
open a browser and do ```cmd + o```. Then select the index.html from project1 folder.

## Project 2

This project demonstrates common JavaScript security vulnerabilities and how to fix them. The application provides both **unsafe (vulnerable)** and **safe (secure)** implementations to clearly show the differences.


### Features

- Code injection via web applications (XSS)
- Dynamic evaluation using eval()
- Secure alternatives to eval()
- Content Security Policy (CSP)

### How to Run

```bash
npm install
node app.js
```

Open browser and go to:
http://localhost:3000

---

## Project 3 — Secure payment demo

Standalone demo under `project3/`: register, log in, record a **demo** payment (amount in cents + optional merchant note), and list payment history in PostgreSQL. This is **not** a real card integration: no card network, no PCI scope for PAN/CVV. It demonstrates **parameterized SQL** (SQL injection mitigation) and **safe browser rendering** via `innerText` for XSS mitigation when showing user-influenced text.

### Requirements

- Python 3.9+
- PostgreSQL
- `psycopg` (see `project3/requirements.txt`)

### Setup database

1. Create a database (example name: `project3db`).
2. Edit `project3/server.py` → `DB_CONFIG` (`host`, `dbname`, `user`, `password`) for your environment.
3. Apply the schema from the repository root:

   ```bash
   psql -U postgres -h 127.0.0.1 -d project3db -f project3/schema.sql
   ```

   Or from inside `project3`:

   ```bash
   cd project3
   psql -U postgres -h 127.0.0.1 -d project3db -f schema.sql
   ```

### Run the API and UI

```bash
cd project3
pip install -r requirements.txt
python server.py
```

The demo API listens on **HTTP** at `http://127.0.0.1:8444` (no TLS in this module; use TLS in production or terminate TLS at a reverse proxy).

Open `project3/index.html` in a browser (or serve the folder with a static server). The page uses `http://127.0.0.1:8444` as the API base; change the `API` constant in `index.html` if you change host or port.

### API endpoints (JSON `POST` bodies)

| Path | Purpose |
|------|---------|
| `/register` | `username`, `password` |
| `/login` | `username`, `password` |
| `/pay` | `username`, `password`, `amount_cents`, optional `merchant_note` |
| `/history` | `username`, `password` — returns `payments` array |

### Security notes

- **SQL injection:** All dynamic values use parameterized `cur.execute("... %s ...", (value,))` in `project3/server.py`. Do not concatenate user input into SQL strings.
- **XSS:** JSON from the API is displayed with **`innerText`** in `project3/index.html`. Using `innerHTML` with the same data could execute markup; a full application should also use **Content-Security-Policy** and server-side encoding when generating HTML.
- **Real payments:** Use a payment provider (tokenization, hosted fields), avoid secrets in source control, prefer session-based auth instead of sending the password on every request, and use HTTPS for all production traffic.
