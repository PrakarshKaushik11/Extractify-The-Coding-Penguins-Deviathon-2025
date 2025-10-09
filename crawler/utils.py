import requests
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser


def get_robots_parser(domain_url):
    parsed = urlparse(domain_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
    except:
        # fallback, allow all on error
        rp = None
    return rp

def is_allowed_by_robots(rp, url):
    if rp is None:
        return True
    return rp.can_fetch("*", url)

def normalize_url(url):
    # Remove URL fragment (#...) and trailing slashes
    url, _ = urldefrag(url)
    if url.endswith('/'):
        url = url[:-1]
    return url

def get_canonical_url(soup):
    tag = soup.find('link', rel='canonical')
    if tag and tag.get('href'):
        return tag['href']
    return None

def extract_main_text(soup):
    # Simple heuristic: remove scripts, styles, nav, footer, header, ads (by common attributes)
    # Then get text from body

    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
        tag.decompose()

    # Remove common ad containers by id/class names (basic)
    for ad_id in ['advertisement', 'ads', 'ad', 'promo', 'cookie']:
        for ad in soup.find_all(id=ad_id):
            ad.decompose()
        for ad in soup.find_all(class_=ad_id):
            ad.decompose()

    body = soup.body
    if not body:
        body = soup

    text = body.get_text(separator='\n', strip=True)
    return text
