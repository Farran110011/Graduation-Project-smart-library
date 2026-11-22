from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import get_db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def index():
    if 'user_id' not in session:                 # librarians only
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT COUNT(*) AS total FROM books')
    total_books = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM books WHERE status = 'misplaced'")
    misplaced_count = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM books WHERE status = 'borrowed'")
    borrowed_count = cursor.fetchone()['total']

    on_shelf_count = total_books - misplaced_count - borrowed_count

    cursor.execute('''
        SELECT b.title, b.author, b.rfid_tag,
               es.shelf_name AS expected_shelf,
               cs.shelf_name AS current_shelf
        FROM books b
        JOIN shelves es ON b.expected_shelf_id = es.id
        JOIN shelves cs ON b.current_shelf_id = cs.id
        WHERE b.status = 'misplaced'
    ''')
    misplaced_books = cursor.fetchall()

    cursor.execute('''
        SELECT sl.scanned_at, sl.is_misplaced,
               b.title, s.shelf_name,
               u.username AS scanned_by
        FROM scan_logs sl
        JOIN books b ON sl.book_id = b.id
        JOIN shelves s ON sl.shelf_id = s.id
        LEFT JOIN users u ON sl.scanned_by = u.id
        ORDER BY sl.scanned_at DESC
        LIMIT 20
    ''')
    recent_scans = cursor.fetchall()

    cursor.execute('''
        SELECT br.id, br.borrowed_at, br.due_date, br.status,
               b.title, st.student_name, st.university_id
        FROM borrowings br
        JOIN books b ON br.book_id = b.id
        JOIN students st ON br.student_id = st.id
        WHERE br.status IN ('active', 'overdue')
        ORDER BY br.due_date ASC
    ''')
    active_borrowings = cursor.fetchall()

    cursor.execute("SELECT id, title FROM books WHERE status = 'on shelf' ORDER BY title")
    available_books = cursor.fetchall()          # fills the borrow dropdown

    cursor.close()
    conn.close()

    return render_template('dashboard.html',
                           total_books=total_books,
                           on_shelf=on_shelf_count,
                           misplaced_count=misplaced_count,
                           borrowed_count=borrowed_count,
                           misplaced_books=misplaced_books,
                           recent_scans=recent_scans,
                           active_borrowings=active_borrowings,
                           available_books=available_books)
