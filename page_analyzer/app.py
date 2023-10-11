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
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = '123456789_qwerty'
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    messages = get_flashed_messages()

    return render_template(
        'index.html',
        messages=messages
    )


@app.post('/urls')
def check_url():
    url = request.form.to_dict()['url']
    url_is_valid = validate_url(url)

    if url_is_valid and len(url) < 255:
        parsed_url = urlparse(url)
        norm_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
        with psycopg2.connect(app.config['DATABASE_URL']) as db:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM urls WHERE name = %s;", (norm_url,))
                url_in_bd = cursor.fetchone()

                if url_in_bd is not None:
                    flash('Страница уже существует', 'error')
                    url_id = url_in_bd[0]
                    return redirect(
                        url_for('show_url', id=url_id),
                        code=302
                    )

                cursor.execute("INSERT INTO urls (name) VALUES (%s)", (norm_url,))
                cursor.execute("SELECT * FROM urls WHERE name = %s;", (norm_url,))
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
            cursor.execute("SELECT id, name FROM urls ORDER BY id DESC;")
            sites = cursor.fetchall()


    return render_template(
        'urls.html',
        sites=sites
    )


@app.get('/urls/<int:id>')
def show_url(id):
    messages = get_flashed_messages(with_categories=True)
    for message in messages:
        status, _ = message

    query = 'SELECT * FROM urls WHERE id = (%s)'

    with psycopg2.connect(app.config['DATABASE_URL']) as db:
        with db.cursor() as cursor:
            cursor.execute(query, (id,))
            site_id, site_url, date = cursor.fetchone()
    site_date = date.strftime('%Y-%m-%d')

    return render_template(
        'url.html',
        status=status,
        site_id=site_id,
        site_url=site_url,
        site_date=site_date
    )


if __name__ == '__main__':
    app.run()
