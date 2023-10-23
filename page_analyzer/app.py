from flask import (
    Flask,
    render_template,
    redirect,
    request,
    flash,
    url_for,
    get_flashed_messages
)
from urllib.parse import urlparse
from validators.url import url as validate_url
import psycopg2
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import requests

load_dotenv()
app = Flask(__name__)
app.secret_key = '123456789_qwerty'
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

successful_http_responses = [200, 201, 204, 202, 203, 205, 206, 207, 208]

@app.route('/')
def index():
    messages = get_flashed_messages()

    return render_template(
        'index.html',
        messages=messages
    )


@app.post('/urls')
def add_url():
    url = request.form.to_dict()['url']
    url_is_valid = validate_url(url)

    if url_is_valid and len(url) < 255:
        parsed_url = urlparse(url)
        norm_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
        with psycopg2.connect(app.config['DATABASE_URL']) as db:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM urls WHERE name = %s;", (norm_url,)
                )
                url_in_bd = cursor.fetchone()

                if url_in_bd is not None:
                    flash('Страница уже существует', 'error')
                    url_id = url_in_bd[0]
                    return redirect(
                        url_for('show_url', id=url_id),
                        code=302
                    )

                cursor.execute(
                    "INSERT INTO urls (name) VALUES (%s)", (norm_url,)
                )
                cursor.execute(
                    "SELECT * FROM urls WHERE name = %s;", (norm_url,)
                )
                url_id = cursor.fetchone()[0]
        flash('Страница успешно добавлена', 'success')
        return redirect(
            url_for('show_url', id=url_id),
            code=302
        )
    flash('Некорректный URL')
    return redirect(url_for('index'))


@app.get('/urls')
def show_urls():
    with psycopg2.connect(app.config['DATABASE_URL']) as db:
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
            sites = cursor.fetchall()

    return render_template(
        'urls.html',
        sites=sites
    )


@app.get('/urls/<int:id>')
def show_url(id):
    messages = get_flashed_messages(with_categories=True)
    status = False
    for message in messages:
        status, _ = message

    with psycopg2.connect(app.config['DATABASE_URL']) as db:
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM urls WHERE id = (%s)', (id,))
            site_id, site_url, date = cursor.fetchone()
            site_date = date.strftime('%Y-%m-%d')
            cursor.execute(
                '''
                SELECT id,status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = (%s)
                ORDER BY id DESC;
                ''',
                (id,)
            )
            url_checks = cursor.fetchall()

    return render_template(
        'url.html',
        status=status,
        site_id=site_id,
        site_url=site_url,
        site_date=site_date,
        url_checks=url_checks
    )


@app.post('/urls/<int:id>/checks')
def check_url(id):

    with psycopg2.connect(app.config['DATABASE_URL']) as db:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM urls WHERE id=(%s);",
                (id,)
            )
            url = (cursor.fetchone())[0]
            request = requests.get(url)
            status_code = request.status_code
            if status_code in successful_http_responses:
                soup = BeautifulSoup(request.text, 'html.parser')

                if soup.h1 is not None:
                    h1 = soup.h1.text
                else:
                    h1 = ''
                title = soup.title.string

                description_text = soup.find('meta', attrs={'name': 'description'}).get('content')
                if len(description_text) > 255:
                    description = description_text[:252] + '...'
                else:
                    description = description_text

                cursor.execute(
                    "INSERT INTO url_checks (url_id, status_code, h1, title, description) VALUES (%s, %s, %s, %s, %s);",
                    (id, status_code, h1, title, description)
                )
                flash('Страница успешно проверена', 'checked')
            else:
                flash('Произошла ошибка при проверке', 'check-error')
    return redirect(url_for('show_url', id=id))


if __name__ == '__main__':
    app.run()
