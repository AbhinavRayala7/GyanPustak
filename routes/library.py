from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from database.connection import execute_query
from datetime import datetime, timedelta

library_bp = Blueprint('library', __name__)

@library_bp.route('/library')
@login_required
def index():
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', '').strip()
    
    # Base query
    query = """
        SELECT b.*, c.CategoryName 
        FROM Books b
        INNER JOIN Categories c ON b.CategoryID = c.CategoryID
        WHERE 1=1
    """
    params = []
    
    if search:
        query += " AND (b.Title LIKE ? OR b.Author LIKE ? OR b.ISBN = ?)"
        params.extend([f"%{search}%", f"%{search}%", search])
        
    if category_id:
        query += " AND b.CategoryID = ?"
        params.append(category_id)
        
    query += " ORDER BY b.Title ASC"
    
    try:
        books = execute_query(query, tuple(params))
        categories = execute_query("SELECT * FROM Categories ORDER BY CategoryName ASC")
        
        # Get active borrows for the current user to disable borrow buttons if already borrowing
        user_borrows = execute_query(
            "SELECT BookID, Status FROM BorrowedBooks WHERE UserID = ? AND Status NOT IN ('Returned', 'Rejected')",
            (session['user_id'],)
        )
        borrowed_book_ids = {item['BookID']: item['Status'] for item in user_borrows}
        
        return render_template(
            'library.html',
            books=books,
            categories=categories,
            borrowed_book_ids=borrowed_book_ids,
            search=search,
            category_id=category_id
        )
    except Exception as e:
        flash(f"Error loading library: {e}", "danger")
        return redirect(url_for('dashboard.index'))

@library_bp.route('/library/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    user_id = session['user_id']
    
    try:
        # Check if already borrowing or requested
        existing = execute_query(
            "SELECT Status FROM BorrowedBooks WHERE UserID = ? AND BookID = ? AND Status NOT IN ('Returned', 'Rejected')",
            (user_id, book_id)
        )
        if existing:
            flash("You have already requested or borrowed this book.", "warning")
            return redirect(url_for('library.index'))
            
        # Check book availability
        book = execute_query("SELECT AvailableCopies FROM Books WHERE BookID = ?", (book_id,))
        if not book:
            flash("Book not found.", "danger")
            return redirect(url_for('library.index'))
            
        available = book[0]['AvailableCopies']
        if available <= 0:
            flash("No copies currently available. You can reserve this book instead.", "warning")
            return redirect(url_for('library.index'))
            
        # Create Borrow Record (Pending Admin Approval)
        # Note: We decrement the copy count *after* admin approval to keep inventory accurate,
        # but to prevent double-borrowing from the queue, we can check during approval.
        # However, to keep it simple, we record the pending borrow now.
        borrow_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S') # 14 days borrow period
        
        execute_query(
            "INSERT INTO BorrowedBooks (UserID, BookID, BorrowDate, DueDate, Status) VALUES (?, ?, ?, ?, 'Pending')",
            (user_id, book_id, borrow_date, due_date),
            fetch=False,
            commit=True
        )
        
        flash("Borrow request submitted successfully! Waiting for admin approval.", "success")
    except Exception as e:
        flash(f"Borrow request failed: {e}", "danger")
        
    return redirect(url_for('library.index'))

@library_bp.route('/library/reserve/<int:book_id>', methods=['POST'])
@login_required
def reserve_book(book_id):
    user_id = session['user_id']
    
    try:
        # Check if already reserved
        existing = execute_query(
            "SELECT Status FROM Reservations WHERE UserID = ? AND BookID = ? AND Status = 'Active'",
            (user_id, book_id)
        )
        if existing:
            flash("You already have an active reservation for this book.", "warning")
            return redirect(url_for('library.index'))
            
        # Check if book is actually unavailable (reservations are for out-of-stock books)
        book = execute_query("SELECT AvailableCopies FROM Books WHERE BookID = ?", (book_id,))
        if not book:
            flash("Book not found.", "danger")
            return redirect(url_for('library.index'))
            
        if book[0]['AvailableCopies'] > 0:
            flash("Copies are currently available. Please borrow it instead.", "info")
            return redirect(url_for('library.index'))
            
        # Insert reservation
        execute_query(
            "INSERT INTO Reservations (UserID, BookID, Status) VALUES (?, ?, 'Active')",
            (user_id, book_id),
            fetch=False,
            commit=True
        )
        flash("Book reserved successfully! You will be notified when it becomes available.", "success")
    except Exception as e:
        flash(f"Reservation failed: {e}", "danger")
        
    return redirect(url_for('library.index'))

@library_bp.route('/library/return/<int:borrow_id>', methods=['POST'])
@login_required
def return_book(borrow_id):
    # Returns a book (Student initiation)
    user_id = session['user_id']
    
    try:
        # Verify ownership of this borrow record
        borrow_record = execute_query(
            "SELECT * FROM BorrowedBooks WHERE BorrowID = ? AND UserID = ? AND Status = 'Approved'",
            (borrow_id, user_id)
        )
        if not borrow_record:
            flash("Invalid borrow record or book already returned.", "danger")
            return redirect(url_for('dashboard.index'))
            
        record = borrow_record[0]
        book_id = record['BookID']
        return_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update borrow record to 'Returned'
        execute_query(
            "UPDATE BorrowedBooks SET ReturnDate = ?, Status = 'Returned' WHERE BorrowID = ?",
            (return_date, borrow_id),
            fetch=False,
            commit=True
        )
        
        # Increment available copies back by 1
        execute_query(
            "UPDATE Books SET AvailableCopies = AvailableCopies + 1 WHERE BookID = ?",
            (book_id,),
            fetch=False,
            commit=True
        )
        
        flash("Book returned successfully!", "success")
    except Exception as e:
        flash(f"Return failed: {e}", "danger")
        
    return redirect(url_for('dashboard.index'))
