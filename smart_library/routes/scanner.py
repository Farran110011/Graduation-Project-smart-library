from flask import Blueprint, render_template, request, jsonify, session
from db import get_db
import random

scanner_bp = Blueprint('scanner', __name__)


@scanner_bp.route('/simulator')
def simulator():
    return render_template('simulator.html')


@scanner_bp.route('/api/scan', methods=['POST'])
def receive_scan():                              # receives a scan {rfid_tag, shelf_code} from the simulator
    data = request.get_json()
    rfid_tag = data.get('rfid_tag')
    shelf_code = data.get('shelf_code')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM books WHERE rfid_tag = %s', (rfid_tag,))
    book = cursor.fetchone()

    cursor.execute('SELECT * FROM shelves WHERE shelf_code = %s', (shelf_code,))
    shelf = cursor.fetchone()

    if not book or not shelf:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Book or shelf not found'}), 404

    is_misplaced = (book['expected_shelf_id'] != shelf['id'])   # wrong shelf means misplaced
    new_status = 'misplaced' if is_misplaced else 'on shelf'

    cursor.execute('''
        UPDATE books SET current_shelf_id = %s, status = %s
        WHERE id = %s
    ''', (shelf['id'], new_status, book['id']))

    scanned_by = session.get('user_id')          # None if not logged in
    cursor.execute('''
        INSERT INTO scan_logs (book_id, shelf_id, scanned_by, is_misplaced)
        VALUES (%s, %s, %s, %s)
    ''', (book['id'], shelf['id'], scanned_by, is_misplaced))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        'book_title': book['title'],
        'rfid_tag': rfid_tag,
        'shelf': shelf['shelf_name'],
        'is_misplaced': is_misplaced,
        'expected_shelf_id': book['expected_shelf_id'],
        'scanned_shelf_id': shelf['id'],
        'status': new_status
    })


@scanner_bp.route('/api/books/<shelf_code>')
def books_on_shelf(shelf_code):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT id FROM shelves WHERE shelf_code = %s', (shelf_code,))
    shelf = cursor.fetchone()

    if not shelf:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Shelf not found'}), 404

    cursor.execute('''
        SELECT b.rfid_tag, b.title, b.author, b.category,
               b.expected_shelf_id, b.current_shelf_id, b.status
        FROM books b
        WHERE b.current_shelf_id = %s
    ''', (shelf['id'],))
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'shelf_code': shelf_code, 'books': books})


@scanner_bp.route('/api/simulator/state')
def simulator_state():                           # lets the simulator sync with the database on load
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT b.rfid_tag,
               cs.shelf_code AS current_shelf_code,
               b.status
        FROM books b
        LEFT JOIN shelves cs ON b.current_shelf_id = cs.id
    ''')
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'books': books})


@scanner_bp.route('/api/misplace', methods=['POST'])
def misplace_book():                             # moves a random correct book to a wrong shelf (for testing)
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT b.id, b.rfid_tag, b.title, b.expected_shelf_id,
               s.shelf_code AS expected_code
        FROM books b
        JOIN shelves s ON b.expected_shelf_id = s.id
        WHERE b.current_shelf_id = b.expected_shelf_id
          AND b.status = 'on shelf'
    ''')
    correct_books = cursor.fetchall()

    if not correct_books:
        cursor.close()
        conn.close()
        return jsonify({'error': 'No correctly placed books to misplace'}), 400

    book = random.choice(correct_books)

    cursor.execute('SELECT id, shelf_code FROM shelves WHERE id != %s', (book['expected_shelf_id'],))
    other_shelves = cursor.fetchall()
    new_shelf = random.choice(other_shelves)     # a different shelf than the expected one

    cursor.execute('''
        UPDATE books SET current_shelf_id = %s, status = 'misplaced'
        WHERE id = %s
    ''', (new_shelf['id'], book['id']))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        'rfid_tag': book['rfid_tag'],
        'title': book['title'],
        'from_shelf': book['expected_code'],
        'to_shelf': new_shelf['shelf_code'],
        'to_shelf_id': new_shelf['id']
    })


@scanner_bp.route('/api/reset', methods=['POST'])
def reset_books():                               # puts every non-borrowed book back on its correct shelf
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        UPDATE books
        SET current_shelf_id = expected_shelf_id, status = 'on shelf'
        WHERE status != 'borrowed'
    ''')

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'All books reset to correct shelves'})
