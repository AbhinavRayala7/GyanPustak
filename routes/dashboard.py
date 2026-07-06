from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from routes.auth import login_required
from database.connection import execute_query

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    role = session.get('role')
    user_id = session.get('user_id')
    
    if role == 'SuperAdmin':
        return superadmin_dashboard()
    elif role == 'Admin':
        return admin_dashboard()
    else:
        return student_dashboard(user_id)

def student_dashboard(user_id):
    try:
        # 1. Total borrowed books count (currently active)
        borrowed_count = execute_query(
            "SELECT COUNT(*) as cnt FROM BorrowedBooks WHERE UserID = ? AND Status IN ('Approved', 'Overdue')",
            (user_id,)
        )[0]['cnt']
        
        # 2. Active reservations count
        reservations_count = execute_query(
            "SELECT COUNT(*) as cnt FROM Reservations WHERE UserID = ? AND Status = 'Active'",
            (user_id,)
        )[0]['cnt']
        
        # 3. Open support tickets count
        tickets_count = execute_query(
            "SELECT COUNT(*) as cnt FROM SupportTickets WHERE UserID = ? AND Status IN ('Open', 'In Progress')",
            (user_id,)
        )[0]['cnt']
        
        # 4. Recent borrowing history list (top 5)
        recent_borrows = execute_query(
            """SELECT bb.BorrowID, b.Title, b.Author, bb.BorrowDate, bb.DueDate, bb.Status 
               FROM BorrowedBooks bb
               INNER JOIN Books b ON bb.BookID = b.BookID
               WHERE bb.UserID = ?
               ORDER BY bb.BorrowDate DESC LIMIT 5""",
            (user_id,)
        )
        
        return render_template(
            'dashboard_student.html',
            borrowed_count=borrowed_count,
            reservations_count=reservations_count,
            tickets_count=tickets_count,
            recent_borrows=recent_borrows
        )
    except Exception as e:
        return f"Dashboard error: {e}"

def admin_dashboard():
    try:
        # 1. Total unique book titles
        total_books = execute_query("SELECT COUNT(*) as cnt FROM Books")[0]['cnt']
        
        # 2. Total active issued books
        issued_books = execute_query(
            "SELECT COUNT(*) as cnt FROM BorrowedBooks WHERE Status IN ('Approved', 'Overdue')"
        )[0]['cnt']
        
        # 3. Pending borrow requests
        pending_borrows = execute_query(
            "SELECT COUNT(*) as cnt FROM BorrowedBooks WHERE Status = 'Pending'"
        )[0]['cnt']
        
        # 4. Open support tickets
        open_tickets = execute_query(
            "SELECT COUNT(*) as cnt FROM SupportTickets WHERE Status IN ('Open', 'In Progress')"
        )[0]['cnt']
        
        # 5. Pending bookstore orders
        pending_orders = execute_query(
            "SELECT COUNT(*) as cnt FROM Orders WHERE OrderStatus = 'Pending'"
        )[0]['cnt']
        
        return render_template(
            'dashboard_admin.html',
            total_books=total_books,
            issued_books=issued_books,
            pending_borrows=pending_borrows,
            open_tickets=open_tickets,
            pending_orders=pending_orders
        )
    except Exception as e:
        return f"Dashboard error: {e}"

def superadmin_dashboard():
    try:
        # 1. Total users
        total_users = execute_query("SELECT COUNT(*) as cnt FROM Users")[0]['cnt']
        
        # 2. Total admins
        total_admins = execute_query("SELECT COUNT(*) as cnt FROM Users WHERE Role = 'Admin'")[0]['cnt']
        
        # 3. Total active bookstore listings
        total_listings = execute_query("SELECT COUNT(*) as cnt FROM Listings WHERE ListingStatus = 'Active'")[0]['cnt']
        
        # 4. Total orders placed
        total_orders = execute_query("SELECT COUNT(*) as cnt FROM Orders")[0]['cnt']
        
        return render_template(
            'dashboard_super.html',
            total_users=total_users,
            total_admins=total_admins,
            total_listings=total_listings,
            total_orders=total_orders
        )
    except Exception as e:
        return f"Dashboard error: {e}"

# ==========================================
# Chart API Endpoints (JSON)
# ==========================================
@dashboard_bp.route('/api/charts/books-by-category')
@login_required
def chart_books_by_category():
    # Renders the number of books in each category
    query = """
        SELECT c.CategoryName, COUNT(b.BookID) as BookCount
        FROM Categories c
        LEFT JOIN Books b ON c.CategoryID = b.CategoryID
        GROUP BY c.CategoryName
    """
    try:
        data = execute_query(query)
        labels = [item['CategoryName'] for item in data]
        values = [item['BookCount'] for item in data]
        return jsonify({'labels': labels, 'values': values})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/charts/borrowing-trends')
@login_required
def chart_borrowing_trends():
    # Renders aggregate borrowing counts by category
    query = """
        SELECT c.CategoryName, COUNT(bb.BorrowID) as BorrowCount
        FROM Categories c
        INNER JOIN Books b ON c.CategoryID = b.CategoryID
        INNER JOIN BorrowedBooks bb ON b.BookID = bb.BookID
        GROUP BY c.CategoryName
    """
    try:
        data = execute_query(query)
        labels = [item['CategoryName'] for item in data]
        values = [item['BorrowCount'] for item in data]
        return jsonify({'labels': labels, 'values': values})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
