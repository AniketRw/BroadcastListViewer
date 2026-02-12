from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional
import pyodbc
from datetime import datetime, date
import os

app = FastAPI(title="Broadcast Contacts API")

# CORS (production madhe specific domain theva)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# DATABASE CONFIG (ENV BASED)
# ==============================
DB_CONFIG = {
    "server": os.getenv("DB_SERVER"),
    "database": os.getenv("DB_NAME"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "driver": "{ODBC Driver 17 for SQL Server}",
}


def get_db_connection():
    conn_string = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )
    return pyodbc.connect(conn_string)


# ==============================
# SERVE FRONTEND
# ==============================
@app.get("/", response_class=FileResponse)
def serve_home():
    return FileResponse("index.html")


# ==============================
# FILTER OPTIONS
# ==============================
@app.get("/filter-options")
def get_filter_options():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT ContactName 
            FROM BroadcastContact 
            WHERE ContactName IS NOT NULL 
            ORDER BY ContactName
        """)
        contact_names = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT Heading 
            FROM BroadcastContact 
            WHERE Heading IS NOT NULL 
            ORDER BY Heading
        """)
        headings = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return {
            "contact_names": contact_names,
            "headings": headings
        }

    except Exception as e:
        return {"error": str(e)}, 500


# ==============================
# CONTACTS API
# ==============================
@app.get("/contacts")
def get_contacts(
    contact_names: Optional[List[str]] = Query(None),
    headings: Optional[List[str]] = Query(None),
    created_date: Optional[date] = Query(None),
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT ContactName, Heading, CreatedAt
            FROM BroadcastContact
            WHERE 1=1
        """
        params = []

        if contact_names:
            placeholders = ",".join(["?" for _ in contact_names])
            query += f" AND ContactName IN ({placeholders})"
            params.extend(contact_names)

        if headings:
            placeholders = ",".join(["?" for _ in headings])
            query += f" AND Heading IN ({placeholders})"
            params.extend(headings)

        if created_date:
            query += " AND CAST(CreatedAt AS DATE) = ?"
            params.append(created_date)

        query += " ORDER BY CreatedAt DESC"

        cursor.execute(query, params)

        columns = [column[0] for column in cursor.description]
        results = []

        for row in cursor.fetchall():
            row_dict = {}
            for i, column in enumerate(columns):
                value = row[i]
                if isinstance(value, datetime):
                    value = value.isoformat()
                row_dict[column] = value
            results.append(row_dict)

        cursor.close()
        conn.close()

        return results

    except Exception as e:
        return {"error": str(e)}, 500


# ==============================
# LOCAL RUN
# ==============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
