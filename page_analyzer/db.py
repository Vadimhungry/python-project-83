import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_url(url):
    with psycopg2.connect(DATABASE_URL) as db:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM urls WHERE name = %s;", (url,)
            )
            url_in_bd = cursor.fetchone()
    return url_in_bd


def get_url_id(url):
    return get_url(url)[0]


def get_url_info(id):
    with psycopg2.connect(DATABASE_URL) as db:
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM urls WHERE id = (%s)', (id,))
            site_id, site_url, date = cursor.fetchone()
            site_date = date.strftime('%Y-%m-%d')
    return site_url, site_date


def get_url_name(id):
    with psycopg2.connect(DATABASE_URL) as db:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM urls WHERE id=(%s);",
                (id,)
            )
            return (cursor.fetchone())[0]


def get_all_urls():
    with psycopg2.connect(DATABASE_URL) as db:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT
                    DISTINCT ON (url_id) url_id,
                    urls.name,
                    url_checks.created_at,
                    status_code
                FROM
                    url_checks
                JOIN urls ON urls.id=url_checks.url_id
                ORDER BY url_id, created_at DESC;'''
            )
            return cursor.fetchall()


def get_checks(id):
    with psycopg2.connect(DATABASE_URL) as db:
        with db.cursor() as cursor:
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
    with psycopg2.connect(DATABASE_URL) as db:
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO urls (name) VALUES (%s)", (url,)
            )


def insert_check(id, status_code, h1, title, description):
    with psycopg2.connect(DATABASE_URL) as db:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO
                    url_checks(url_id, status_code, h1, title, description)
                VALUES
                    (%s, %s, %s, %s, %s);''',
                (id, status_code, h1, title, description)
            )
