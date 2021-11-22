import requests
from bs4 import BeautifulSoup as bs

url_tr = "https://www.tradingview.com/symbols/BNBUSDT/ideas/"
r = requests.get(url_tr)

# print(r.text)
"""""""""
#tv-idea-label tv-widget-idea__label tv-idea-label--short
tv-idea-label tv-widget-idea__label tv-idea-label--long
vacancies_names2

tv-idea-label__icon
"""""
soup = bs(r.text, "html.parser")
class_str = "tv-feed__item tv-feed-layout__card-item js-feed__item--inited"
#class_str="tv-idea-label tv-widget-idea__label tv-idea-label--long"

vacancies_names = soup.find_all('span',class_="tv-idea-label tv-widget-idea__label tv-idea-label--long")
print(vacancies_names)

vacancies_names2 = soup.find_all('span',class_="tv-idea-label tv-widget-idea__label tv-idea-label--short")
print(vacancies_names)
#prettify

def shetchik(names):
    x = 0
    for name in names:
        print(name.text.strip())
        x = x + 1
    print(x)
    return


shetchik(vacancies_names)
shetchik(vacancies_names2)
