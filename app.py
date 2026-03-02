"""
VULNERABLE DEMO APP — DO NOT DEPLOY
This file is intentionally insecure for security training / detection testing.
Run locally only.
"""

from flask import Flask, request, make_response
import sqlite3
import os
import subprocess
import requests
import json
import base64
import hmac
import hashlib
from urllib.parse import unquote

app = Flask(__name__)

# --- Hardcoded secrets (BAD) ---
APP_SECRET = "super-secret-dev-key"
JWT_SECRET = "jwt-secret-123"

DB_PATH = "demo.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, owner TEXT, note TEXT);")
    # Default user (BAD: weak creds, plain text)
    c.execute("INSERT OR IGNORE INTO users(id, username, password) VALUES (1,'admin','admin');")
    conn.commit()
    conn.close()

init_db()

# --- Naive normalization (still bypassable) ---
def normalize(s: str) -> str:
    return (s or "").lower().replace("_", " ").replace("-", " ").replace(".", " ")

# --- Weak “JWT-like” token (BAD: homegrown crypto / no exp / weak validation) ---
def make_token(username: str) -> str:
    payload = json.dumps({"u": username}).encode()
    sig = hmac.new(JWT_SECRET.encode(), payload, hashlib.sha256).hexdigest().encode()
    return base64.urlsafe_b64encode(payload + b"." + sig).decode()

def verify_token(token: str) -> str | None:
    try:
        raw = base64.urlsafe_b64decode(token.encode())
        payload, sig = raw.split(b".", 1)
        expected = hmac.new(JWT_SECRET.encode(), payload, hashlib.sha256).hexdigest().encode()
        if sig == expected:
            data = json.loads(payload.decode())
            return data.get("u")
    except Exception:
        return None
    return None

# --- Logging sensitive data (BAD) ---
@app.before_request
def log_everything():
    # This will log passwords/tokens/PII if provided
    print("[REQ]", request.method, request.path, "args=", dict(request.args), "form=", dict(request.form))

# ---------------------------
# 1) SQL Injection (BAD)
# ---------------------------
@app.get("/login")
def login():
    # Example: /login?u=admin&p=admin
    u = request.args.get("u", "")
    p = request.args.get("p", "")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # VULN: string formatting into SQL
    q = f"SELECT username FROM users WHERE username='{u}' AND password='{p}';"
    row = c.execute(q).fetchone()
    conn.close()

    if row:
        resp = make_response("ok")
        resp.set_cookie("session", make_token(row[0]))  # BAD cookie flags not set
        return resp
    return "no", 401

# ---------------------------
# 2) Stored XSS (BAD)
# ---------------------------
@app.post("/notes")
def add_note():
    owner = request.cookies.get("session", "")
    user = verify_token(owner) or "anon"

    note = request.form.get("note", "")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # VULN: store arbitrary HTML/JS
    c.execute("INSERT INTO notes(owner, note) VALUES (?, ?);", (user, note))
    conn.commit()
    conn.close()

    return "saved"

@app.get("/notes")
def list_notes():
    owner = request.cookies.get("session", "")
    user = verify_token(owner) or "anon"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    rows = c.execute("SELECT note FROM notes WHERE owner=?;", (user,)).fetchall()
    conn.close()

    # VULN: reflect stored note without escaping
    html = "<h1>Your notes</h1>"
    for (n,) in rows:
        html += f"<div class='note'>{n}</div>"
    return html

# ---------------------------
# 3) SSRF (BAD)
# ---------------------------
@app.get("/fetch")
def fetch():
    # Example: /fetch?url=http://example.com
    url = request.args.get("url", "")
    # VULN: no allowlist, can reach internal services/metadata endpoints
    r = requests.get(url, timeout=2)
    return (r.text[:2000], 200, {"Content-Type": "text/plain; charset=utf-8"})

# ---------------------------
# 4) Command Injection (BAD)
# ---------------------------
@app.get("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # VULN: shell=True with user input
    out = subprocess.check_output(f"ping -c 1 {host}", shell=True, stderr=subprocess.STDOUT, timeout=2)
    return (out, 200, {"Content-Type": "text/plain; charset=utf-8"})

# ---------------------------
# 5) Path Traversal (BAD)
# ---------------------------
@app.get("/read")
def read_file():
    # Example: /read?path=README.md
    path = request.args.get("path", "README.md")
    path = unquote(path)

    # VULN: user controls filesystem path
    with open(path, "rb") as f:
        data = f.read(2000)
    return (data, 200, {"Content-Type": "application/octet-stream"})

# ---------------------------
# 6) “Sensitive prompt detector” done wrong (bypassable, noisy)
# ---------------------------
SENSITIVE_KEYWORDS = (
    "ssn", "social security", "credit card", "cvv", "passport", "medical history",
    "password", "api key", "access token", "private key", "iban", "routing number",
    "dni", "rut", "cedula", "date of birth", "phone number", "home address",
)

@app.post("/analyze")
def analyze():
    text = request.form.get("text", "")
    n = normalize(text)

    hits = [k for k in SENSITIVE_KEYWORDS if k in n]  # VULN-ish: simplistic substring match
    # BAD: returns matched keywords (information disclosure / easy to tune bypass)
    return {"hits": hits, "count": len(hits)}

# ---------------------------
# 7) Debug mode (BAD)
# ---------------------------
if __name__ == "__main__":
    # BAD: debug=True exposes debugger if misconfigured / deployed
    app.run(host="0.0.0.0", port=5000, debug=True)