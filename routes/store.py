from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from routes.auth import login_required
from database.connection import execute_query

store_bp = Blueprint('store', __name__)

@store_bp.route('/store')
@login_required
def index():
    # Browse bookstore products
    try:
        listings = execute_query(
            """SELECT l.ListingID, l.Price, l.Condition, l.ListingDescription, l.Stock,
                      b.Title, b.Author, b.Publisher, b.Edition, c.CategoryName
               FROM Listings l
               INNER JOIN Books b ON l.BookID = b.BookID
               INNER JOIN Categories c ON b.CategoryID = c.CategoryID
               WHERE l.ListingStatus = 'Active' AND l.Stock > 0
               ORDER BY b.Title ASC"""
        )
        return render_template('store.html', listings=listings)
    except Exception as e:
        flash(f"Error loading store: {e}", "danger")
        return redirect(url_for('dashboard.index'))

@store_bp.route('/store/cart/add/<int:listing_id>', methods=['POST'])
@login_required
def add_to_cart(listing_id):
    # Initialize cart in session if not present
    if 'cart' not in session:
        session['cart'] = {}
        
    cart = session['cart']
    listing_id_str = str(listing_id)
    
    try:
        # Check stock
        listing = execute_query("SELECT Stock FROM Listings WHERE ListingID = ?", (listing_id,))
        if not listing:
            flash("Product not found.", "danger")
            return redirect(url_for('store.index'))
            
        stock = listing[0]['Stock']
        current_qty = cart.get(listing_id_str, 0)
        
        if current_qty + 1 > stock:
            flash(f"Cannot add more items. Only {stock} copies are in stock.", "warning")
        else:
            cart[listing_id_str] = current_qty + 1
            session['cart'] = cart # Re-save session
            flash("Item added to cart!", "success")
    except Exception as e:
        flash(f"Failed to add to cart: {e}", "danger")
        
    return redirect(url_for('store.index'))

