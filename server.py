import re
import requests
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from flask import Flask, redirect

TARGET_URL = 'http://habrahabr.ru'
RE_ALL_CHARS = re.compile(r'\b[^\W_]{6}\b', re.IGNORECASE | re.UNICODE)
RE_FILE_PATH = re.compile(r'.[A-Za-z\d]+$', )
RE_HABR_LINKS = re.compile(r'^(http|https)://(habrahabr|habr)(.*)')

app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # redirect for file requests
    # this also could be done by replacing src/urls of some tags in soup
    if RE_FILE_PATH.search(path):
        return redirect('%s/%s' % (TARGET_URL, path), code=302)

    original_url = '%s/%s' % (TARGET_URL, path)
    res = requests.get(original_url)
    soup = BeautifulSoup(res.content, "html.parser")
    # replace words in visible part of the page
    content = soup.find('div', {'class': 'layout'})
    if content:
        # replace all text occurrences
        targets = content.find_all(text=RE_ALL_CHARS)
        for t in targets:
            # sometimes you can find script tags inside content div, just skip such occurrences
            if t.parent and t.parent.name != 'script':
                fixed = RE_ALL_CHARS.sub(lambda x: '%s™' % x.group(), t)
                t.replace_with(fixed)
        # replace links
        links = soup.find_all('a', {'href': RE_HABR_LINKS})
        for l in links:
            l['href'] = urlparse(l['href']).path
    return str(soup)


if __name__ == "__main__":
    app.run()
