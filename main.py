from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pyodbc
from datetime import datetime, date

app = FastAPI(title="Broadcast Contacts API")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection configuration
# IMPORTANT: Update these with your actual SQL Server credentials
DB_CONFIG = {
    'server': 'rsplgensql.retailware.in,41151',  # e.g., 'localhost' or 'server_ip'
    'database': 'AjitContacts',
    'username': 'rwgen',
    'password': 'RgeN#@$2025!99',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def get_db_connection():
    """Create and return a database connection"""
    conn_string = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_string)

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "API is running", "message": "Broadcast Contacts API"}


@app.get("/filter-options")
def get_filter_options():
    """
    Get distinct values for ContactName, Heading, and MobilePhone for filter dropdowns
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get distinct contact names
        cursor.execute("SELECT DISTINCT ContactName FROM vwFinalContacts WHERE ContactName IS NOT NULL ORDER BY ContactName")
        contact_names = [row[0] for row in cursor.fetchall()]
        
        # Get distinct headings
        cursor.execute("SELECT DISTINCT Heading FROM vwFinalContacts WHERE Heading IS NOT NULL ORDER BY Heading")
        headings = [row[0] for row in cursor.fetchall()]
        
        # Get distinct mobile numbers
        cursor.execute("SELECT DISTINCT MobilePhone FROM vwFinalContacts WHERE MobilePhone IS NOT NULL AND MobilePhone <> '' ORDER BY MobilePhone")
        mobile_numbers = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            "contact_names": contact_names,
            "headings": headings,
            "mobile_numbers": mobile_numbers
        }
    
    except Exception as e:
        return {"error": str(e)}, 500


@app.get("/contacts")
# def get_contacts(
#     contact_names: Optional[List[str]] = Query(None),
#     headings: Optional[List[str]] = Query(None),
#     mobile_numbers: Optional[List[str]] = Query(None),
#     created_date: Optional[date] = Query(None)
# ):
#     """
#     Get filtered contacts based on ContactName, Heading, MobilePhone, and CreatedAt date
#     All filters use AND logic
#     """
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         # Build the SQL query dynamically
#         query = "SELECT ContactName, Heading, MobilePhone, CreatedAt FROM vwFinalContacts WHERE 1=1"
#         params = []
        
#         # Add ContactName filter (if multiple values, use IN clause)
#         if contact_names and len(contact_names) > 0:
#             placeholders = ','.join(['?' for _ in contact_names])
#             query += f" AND ContactName IN ({placeholders})"
#             params.extend(contact_names)
        
#         # Add Heading filter (if multiple values, use IN clause)
#         if headings and len(headings) > 0:
#             placeholders = ','.join(['?' for _ in headings])
#             query += f" AND Heading IN ({placeholders})"
#             params.extend(headings)
        
#         # Add MobilePhone filter (if multiple values, use IN clause)
#         if mobile_numbers and len(mobile_numbers) > 0:
#             placeholders = ','.join(['?' for _ in mobile_numbers])
#             query += f" AND MobilePhone IN ({placeholders})"
#             params.extend(mobile_numbers)
        
#         # Add CreatedAt date filter (only date, ignore time)
#         if created_date:
#             query += " AND CAST(CreatedAt AS DATE) = ?"
#             params.append(created_date)
        
#         # Order by Heading, ContactName
#         query += " ORDER BY Heading, ContactName"
        
#         cursor.execute(query, params)
        
#         # Fetch all results
#         columns = [column[0] for column in cursor.description]
#         results = []
@app.get("/contacts")
def get_contacts(
    contact_names: Optional[List[str]] = Query(None),
    headings: Optional[List[str]] = Query(None),
    mobile_numbers: Optional[List[str]] = Query(None),
    created_date: Optional[date] = Query(None)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT ContactName, Heading, MobilePhone, CreatedAt FROM vwFinalContacts WHERE 1=1"
        params = []

        if contact_names:
            placeholders = ','.join(['?' for _ in contact_names])
            query += f" AND ContactName IN ({placeholders})"
            params.extend(contact_names)

        if headings:
            placeholders = ','.join(['?' for _ in headings])
            query += f" AND Heading IN ({placeholders})"
            params.extend(headings)

        if mobile_numbers:
            placeholders = ','.join(['?' for _ in mobile_numbers])
            query += f" AND MobilePhone IN ({placeholders})"
            params.extend(mobile_numbers)

        if created_date:
            query += " AND CAST(CreatedAt AS DATE) = ?"
            params.append(created_date)

        query += " ORDER BY Heading, ContactName"

        cursor.execute(query, params)

        results = []

        for row in cursor.fetchall():
            results.append({
                "ContactName": row.ContactName,
                "Heading": row.Heading,
                "MobilePhone": row.MobilePhone,
                "CreatedAt": row.CreatedAt.isoformat() if row.CreatedAt else None
            })

        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print("Contacts error:", str(e))
        return []

        
        # for row in cursor.fetchall():
        #     row_dict = {}
        #     for i, column in enumerate(columns):
        #         value = row[i]
        #         # Convert datetime to ISO format string for JSON serialization
        #         if isinstance(value, datetime):
        #             value = value.isoformat()
        #         row_dict[column] = value
        #     results.append(row_dict)
        for row in cursor.fetchall():
            row_dict = {
            "ContactName": row.ContactName,
            "Heading": row.Heading,
            "MobilePhone": row.MobilePhone,
            "CreatedAt": row.CreatedAt.isoformat() if row.CreatedAt else None
        }
        results.append(row_dict)
        
        cursor.close()
        conn.close()
        
        return results
    
    # except Exception as e:
    #     return {"error": str(e)}, 500
    except Exception as e:
        print("Filter options error:", str(e))
    return {
        "contact_names": [],
        "headings": [],
        "mobile_numbers": []
    }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
