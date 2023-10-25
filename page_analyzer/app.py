import os
from urllib.parse import urlparse
from page_analyzer.db import (
    get_url,
    get_url_id,
    get_all_urls,
    get_url_info,
    get_checks,
    get_url_name,
    insert_url,
    insert_check
)
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    flash,
    url_for
)
from validators.url import url as validate_url

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

successful_http_responses = [200, 201, 204, 202, 203, 205, 206, 207, 208]


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    # todo выделить парсинг в отдельный модуль
    url = request.form.to_dict()['url']
    url_is_valid = validate_url(url)

    if url_is_valid and len(url) < 255:
        parsed_url = urlparse(url)
        norm_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
        url_in_bd = get_url(norm_url)
        if url_in_bd is not None:
            flash('Страница уже существует', 'error')
            url_id = url_in_bd[0]
            return redirect(
                url_for('show_url', id=url_id),
                code=302
            )

        insert_url(norm_url)
        url_id = get_url_id(norm_url)

        flash('Страница успешно добавлена', 'success')
        return redirect(
            url_for('show_url', id=url_id),
            code=302
        )
    flash('Некорректный URL')
    return render_template('index.html'), 422


@app.get('/urls')
def show_urls():
    sites = get_all_urls()
    return render_template(
        'urls.html',
        sites=sites
    )


@app.get('/urls/<int:id>')
def show_url(id):
    site_url, site_date = get_url_info(id)
    url_checks = get_checks(id)
    return render_template(
        'url.html',
        site_id=id,
        site_url=site_url,
        site_date=site_date,
        url_checks=url_checks
    )


@app.post('/urls/<int:id>/checks')
def check_url(id):
    url = get_url_name(id)

    request = requests.get(url)
    status_code = request.status_code
    if status_code in successful_http_responses:
        soup = BeautifulSoup(request.text, 'html.parser')

        if soup.h1 is not None:
            h1 = soup.h1.text
        else:
            h1 = ''
        title = soup.title.string

        description_tag = soup.find(
            'meta',
            attrs={'name': 'description'}
        )
        if description_tag is not None:
            description_text = description_tag.get('content')
        else:
            description_text = ''

        if len(description_text) > 255:
            description_words = description_text[:252].split(' ')[:-1]
            description_cut = ' '.join(description_words)
            description = description_cut + '...'
        else:
            description = description_text

        insert_check(id, status_code, h1, title, description)
        flash('Страница успешно проверена', 'checked')
    else:
        flash('Произошла ошибка при проверке', 'check-error')

    return redirect(url_for('show_url', id=id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
