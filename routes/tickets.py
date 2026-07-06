from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from database.connection import execute_query

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets', methods=['GET', 'POST'])
@login_required
def index():
    user_id = session['user_id']
    role = session['role']
    
    if request.method == 'POST':
        # Create a new ticket (Students only)
        if role != 'Student':
            flash("Only students can create support tickets.", "danger")
            return redirect(url_for('tickets.index'))
            
        subject = request.form.get('subject', '').strip()
        category = request.form.get('category')
        description = request.form.get('description', '').strip()
        
        if not subject or not category or not description:
            flash("Please fill in all fields to create a ticket.", "warning")
            return redirect(url_for('tickets.index'))
            
        try:
            # 1. Insert Ticket
            ticket_id = execute_query(
                "INSERT INTO SupportTickets (UserID, Subject, Category, Description) VALUES (?, ?, ?, ?)",
                (user_id, subject, category, description),
                fetch=False,
                commit=True
            )
            
            # Fallback if SQLite fails to return lastrowid
            if not ticket_id:
                latest = execute_query(
                    "SELECT TicketID FROM SupportTickets WHERE UserID = ? ORDER BY DateCreated DESC LIMIT 1",
                    (user_id,)
                )
                ticket_id = latest[0]['TicketID']
                
            # 2. Insert initial ticket description into message log as first entry
            execute_query(
                "INSERT INTO TicketMessages (TicketID, SenderID, MessageText) VALUES (?, ?, ?)",
                (ticket_id, user_id, description),
                fetch=False,
                commit=True
            )
            
            flash("Support ticket created successfully!", "success")
        except Exception as e:
            flash(f"Failed to create ticket: {e}", "danger")
            
        return redirect(url_for('tickets.index'))
        
    # GET Request: Fetch tickets list
    try:
        if role == 'Student':
            tickets = execute_query(
                "SELECT * FROM SupportTickets WHERE UserID = ? ORDER BY DateUpdated DESC",
                (user_id,)
            )
        else:
            # Admins view all tickets
            tickets = execute_query(
                """SELECT t.*, u.Username 
                   FROM SupportTickets t
                   INNER JOIN Users u ON t.UserID = u.UserID
                   ORDER BY t.Status ASC, t.DateUpdated DESC"""
            )
            
        return render_template('tickets.html', tickets=tickets)
    except Exception as e:
        flash(f"Error loading tickets: {e}", "danger")
        return redirect(url_for('dashboard.index'))

@tickets_bp.route('/tickets/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def detail(ticket_id):
    user_id = session['user_id']
    role = session['role']
    
    # Verify ticket ownership (Students can only view their own; admins view all)
    try:
        ticket = execute_query("SELECT * FROM SupportTickets WHERE TicketID = ?", (ticket_id,))
        if not ticket:
            flash("Ticket not found.", "danger")
            return redirect(url_for('tickets.index'))
            
        t = ticket[0]
        if role == 'Student' and t['UserID'] != user_id:
            flash("Access Denied.", "danger")
            return redirect(url_for('tickets.index'))
            
        if request.method == 'POST':
            # Send message to ticket thread
            message_text = request.form.get('message_text', '').strip()
            if message_text:
                execute_query(
                    "INSERT INTO TicketMessages (TicketID, SenderID, MessageText) VALUES (?, ?, ?)",
                    (ticket_id, user_id, message_text),
                    fetch=False,
                    commit=True
                )
                
                # Update ticket's last updated time
                execute_query(
                    "UPDATE SupportTickets SET DateUpdated = datetime('now', 'localtime') WHERE TicketID = ?",
                    (ticket_id,),
                    fetch=False,
                    commit=True
                )
                
                flash("Reply sent.", "success")
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
            
        # GET Request: Fetch ticket thread messages
        messages = execute_query(
            """SELECT tm.*, u.Username, u.Role as SenderRole 
               FROM TicketMessages tm
               INNER JOIN Users u ON tm.SenderID = u.UserID
               WHERE tm.TicketID = ?
               ORDER BY tm.DateSent ASC""",
            (ticket_id,)
        )
        
        # Get ticket owner info
        owner = execute_query("SELECT Username, CollegeName FROM Users WHERE UserID = ?", (t['UserID'],))[0]
        
        return render_template('tickets.html', ticket=t, messages=messages, owner=owner, detail_view=True)
        
    except Exception as e:
        flash(f"Error loading ticket detail: {e}", "danger")
        return redirect(url_for('tickets.index'))

@tickets_bp.route('/tickets/close/<int:ticket_id>', methods=['POST'])
@login_required
def close_ticket(ticket_id):
    user_id = session['user_id']
    role = session['role']
    
    try:
        ticket = execute_query("SELECT UserID FROM SupportTickets WHERE TicketID = ?", (ticket_id,))
        if not ticket:
            flash("Ticket not found.", "danger")
            return redirect(url_for('tickets.index'))
            
        t = ticket[0]
        # Student owner or Admin can close tickets
        if role == 'Student' and t['UserID'] != user_id:
            flash("Access Denied.", "danger")
            return redirect(url_for('tickets.index'))
            
        execute_query(
            "UPDATE SupportTickets SET Status = 'Resolved', DateUpdated = datetime('now', 'localtime') WHERE TicketID = ?",
            (ticket_id,),
            fetch=False,
            commit=True
        )
        
        # Send closing system log message
        system_text = "--- Ticket closed and marked resolved ---"
        execute_query(
            "INSERT INTO TicketMessages (TicketID, SenderID, MessageText) VALUES (?, ?, ?)",
            (ticket_id, user_id, system_text),
            fetch=False,
            commit=True
        )
        
        flash("Ticket closed.", "success")
    except Exception as e:
        flash(f"Failed to close ticket: {e}", "danger")
        
    return redirect(url_for('tickets.index'))
