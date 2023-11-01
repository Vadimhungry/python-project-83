from urllib.parse import urlparse
from validators.url import url as check_url


def validate_url(url):
    errors = []

    if not check_url(url):
        errors.append(('Некорректный URL', 'danger'))

    if len(url) > 255:
        errors.append(('Error! Url length > 255', 'danger'))

    return errors


def normalize_url(url):
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'
