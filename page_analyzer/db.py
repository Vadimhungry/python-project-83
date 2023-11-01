import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import DictCursor

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class DatabaseConnection:
    def __enter__(self):
        self.db = psycopg2.connect(DATABASE_URL)
        self.cursor = self.db.cursor(cursor_factory=DictCursor)
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.commit()
        self.cursor.close()
        self.db.close()


def get_url(url):
    with DatabaseConnection() as cursor:
        cursor.execute(
            "SELECT * FROM urls WHERE name = %s;", (url,)
        )
        url_in_bd = cursor.fetchone()
    return url_in_bd


def get_url_info(id):
    with DatabaseConnection() as cursor:
        cursor.execute('SELECT * FROM urls WHERE id = (%s)', (id,))
        site_id, site_url, date = cursor.fetchone()
        site_date = date.strftime('%Y-%m-%d')
    return {'id': id, 'url': site_url, 'date': site_date}


def get_all_urls():
    with DatabaseConnection() as cursor:
        cursor.execute(
            '''
            SELECT
                DISTINCT ON (urls.id) urls.id,
                urls.name,
                url_checks.created_at,
                status_code
            FROM
                url_checks RIGHT JOIN urls
                ON urls.id=url_checks.url_id
            ORDER BY urls.id, created_at DESC;
            '''
        )
        return cursor.fetchall()


def get_checks(id):
    with DatabaseConnection() as cursor:
        cursor.execute(
            '''
            SELECT id,status_code, h1, title, description, created_at
            FROM url_checks
            WHERE url_id = (%s)
            ORDER BY id DESC;
            ''',
            (id,)
        )
        return cursor.fetchall()


def insert_url(url):
    with DatabaseConnection() as cursor:
        cursor.execute(
            "INSERT INTO urls (name) VALUES (%s) RETURNING id",
            (url,)
        )
        return cursor.fetchone()[0]


def insert_check(id, status_code, h1, title, description):
    with DatabaseConnection() as cursor:
        cursor.execute(
            '''
            INSERT INTO
                url_checks(url_id, status_code, h1, title, description)
            VALUES
                (%s, %s, %s, %s, %s);
            ''',
            (id, status_code, h1, title, description)
        )
