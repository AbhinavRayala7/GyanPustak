from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required, role_required
from database.connection import execute_query
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Helper to verify permissions
def is_admin():
    return session.get('role') in ['Admin', 'SuperAdmin']

# ==========================================
# 1. Book & Inventory Management (CRUD)
# ==========================================
@admin_bp.route('/admin/books', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'SuperAdmin'])
def manage_books():
    if request.method == 'POST':
        # Create or update book
        book_id = request.form.get('book_id') # Present if editing
        isbn = request.form.get('isbn').strip()
        title = request.form.get('title').strip()
        author = request.form.get('author').strip()
        edition = request.form.get('edition').strip()
        publisher = request.form.get('publisher').strip()
        year = request.form.get('publication_year')
        category_id = request.form.get('category_id')
        total_copies = request.form.get('total_copies')
        
        # Simple Validation
        if not isbn or not title or not author or not category_id:
            flash("ISBN, Title, Author, and Category are required.", "warning")
            return redirect(url_for('admin.manage_books'))
            
        try:
            if book_id:
                # Update existing book
                # Calculate available copies adjustment based on total copies change
                old_book = execute_query("SELECT TotalCopies, AvailableCopies FROM Books WHERE BookID = ?", (book_id,))[0]
                diff = int(total_copies) - old_book['TotalCopies']
                new_available = old_book['AvailableCopies'] + diff
                if new_available < 0:
                     new_available = 0
                     
                execute_query(
                    """UPDATE Books 
                       SET ISBN = ?, Title = ?, Author = ?, Edition = ?, Publisher = ?, 
                           PublicationYear = ?, CategoryID = ?, TotalCopies = ?, AvailableCopies = ? 
                       WHERE BookID = ?""",
                    (isbn, title, author, edition, publisher, year or None, category_id, total_copies, new_available, book_id),
                    fetch=False,
                    commit=True
                )
                flash("Book updated successfully.", "success")
            else:
                # Insert new book
                execute_query(
                    """INSERT INTO Books (ISBN, Title, Author, Edition, Publisher, PublicationYear, CategoryID, TotalCopies, AvailableCopies) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (isbn, title, author, edition, publisher, year or None, category_id, total_copies, total_copies),
                    fetch=False,
                    commit=True
                )
                flash("Book added to library catalog.", "success")
        except Exception as e:
            flash(f"Database error: {e}", "danger")
            
        return redirect(url_for('admin.manage_books'))
        
    # GET: List books and categories
    try:
        books = execute_query(
            """SELECT b.*, c.CategoryName 
               FROM Books b 
               INNER JOIN Categories c ON b.CategoryID = c.CategoryID 
               ORDER BY b.Title ASC"""
        )
        categories = execute_query("SELECT * FROM Categories ORDER BY CategoryName ASC")
        return render_template('admin_books.html', books=books, categories=categories)
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('dashboard.index'))

@admin_bp.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@login_required
@role_required(['Admin', 'SuperAdmin'])
def delete_book(book_id):
    try:
        execute_query("DELETE FROM Books WHERE BookID = ?", (book_id,), fetch=False, commit=True)
        flash("Book deleted from library catalog.", "success")
    except Exception as e:
        flash(f"Cannot delete book: {e}", "danger")
    return redirect(url_for('admin.manage_books'))

# ==========================================
# 2. Manage Borrow & Return Requests
# ==========================================
@admin_bp.route('/admin/requests')
@login_required
@role_required(['Admin', 'SuperAdmin'])
def manage_requests():
    # Fetch pending borrow requests
    try:
        borrow_requests = execute_query(
            """SELECT bb.*, u.Username, u.CollegeName, b.Title, b.Author, b.AvailableCopies 
               FROM BorrowedBooks bb
               INNER JOIN Users u ON bb.UserID = u.UserID
               INNER JOIN Books b ON bb.BookID = b.BookID
               WHERE bb.Status = 'Pending'
               ORDER BY bb.BorrowDate ASC"""
        )
        
        # Fetch pending bookstore orders
        orders = execute_query(
            """SELECT o.*, u.Username, u.CollegeName 
               FROM Orders o
               INNER JOIN Users u ON o.BuyerID = u.UserID
               WHERE o.OrderStatus = 'Pending'
               ORDER BY o.OrderDate ASC"""
        )
        
        return render_template('admin_requests.html', borrows=borrow_requests, orders=orders)
    except Exception as e:
        flash(f"Error loading requests: {e}", "danger")
        return redirect(url_for('dashboard.index'))

@admin_bp.route('/admin/requests/borrow/<int:borrow_id>/<string:action>', methods=['POST'])
@login_required
@role_required(['Admin', 'SuperAdmin'])
def process_borrow(borrow_id, action):
    try:
        borrow = execute_query("SELECT BookID, Status FROM BorrowedBooks WHERE BorrowID = ?", (borrow_id,))
        if not borrow:
            flash("Borrow request not found.", "danger")
            return redirect(url_for('admin.manage_requests'))
            
        record = borrow[0]
        if record['Status'] != 'Pending':
            flash("Request already processed.", "warning")
            return redirect(url_for('admin.manage_requests'))
            
        book_id = record['BookID']
        
        if action == 'approve':
            # Check availability
            book = execute_query("SELECT AvailableCopies FROM Books WHERE BookID = ?", (book_id,))[0]
            if book['AvailableCopies'] <= 0:
                flash("Cannot approve borrow request. Book has 0 available copies.", "danger")
                return redirect(url_for('admin.manage_requests'))
                
            # Update borrow record
            execute_query(
                "UPDATE BorrowedBooks SET Status = 'Approved' WHERE BorrowID = ?",
                (borrow_id,),
                fetch=False,
                commit=True
            )
            # Decrement inventory copies
            execute_query(
                "UPDATE Books SET AvailableCopies = AvailableCopies - 1 WHERE BookID = ?",
                (book_id,),
                fetch=False,
                commit=True
            )
            flash("Borrow request approved!", "success")
            
        elif action == 'reject':
            execute_query(
                "UPDATE BorrowedBooks SET Status = 'Rejected' WHERE BorrowID = ?",
                (borrow_id,),
                fetch=False,
                commit=True
            )
            flash("Borrow request rejected.", "info")
            
    except Exception as e:
        flash(f"Failed to process request: {e}", "danger")
        
    return redirect(url_for('admin.manage_requests'))

# ==========================================
# 3. Manage Store Orders
# ==========================================
@admin_bp.route('/admin/orders/<int:order_id>/<string:status>', methods=['POST'])
@login_required
@role_required(['Admin', 'SuperAdmin'])
def process_order(order_id, status):
    try:
        # Check order existence
        order = execute_query("SELECT OrderStatus FROM Orders WHERE OrderID = ?", (order_id,))
        if not order:
            flash("Order not found.", "danger")
            return redirect(url_for('admin.manage_requests'))
            
        current_status = order[0]['OrderStatus']
        
        if status == 'Approved':
            execute_query(
                "UPDATE Orders SET OrderStatus = 'Approved', PaymentStatus = 'Paid' WHERE OrderID = ?",
                (order_id,),
                fetch=False,
                commit=True
            )
            flash("Order approved and marked as paid.", "success")
        elif status == 'Cancelled':
            # If cancelling, revert inventory stocks
            execute_query(
                "UPDATE Orders SET OrderStatus = 'Cancelled' WHERE OrderID = ?",
                (order_id,),
                fetch=False,
                commit=True
            )
            items = execute_query("SELECT ListingID, Quantity FROM OrderItems WHERE OrderID = ?", (order_id,))
            for item in items:
                execute_query(
                    "UPDATE Listings SET Stock = Stock + ? WHERE ListingID = ?",
                    (item['Quantity'], item['ListingID']),
                    fetch=False,
                    commit=True
                )
            flash("Order cancelled and inventory stocks returned.", "info")
        elif status == 'Delivered':
            execute_query(
                "UPDATE Orders SET OrderStatus = 'Delivered' WHERE OrderID = ?",
                (order_id,),
                fetch=False,
                commit=True
            )
            flash("Order marked as delivered.", "success")
            
    except Exception as e:
        flash(f"Failed to update order status: {e}", "danger")
        
    return redirect(url_for('admin.manage_requests'))

# ==========================================
# 4. Super Admin User Control (SuperAdmin only)
# ==========================================
@admin_bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
@role_required(['SuperAdmin'])
def manage_users():
    if request.method == 'POST':
        # Create new user / edit user status
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        phone = request.form.get('phone').strip()
        college = request.form.get('college').strip()
        password = request.form.get('password')
        role = request.form.get('role')
        user_status = request.form.get('status', 'Active')
        
        user_id = request.form.get('user_id') # Present if editing
        
        if user_id:
            # Update user profile & status (SuperAdmin overriding)
            try:
                if password:
                    # Update with new password
                    hashed_pw = generate_password_hash(password)
                    execute_query(
                        """UPDATE Users 
                           SET Username = ?, Email = ?, Phone = ?, CollegeName = ?, Role = ?, UserStatus = ?, PasswordHash = ? 
                           WHERE UserID = ?""",
                        (username, email, phone, college, role, user_status, hashed_pw, user_id),
                        fetch=False,
                        commit=True
                    )
                else:
                    execute_query(
                        """UPDATE Users 
                           SET Username = ?, Email = ?, Phone = ?, CollegeName = ?, Role = ?, UserStatus = ? 
                           WHERE UserID = ?""",
                        (username, email, phone, college, role, user_status, user_id),
                        fetch=False,
                        commit=True
                    )
                flash("User account updated successfully.", "success")
            except Exception as e:
                flash(f"Failed to update user: {e}", "danger")
        else:
            # Create user
            if not username or not email or not college or not password or not role:
                flash("Please provide all required fields to create a user account.", "warning")
                return redirect(url_for('admin.manage_users'))
                
            try:
                # Check uniqueness
                exists = execute_query("SELECT UserID FROM Users WHERE Username = ? OR Email = ?", (username, email))
                if exists:
                    flash("Username or Email already registered.", "warning")
                    return redirect(url_for('admin.manage_users'))
                    
                hashed_pw = generate_password_hash(password)
                execute_query(
                    """INSERT INTO Users (Username, Email, PasswordHash, Phone, CollegeName, Role, UserStatus) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (username, email, hashed_pw, phone, college, role, user_status),
                    fetch=False,
                    commit=True
                )
                flash(f"Created new {role} account: {username}.", "success")
            except Exception as e:
                flash(f"Failed to create user: {e}", "danger")
                
        return redirect(url_for('admin.manage_users'))
        
    # GET: List all users
    try:
        users = execute_query("SELECT * FROM Users ORDER BY Role ASC, Username ASC")
        return render_template('admin_users.html', users=users)
    except Exception as e:
        flash(f"Error loading users: {e}", "danger")
        return redirect(url_for('dashboard.index'))
