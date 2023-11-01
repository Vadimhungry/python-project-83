from bs4 import BeautifulSoup


def parse_ceo_tags(content):
    soup = BeautifulSoup(content, 'html.parser')

    if soup.h1 is not None:
        h1 = soup.h1.text
    else:
        h1 = ''

    if soup.title:
        title = soup.title.string
    else:
        title = ''

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
