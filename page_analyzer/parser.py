from urllib.parse import urlparse

from bs4 import BeautifulSoup
from validators.url import url as check_url


def is_valid_url(url):
    errors = []

    if not check_url(url):
        errors.append('Error! Url is invalid')

    if len(url) > 255:
        errors.append('Error! Url length > 255')

    if errors == []:
        return True
    return errors


def normalize_url(url):
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


def get_tags(content):
    soup = BeautifulSoup(content, 'html.parser')

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

    return h1, title, description
