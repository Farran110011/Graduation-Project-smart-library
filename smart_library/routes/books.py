from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from db import get_db
from datetime import date, timedelta

books_bp = Blueprint('books', __name__)


@books_bp.route('/search')
def search():                                    # public page, searches by title, author, or RFID tag
    query = request.args.get('q', '').strip()
    results = []

    if query:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        like = f'%{query}%'
        cursor.execute('''
            SELECT b.id, b.title, b.author, b.isbn, b.rfid_tag,
                   b.status, b.category,
                   es.shelf_name AS expected_shelf,
                   cs.shelf_name AS current_shelf,
                   cs.shelf_code AS current_shelf_code
            FROM books b
            JOIN shelves es ON b.expected_shelf_id = es.id
            LEFT JOIN shelves cs ON b.current_shelf_id = cs.id
            WHERE b.title LIKE %s
               OR b.author LIKE %s
               OR b.rfid_tag LIKE %s
            ORDER BY b.title
        ''', (like, like, like))
        results = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template('search.html', query=query, results=results)


@books_bp.route('/books/borrow', methods=['POST'])
def borrow():
    if 'user_id' not in session:                 # librarians only
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    book_id = request.form['book_id']
    university_id = request.form['university_id'].strip()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT id FROM students WHERE university_id = %s', (university_id,))
    student = cursor.fetchone()
    if not student:                              # student must exist
        flash(f'Student ID {university_id} not found.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard.index'))

    cursor.execute('SELECT status FROM books WHERE id = %s', (book_id,))
    book = cursor.fetchone()
    if not book or book['status'] == 'borrowed':   # book must be available
        flash('This book is not available for borrowing.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard.index'))

    due = date.today() + timedelta(days=14)        # 2-week loan period
    cursor.execute('''
        INSERT INTO borrowings (book_id, student_id, due_date)
        VALUES (%s, %s, %s)
    ''', (book_id, student['id'], due))

    cursor.execute('''
        UPDATE books SET status = 'borrowed', current_shelf_id = NULL
        WHERE id = %s
    ''', (book_id,))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Book borrowed successfully.', 'success')
    return redirect(url_for('dashboard.index'))


@books_bp.route('/books/return/<int:borrowing_id>', methods=['POST'])
def return_book(borrowing_id):
    if 'user_id' not in session:                 # librarians only
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT book_id FROM borrowings WHERE id = %s', (borrowing_id,))
    borrowing = cursor.fetchone()
    if not borrowing:
        flash('Borrowing record not found.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard.index'))

    cursor.execute('''
        UPDATE borrowings SET status = 'returned', returned_at = NOW()
        WHERE id = %s
    ''', (borrowing_id,))

    cursor.execute('''
        UPDATE books SET status = 'on shelf',
                         current_shelf_id = expected_shelf_id
        WHERE id = %s
    ''', (borrowing['book_id'],))                 # book goes back to its expected shelf

    conn.commit()
    cursor.close()
    conn.close()

    flash('Book returned successfully.', 'success')
    return redirect(url_for('dashboard.index'))
