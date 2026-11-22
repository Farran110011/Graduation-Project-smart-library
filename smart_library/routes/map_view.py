from flask import Blueprint, render_template, jsonify
from db import get_db

map_bp = Blueprint('map', __name__)


@map_bp.route('/map')
def library_map():
    return render_template('map.html')


@map_bp.route('/api/shelves')
def shelves_data():                              # shelves with book counts, used by the map
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT s.id, s.shelf_code, s.shelf_name, s.category,
               s.floor, s.map_x, s.map_y,
               COUNT(b.id) AS book_count,
               SUM(CASE WHEN b.status = 'misplaced' THEN 1 ELSE 0 END) AS misplaced_count
        FROM shelves s
        LEFT JOIN books b ON b.current_shelf_id = s.id
        GROUP BY s.id
    ''')
    shelves = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'shelves': shelves})


@map_bp.route('/api/shelf/<int:shelf_id>/books')
def shelf_books(shelf_id):                       # books currently on one shelf
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT b.title, b.author, b.rfid_tag, b.status,
               es.shelf_name AS expected_shelf
        FROM books b
        JOIN shelves es ON b.expected_shelf_id = es.id
        WHERE b.current_shelf_id = %s
        ORDER BY b.title
    ''', (shelf_id,))
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'books': books})
