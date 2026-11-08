# 📚 Gyan Pustak - Library Management & Campus Bookstore

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask_3.0-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20MSSQL-00599C.svg?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Frontend](https://img.shields.io/badge/Frontend-HTML5%20%7C%20CSS3%20%7C%20JS-E34F26.svg?logo=html5&logoColor=white)](https://developer.mozilla.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Gyan Pustak** is a full-stack, role-based web application designed for college campuses. It combines traditional **library circulation management** with a **peer-to-peer textbook marketplace** and an **integrated support ticketing system**.

Built with a zero-config setup, the system runs automatically out-of-the-box using local SQLite, while also supporting enterprise Microsoft SQL Server environments.

---

## ✨ Key Features & Modules

### 🎓 1. Student Portal
* **Library Catalog:** Real-time search across titles, authors, and categories. Borrow books or reserve out-of-stock titles.
* **Peer-to-Peer Bookstore:** Browse used textbooks listed by fellow students with condition tags (*Like New*, *Good*, *Acceptable*).
* **Shopping Cart & Orders:** Session-backed cart, checkout flow, and live order tracking.
* **Support Center:** Raise ticket threads to communicate directly with librarians.

### 🛡️ 2. Admin (Librarian) Portal
* **Circulation Control:** Review and approve/reject book borrow and reservation requests.
* **Inventory Management:** Full CRUD operations to add, update, and manage book stock.
* **Order Processing:** Update order fulfillment statuses (*Pending*, *Shipped*, *Delivered*).
* **Ticketing Desk:** Real-time message thread interface to respond to student support queries.

### 👑 3. Super Admin & Analytics
* **Interactive Dashboards:** Visualized borrowing trends and popular categories powered by Chart.js.
* **User Control:** Manage user statuses (Active/Suspended) and assign administrative privileges.
* **Excel Data Exports:** Export inventory records, borrow logs, and transactions into multi-sheet `.xlsx` workbooks via `openpyxl`.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python 3.9+, Flask 3.0.3, Jinja2 Templates |
| **Database** | SQLite3 (Auto-initialized local storage) / Microsoft SQL Server (via `pyodbc`) |
| **Frontend** | Responsive Vanilla CSS3 (Custom design system with Dark/Light theme), Vanilla JavaScript |
| **Data Analytics** | Chart.js (REST endpoints) |
| **Reporting** | `openpyxl` (Dynamic multi-sheet Excel report generator) |

---

## 📁 Repository Structure

```bash
GyanPustak/
├── app.py                # Main Flask application entry point
├── config.py             # App configuration (secret keys, DB paths)
├── requirements.txt      # Python dependencies
├── database/
│   ├── connection.py     # Resilient DB connection manager (MSSQL / SQLite fallback)
│   ├── schema.sql        # Database table DDL definitions
│   └── seed_data.sql     # Initial seed users, books, and marketplace listings
├── routes/
│   ├── auth.py           # Authentication, role verification, registration
│   ├── dashboard.py      # Role-based dashboards (Student, Admin, Super Admin)
│   ├── library.py        # Library search, borrow, and reservation handlers
│   ├── store.py          # Bookstore, cart session, order checkout
│   ├── tickets.py        # Support ticketing threads
│   ├── admin.py          # Book management, order status, ticket moderation
│   └── reports.py        # Dynamic Excel report generation
├── static/
│   ├── css/style.css     # Responsive design system & themes
│   └── js/main.js        # UI modals, theme toggler, Chart.js integrations
└── templates/            # Jinja2 HTML templates
```

---

## 🚀 Quick Start & Installation

Gyan Pustak features **automatic database initialization**. On first launch, if Microsoft SQL Server is not detected, it automatically creates `database/gyanpustak.db`, executes the schema, and populates seed data.

### 1. Clone the Repository
```bash
git clone https://github.com/AbhinavRayala7/GyanPustak.git
cd GyanPustak
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your web browser.

---

## 🔑 Demo Test Accounts

The database comes pre-seeded with test accounts for each role so anyone testing the project can log in immediately.

> **Password for all demo accounts:** `password123`

| Role | Username / Email | Password | "Login As" Role Selection | Capabilities to Test |
| :--- | :--- | :--- | :--- | :--- |
| **Student** | `abhinav` or `abhinav@gyanpustak.in` | `password123` | **Student / User** | Borrow books, buy used textbooks, cart & checkout, open support tickets |
| **Student (Alt)** | `student_rahul` | `password123` | **Student / User** | Alternative student profile |
| **Admin (Librarian)** | `admin` or `admin@gyanpustak.in` | `password123` | **Librarian Admin** | Approve book borrow requests, add/edit books, answer support tickets |
| **Super Admin** | `superadmin` or `superadmin@gyanpustak.in` | `password123` | **Super Admin** | View analytics graphs, manage users, export Excel reports |

*(You can also register a brand-new student account directly from the **Register** page!)*

---

## 💾 Database Architecture

* **Zero-Config Fallback (Default):** Runs immediately using standard Python `sqlite3`. Requires no external database installations or drivers.
* **Microsoft SQL Server (Optional):** To use SQL Server in production or lab environments, set up a database named `GyanPustak` and configure connection details in `config.py`.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
