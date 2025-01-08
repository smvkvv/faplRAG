import re
import requests
import logging

from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta

from config import BASE_URL
from schemas import Post


logger = logging.getLogger(__name__)


def get_months_to_iterate(n_months_to_iterate: int) -> list[str]:
    current_date = datetime.now()

    months = []
    for _ in range(n_months_to_iterate):
        months.append(current_date.strftime("%Y/%m/"))
        current_date -= relativedelta(months=1)

    logger.info("Got months to load: '%s'", months)
    return months


def get_soup_from_url(url: str) -> BeautifulSoup:
    response = requests.get(url)
    html = response.content.decode('windows-1251', errors='replace')

    return BeautifulSoup(html, 'html.parser')


def get_daily_posts_links(month: str) -> list[str]:
    url = BASE_URL + '/calendar/' + month

    response = requests.get(url)
    html = response.content.decode('windows-1251', errors='replace')

    soup = BeautifulSoup(html, 'html.parser')

    paragraphs = soup.findAll('p')
    timestamp_pattern = re.compile(r"^\d{2}\.\d{2}\.\d{4}")

    daily_posts_links = [
        BASE_URL + p.find('a')['href'] for p in paragraphs
        if timestamp_pattern.match(p.text.split()[0].strip())
        and p.find('a', href=True)
    ]

    return daily_posts_links


def process_post(soup: BeautifulSoup, uid: int) -> Post:
    block = soup.find('div', class_='block')

    title = block.find('h2').text
    text_content = ' '.join([elem.text.strip() for elem in block.find('div', class_='content').findAll('p')])
    tags = [elem.text for elem in block.find('p', class_='tags').findAll('a')]

    n_visits = int(re.findall(r'\d+', block.find('p', class_='visits').text)[0])
    author = block.find('p', class_='author').text.strip()
    dt = datetime.strptime(block.find('p', class_='date').text.strip(), '%d.%m.%Y %H:%M')

    return Post(uid=uid,
                title=title,
                text_content=text_content,
                tags=tags,
                n_visits=n_visits,
                author=author,
                dt=dt,
                vector=None)


def get_posts(n_months_to_iterate: int) -> list[dict]:
    months = get_months_to_iterate(n_months_to_iterate)
    posts = []

    for month in months:
        daily_posts_links = get_daily_posts_links(month)

        logger.info("For month '%s' got '%s' daily posts", month, len(daily_posts_links))
        for post_url in daily_posts_links:
            uid = int(re.findall(r'\d+', post_url)[0])
            soup = get_soup_from_url(url=post_url)

            post = process_post(soup, uid)
            posts.append(post.model_dump())

    logger.info("Loaded '%s' posts", len(posts))

    return posts