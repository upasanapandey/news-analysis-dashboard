from bs4 import BeautifulSoup
import re

def clean_html(raw_html):
    clean = BeautifulSoup(raw_html, "html.parser").get_text()
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()