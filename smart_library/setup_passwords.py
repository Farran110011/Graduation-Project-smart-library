import os
from getpass import getpass

import mysql.connector
from werkzeug.security import generate_password_hash


def main():
    passwords = {}
    for username in ('admin', 'librarian1'):
        password = getpass(f'Choose a password for {username}: ')
        if not password:
            raise ValueError('Passwords must not be empty.')
        if password != getpass(f'Confirm password for {username}: '):
            raise ValueError('Passwords do not match.')
        passwords[username] = generate_password_hash(password)

    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', '3306')),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ['DB_PASSWORD'],
        database=os.environ.get('DB_NAME', 'smart_library'),
    )
    cursor = conn.cursor()
    try:
        for username, pw_hash in passwords.items():
            cursor.execute(
                'UPDATE users SET password_hash = %s WHERE username = %s',
                (pw_hash, username),
            )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    print('Account passwords updated. You can now log in.')


if __name__ == '__main__':
    main()
