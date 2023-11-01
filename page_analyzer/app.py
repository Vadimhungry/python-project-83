import os

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    flash,
    url_for
)

from page_analyzer.db import (
    get_url,
    get_all_urls,
    get_url_info,
    get_checks,
    insert_url,
    insert_check
)
from page_analyzer.parser import parse_ceo_tags
from page_analyzer.urls import validate_url, normalize_url

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    url = request.form.get("url")
    errors = validate_url(url)
    if errors:
        for error in errors:
            text, category = error
            flash(text, category)
        return render_template('index.html'), 422

    norm_url = normalize_url(url)
    url_in_bd = get_url(norm_url)

    if url_in_bd is not None:
        flash('Страница уже существует', 'info')
        url_id = url_in_bd['id']
        return redirect(
            url_for('show_url', id=url_id),
            code=302
        )

    url_id = insert_url(norm_url)

    flash('Страница успешно добавлена', 'success')
    return redirect(
        url_for('show_url', id=url_id),
        code=302
    )


@app.get('/urls')
def show_urls():
    sites = get_all_urls()
    return render_template(
        'urls.html',
        sites=sites
    )


@app.get('/urls/<int:id>')
def show_url(id):
    url_info = get_url_info(id)
    url_checks = get_checks(id)
    return render_template(
        'url.html',
        site_id=id,
        site_url=url_info['url'],
        site_date=url_info['date'],
        url_checks=url_checks
    )


@app.post('/urls/<int:id>/checks')
def check_url(id):
    url = get_url_info(id)['url']
    request = requests.get(url)
    status_code = request.status_code

    if status_code == 200:
        tags = parse_ceo_tags(request.text)
        insert_check(id, status_code, *tags)
        flash('Страница успешно проверена', 'success')
    else:
        flash('Произошла ошибка при проверке', 'danger')

    return redirect(url_for('show_url', id=id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
