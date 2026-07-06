# Gyan Pustak - Full-Stack Library Management System & Bookstore

Gyan Pustak is a production-quality, role-based full-stack web application designed for managing college campus library books, peer-to-peer textbook trading, and student support. 

Built using **Python (Flask)** for the backend, **HTML5/CSS3/Vanilla JS** for the frontend, and **Microsoft SQL Server / SQLite** for the database, this project is designed to be developer-friendly, zero-config on first launch, and optimized for campus trades.

---

##  Key Modules & Features

1.  **Multi-Role Access Control:**
    *   **Student:** Register and search the catalog, request borrows/reserves, add textbooks to a cart, order books from peers, and log customer support tickets.
    *   **Admin (Librarian):** Manage book catalogs (CRUD), authorize textbook borrow requests, process bookstore customer orders, and resolve customer support threads.
    *   **Super Admin:** Edit user details, create Admin accounts, deactivate suspended accounts, and view global system analytics.
2.  **Library Circulation Flow:** Request book borrows or place reservations if books are out-of-stock. Returns instantly update inventory.
3.  **Online Bookstore Shopping Cart:** Browse textbooks listed by peers. Add items, update quantities in a session-backed cart, and place orders.
4.  **Customer Support Ticketing:** Thread-based ticketing system styled like a chat window for students to report issues and admins to reply.
5.  **Analytics & Dynamic Charting:** Displays books-by-category and borrowing trends using Chart.js.
6.  **Exportable Reports:** Export active inventory list, borrowing records, and transaction logs directly to multi-sheet Microsoft Excel spreadsheets. Supports native browser Print-to-PDF reports.

---

## 🛠️ Tech Stack

*   **Backend:** Python 3.x, Flask
*   **Database:** Microsoft SQL Server (Primary, via `pyodbc`) with auto-fallback to SQLite3 (Local file-based)
*   **Frontend:** HTML5, Vanilla CSS3 (custom responsive stylesheet with CSS variables for Light/Dark Mode), Vanilla JS
*   **Analytics:** Chart.js (via JSON endpoints)
*   **Reports:** `openpyxl` (dynamic Excel generation)

---

##  Repository Structure

```bash
D:\GyanPustak/
├── app.py                # Main entry point: Flask app initialization
├── config.py             # App configuration (secret key, DB connection string)
├── requirements.txt      # Python dependencies (Flask, pyodbc, openpyxl)
├── database/
│   ├── connection.py     # Database connection manager (SQL Server / SQLite fallback)
│   ├── schema.sql        # Table structures (CREATE TABLE)
│   └── seed_data.sql     # Seed user accounts, books, and listings
├── routes/
│   ├── auth.py           # Login, registration, password hashing
│   ├── dashboard.py      # Dashboards for Student, Admin, and Super Admin
│   ├── library.py        # Catalog search, borrow requests, reservations
│   ├── store.py          # Bookstore, cart, order placement
│   ├── tickets.py        # Support ticket conversation threads
│   ├── admin.py          # Book CRUD, order status, ticket replies, user control
│   └── reports.py        # Excel report exports
├── static/
│   ├── css/
│   │   └── style.css     # Responsive custom stylesheet (variables, layouts)
│   └── js/
│       └── main.js       # Dark mode, modal overlay controls, Chart.js loaders
└── templates/            # HTML structure files
```

---

## 🚀 Local Installation & Setup

Gyan Pustak features an **automatic SQLite database initialization**. If it cannot connect to a Microsoft SQL Server, it will silently create `database/gyanpustak.db`, run DDL schemas, and inject test users automatically. **You can launch the project out-of-the-box in 3 steps!**

### Step 1: Install Dependencies
Open your terminal (Command Prompt, PowerShell, or Bash) and run:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Database (Optional)
If you want to use **Microsoft SQL Server**:
1. Connect to your instance and create a database named `GyanPustak`.
2. Open `config.py` and verify `SQL_SERVER_CONN` is correct for your local instance (e.g. check your server name and verify SQL Server ODBC Driver version).
3. If SQL Server is down or drivers are missing, the system automatically uses SQLite.

### Step 3: Run the Application
Start the local server:
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 🔑 Test Credentials (Seeded Users)
you can find the login credentials in the seed.db files
