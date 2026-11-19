import os, datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import psycopg
from psycopg.rows import dict_row

app = FastAPI()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Nq_udC9Y4jNgLJc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    return psycopg.connect(database_url, row_factory=dict_row)

@app.on_event("startup")
def startup():
    conn = get_conn()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL PRIMARY KEY,
                    handle TEXT,
                    visited_at TIMESTAMP DEFAULT NOW(),
                    referrer TEXT
                )
            """)
        conn.commit()
        conn.close()

@app.post("/api/log")
async def log_visit(request: Request):
    data = await request.json()
    record = {
        "handle": data.get("handle", "unknown"),
        "referrer": data.get("referrer", "direct"),
    }
    conn = get_conn()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO visits (handle, referrer) VALUES (%s, %s)",
                (record["handle"], record["referrer"])
            )
        conn.commit()
        conn.close()
    return JSONResponse({"ok": True})

@app.get("/admin")
async def admin(password: str):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="wrong password")
    conn = get_conn()
    rows = []
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT handle, visited_at, referrer FROM visits ORDER BY visited_at DESC")
            rows = cur.fetchall()
        conn.close()
    html = "<h1>Visitor Log</h1><p><a href='/api/log?clear=1'>Clear all</a></p><br>"
    html += "<table border=1 cellpadding=6><tr><th>Handle</th><th>Time (UTC)</th><th>From</th></tr>"
    for r in rows:
        html += f"<tr><td>{r['handle']}</td><td>{r['visited_at']}</td><td>{r['referrer']}</td></tr>"
    html += "</table>"
    return HTMLResponse(html)

@app.get("/")
def root():
    return {"status": "ok"}
