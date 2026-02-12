# Broadcast Contacts Viewer

A simple web application to view and filter BroadcastContact records from MS SQL Server database.

## Features

- ✅ Multi-select searchable dropdowns for ContactName and Heading
- ✅ Date picker for CreatedAt filtering
- ✅ AND logic across all filters
- ✅ Displays all three columns: ContactName, Heading, CreatedAt
- ✅ Responsive table layout
- ✅ Real-time record count
- ✅ Clean, professional UI

## Technology Stack

- **Frontend**: HTML + JavaScript + jQuery + Select2
- **Backend**: FastAPI (Python)
- **Database**: MS SQL Server (upplus database, BroadcastContact table)

---

## Setup Instructions

### Prerequisites

1. **Python 3.8+** installed
2. **SQL Server ODBC Driver** installed
3. **SQL Server** with database `upplus` and table `BroadcastContact`

### Step 1: Install ODBC Driver (if not already installed)

**For Windows:**
- Download from: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- Install "ODBC Driver 17 for SQL Server"

**For Linux:**
```bash
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Database Connection

Edit `main.py` and update the database configuration:

```python
DB_CONFIG = {
    'server': 'localhost',        # Your SQL Server address
    'database': 'upplus',          # Database name (already set)
    'username': 'your_username',   # Your SQL Server username
    'password': 'your_password',   # Your SQL Server password
    'driver': '{ODBC Driver 17 for SQL Server}'
}
```

**Common driver options:**
- `{ODBC Driver 17 for SQL Server}` - Most common
- `{ODBC Driver 18 for SQL Server}` - Newer version
- `{SQL Server}` - Older systems
- `{SQL Server Native Client 11.0}` - Alternative

To check available drivers on your system:
```python
import pyodbc
print(pyodbc.drivers())
```

### Step 4: Update Frontend API URL

Edit `broadcast_contacts.html` and update the API URL (line 160):

```javascript
const API_BASE_URL = 'http://localhost:8000';  // Change to your server URL
```

**Examples:**
- Local development: `http://localhost:8000`
- Production: `http://your-server-ip:8000` or `https://yourdomain.com/api`

---

## Running the Application

### Start the FastAPI Backend

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Open the Frontend

Simply open `broadcast_contacts.html` in your web browser.

**Or serve it via a simple HTTP server:**

```bash
# Python 3
python -m http.server 8080

# Then open: http://localhost:8080/broadcast_contacts.html
```

---

## Deployment to Production Server

### Option 1: Simple Deployment

1. Copy files to your web server:
   - `main.py`
   - `requirements.txt`
   - `broadcast_contacts.html`

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run FastAPI with nohup (keeps running after logout):
   ```bash
   nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
   ```

4. Place `broadcast_contacts.html` in your web server directory (e.g., IIS, Apache, Nginx)

### Option 2: Using Systemd (Linux)

Create service file `/etc/systemd/system/broadcast-api.service`:

```ini
[Unit]
Description=Broadcast Contacts FastAPI
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/your/app
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable broadcast-api
sudo systemctl start broadcast-api
sudo systemctl status broadcast-api
```

### Option 3: Using IIS (Windows)

1. Install **HttpPlatformHandler** for IIS
2. Create `web.config` in your app directory:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="C:\Python39\python.exe"
                  arguments="-m uvicorn main:app --host 0.0.0.0 --port %HTTP_PLATFORM_PORT%"
                  stdoutLogEnabled="true"
                  stdoutLogFile=".\logs\python.log"
                  startupTimeLimit="60">
    </httpPlatform>
  </system.webServer>
</configuration>
```

---

## API Endpoints

### GET /filter-options

Returns distinct values for filters.

**Response:**
```json
{
  "contact_names": ["John Doe", "Jane Smith", ...],
  "headings": ["Marketing", "Sales", ...]
}
```

### GET /contacts

Returns filtered contacts.

**Query Parameters:**
- `contact_names` (optional, multiple): Filter by contact names
- `headings` (optional, multiple): Filter by headings
- `created_date` (optional): Filter by date (YYYY-MM-DD format)

**Example:**
```
GET /contacts?contact_names=John%20Doe&contact_names=Jane%20Smith&headings=Marketing&created_date=2024-02-12
```

**Response:**
```json
[
  {
    "ContactName": "John Doe",
    "Heading": "Marketing",
    "CreatedAt": "2024-02-12T10:30:00"
  },
  ...
]
```

---

## Troubleshooting

### ODBC Driver Issues

**Error:** "Data source name not found"
- Install ODBC Driver 17 for SQL Server
- Check available drivers: `pyodbc.drivers()`

### Connection Issues

**Error:** "Login failed for user"
- Verify username/password in `main.py`
- Check SQL Server allows remote connections
- Verify SQL Server authentication mode (Windows/Mixed)

**Error:** "Cannot open database 'upplus'"
- Verify database name is correct
- Check user has access to the database

### CORS Issues

**Error:** "CORS policy blocked"
- Ensure FastAPI CORS middleware is configured
- Update `allow_origins` in `main.py` to match your frontend URL

### Port Already in Use

```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Kill the process
taskkill /PID <process_id> /F  # Windows
kill -9 <process_id>           # Linux/Mac
```

---

## Security Notes

⚠️ **For Personal Use Only** - This application has:
- No authentication/authorization
- CORS set to allow all origins
- Direct database access

**For production/multi-user environments, add:**
- User authentication (OAuth, JWT)
- Role-based access control
- API rate limiting
- HTTPS/SSL
- Input validation and sanitization
- Restrict CORS to specific origins

---

## File Structure

```
.
├── main.py                    # FastAPI backend
├── requirements.txt           # Python dependencies
├── broadcast_contacts.html    # Frontend HTML page
└── README.md                  # This file
```

---

## License

Free to use for personal projects.

---

## Support

For issues or questions, check:
1. API documentation: `http://localhost:8000/docs`
2. Browser console for frontend errors (F12)
3. FastAPI logs in terminal

---

**Created for personal use - Simple, efficient, no-nonsense!** 🚀
