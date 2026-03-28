# Residency Project

## Project 1

### Requirements
- Python 3.9+
- PostgreSQL
- psycopg

Install requirements:
pip install -r requirements.txt

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
