import urllib.error
import urllib.request as urllib
import urllib.request
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from newspaper import Article
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup as bs
from datetime import datetime
from csv import DictWriter
import schedule


def Crawling() :
    
    old_df = pd.read_csv('/Users/anjaeu/Desktop/Contents/Elastic/엘라스틱 프로젝트/뉴스 크롤러/밀/news_data_wheat.csv', encoding='utf-8')
    old_df = old_df.fillna(value='')
    old_df['time'] = pd.to_datetime(old_df['time'])
    
    url='https://www.newsnow.co.uk/h/Industry+Sectors/Commodities/Grains%2C+Food+&+Fibre/Wheat?type=ln'
    
    
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("--no-sandbox")    
    
    driver_path = '/usr/local/bin/chromedriver'
    driver=webdriver.Chrome(driver_path, options=options)
    driver.implicitly_wait(1)
    driver.get(url)

    res = requests.get(url)
    soup = bs(res.text, 'lxml')
    div = soup.select_one("div.rs-grid.rs-grid--skeleton.js-skeleton > main > div.rs-newsbox.js-newsbox.js-newsmain.js-central_ln_wrap > div").findAll('div', {"class" : "hl"})

    raw_data = []
    
    for hl in div :
        data = hl.find('a', {"class" : "hll"})
        time = hl.find('span', {'class' : "time"})

        date = time.text
        date = pd.to_datetime(date)
        temp_link = data.get('href')
        name = data.text

        res = requests.get(temp_link)
        soup = bs(res.text, 'lxml')
        url = soup.select_one('script').get_text().split(" ")[13]
        urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', str(url))
        urls = ''.join(urls)
        link = (urls)

        article = Article(link)

        try :
            article.download()
            article.parse()
            if len(article.text) > 30000 :
                article_text = article.summary
            else :
                article_text = article.text
        except :
            article_text = ''

        if date > old_df.iloc[-1]['time'] :
            if name == old_df.iloc[-1]['title'] : 
                print('passing')
            else :
                dict = {'link': link, 'title':name, 'time':date, 'article':article_text}
                raw_data.append(dict)
                print(name, 'appended')
        else :
            pass

    new_data = pd.DataFrame(raw_data)
    new_data.sort_index(axis=0, ascending=False, ignore_index=True, inplace=True)
    old_df.append(new_data).to_csv('/Users/anjaeu/Desktop/Contents/Elastic/엘라스틱 프로젝트/뉴스 크롤러/밀/news_data_wheat.csv', encoding='utf-8', index=False)


Crawling()