@store_bp.route('/store/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    grand_total = 0.0
    
    if cart:
        # Fetch listing details for cart items
        placeholders = ','.join('?' for _ in cart.keys())
        query = f"""
            SELECT l.ListingID, l.Price, l.Condition, b.Title, b.Author
            FROM Listings l
            INNER JOIN Books b ON l.BookID = b.BookID
            WHERE l.ListingID IN ({placeholders})
        """
        try:
            items = execute_query(query, tuple(int(k) for k in cart.keys()))
            for item in items:
                lid = str(item['ListingID'])
                qty = cart[lid]
                subtotal = item['Price'] * qty
                grand_total += subtotal
                cart_items.append({
                    'listing_id': item['ListingID'],
                    'title': item['Title'],
                    'author': item['Author'],
                    'condition': item['Condition'],
                    'price': item['Price'],
                    'quantity': qty,
                    'subtotal': subtotal
                })
        except Exception as e:
            flash(f"Error fetching cart: {e}", "danger")
            
    return render_template('cart.html', cart_items=cart_items, grand_total=grand_total)

@store_bp.route('/store/cart/update', methods=['POST'])
@login_required
def update_cart():
    cart = session.get('cart', {})
    listing_id = request.form.get('listing_id')
    action = request.form.get('action') # 'increase', 'decrease', 'remove'
    
    if not listing_id or listing_id not in cart:
        return redirect(url_for('store.view_cart'))
        
    try:
        if action == 'increase':
            listing = execute_query("SELECT Stock FROM Listings WHERE ListingID = ?", (int(listing_id),))[0]
            if cart[listing_id] + 1 <= listing['Stock']:
                cart[listing_id] += 1
            else:
                flash("Cannot increase quantity. Out of stock.", "warning")
        elif action == 'decrease':
            if cart[listing_id] - 1 > 0:
                cart[listing_id] -= 1
            else:
                cart.pop(listing_id)
        elif action == 'remove':
            cart.pop(listing_id)
            
        session['cart'] = cart
    except Exception as e:
        flash(f"Failed to update cart: {e}", "danger")
        
    return redirect(url_for('store.view_cart'))

@store_bp.route('/store/checkout', methods=['POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    buyer_id = session['user_id']
    shipping_address = request.form.get('shipping_address', '').strip()
    
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('store.index'))
        
    if not shipping_address:
        flash("Please provide a shipping address.", "warning")
        return redirect(url_for('store.view_cart'))
        
    try:
        # Fetch prices and stocks to validate checkout transaction
        placeholders = ','.join('?' for _ in cart.keys())
        listings = execute_query(
            f"SELECT ListingID, Price, Stock FROM Listings WHERE ListingID IN ({placeholders})",
            tuple(int(k) for k in cart.keys())
        )
        
        # Verify stock and calculate total
        total_amount = 0.0
        order_items_to_insert = []
        
        for listing in listings:
            lid = str(listing['ListingID'])
            qty = cart[lid]
            if qty > listing['Stock']:
                flash(f"Insufficient stock for some items. Cart was not checked out.", "danger")
                return redirect(url_for('store.view_cart'))
            total_amount += listing['Price'] * qty
            order_items_to_insert.append((
                listing['ListingID'],
                qty,
                listing['Price']
            ))
            
        # 1. Insert Order Header
        order_id = execute_query(
            "INSERT INTO Orders (BuyerID, TotalAmount, ShippingAddress, PaymentStatus, OrderStatus) VALUES (?, ?, ?, 'Pending', 'Pending')",
            (buyer_id, total_amount, shipping_address),
            fetch=False,
            commit=True
        )
        
        # If SQL Server is used, lastrowid might be fetched differently, but connection.py abstracts this.
        # However, to be absolutely database-agnostic in Flask, we can query the order back by buyer & date,
        # or use connection.py's execute_query return value.
        # SQLite's cursor.lastrowid returns the primary key of the inserted row. Let's make sure we fetch it.
        # If it returns 0 or None, fetch the latest order for this user:
        if not order_id:
            latest_order = execute_query(
                "SELECT OrderID FROM Orders WHERE BuyerID = ? ORDER BY OrderDate DESC LIMIT 1",
                (buyer_id,)
            )
            order_id = latest_order[0]['OrderID']
            
        # 2. Insert Order Items & Decrement Stock
        for item in order_items_to_insert:
            listing_id, qty, price = item
            # Insert item
            execute_query(
                "INSERT INTO OrderItems (OrderID, ListingID, Quantity, PriceAtPurchase) VALUES (?, ?, ?, ?)",
                (order_id, listing_id, qty, price),
                fetch=False,
                commit=True
            )
            # Decrement Stock
            execute_query(
                "UPDATE Listings SET Stock = Stock - ? WHERE ListingID = ?",
                (qty, listing_id),
                fetch=False,
                commit=True
            )
            
        # Clear cart
        session.pop('cart', None)
        flash("Order placed successfully! Pending admin approval.", "success")
        return redirect(url_for('store.orders'))
        
    except Exception as e:
        flash(f"Checkout failed: {e}", "danger")
        return redirect(url_for('store.view_cart'))

@store_bp.route('/store/orders')
@login_required
def orders():
    # View student order history
    buyer_id = session['user_id']
    try:
        orders = execute_query(
            "SELECT * FROM Orders WHERE BuyerID = ? ORDER BY OrderDate DESC",
            (buyer_id,)
        )
        return render_template('orders.html', orders=orders)
    except Exception as e:
        flash(f"Error loading orders: {e}", "danger")
        return redirect(url_for('dashboard.index'))

@store_bp.route('/store/orders/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    buyer_id = session['user_id']
    
    try:
        # Verify order ownership & status
        order = execute_query(
            "SELECT * FROM Orders WHERE OrderID = ? AND BuyerID = ? AND OrderStatus = 'Pending'",
            (order_id, buyer_id)
        )
        if not order:
            flash("Order cannot be cancelled. It may have been approved or already cancelled.", "warning")
            return redirect(url_for('store.orders'))
            
        # 1. Update Order Status to 'Cancelled'
        execute_query(
            "UPDATE Orders SET OrderStatus = 'Cancelled' WHERE OrderID = ?",
            (order_id,),
            fetch=False,
            commit=True
        )
        
        # 2. Revert inventory stocks for each order item
        items = execute_query(
            "SELECT ListingID, Quantity FROM OrderItems WHERE OrderID = ?",
            (order_id,)
        )
        for item in items:
            execute_query(
                "UPDATE Listings SET Stock = Stock + ? WHERE ListingID = ?",
                (item['Quantity'], item['ListingID']),
                fetch=False,
                commit=True
            )
            
        flash("Order cancelled successfully and inventory replenished.", "success")
    except Exception as e:
        flash(f"Cancellation failed: {e}", "danger")
        
    return redirect(url_for('store.orders'))
