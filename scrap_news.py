import requests
from bs4 import BeautifulSoup
import re
import json

class News:
    def __init__(self):
        self.news_ids = []
        self.news_dict = {}
        self.default_url = "https://abc.net.au/news/"

    def get_news_id(self):
        url = 'https://www.abc.net.au/news/sa'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Replace 'your_selector' with the appropriate CSS selector for the news headlines
        list_items = soup.select("ul.List_unstyled__BUts_ li.LinkList_listItem__NLiw1")

        for item in list_items:
            data_uri = item.find('div', {'data-component': 'ListCard'}).get('data-uri')
            id = data_uri.split('/')[-1]
            self.news_ids.append(id)

    @staticmethod
    def get_news(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        art = soup.find('div',id='body')

        if art:
            return art.get_text(strip=True)
        else:
            return 'News not captured'
        
    @staticmethod
    def get_news_headline(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        art = soup.find('h1')

        if art:
            return art.get_text(strip=True)
        else:
            return 'Headline not captured'
        
    @staticmethod
    def get_img(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        img_src = soup.find('img').get('src')

        if img_src:
            return img_src
        else:
            return None

    def get_news_dict(self):
        for id in self.news_ids:
            url = self.default_url+str(id)
            news = News.get_news(url)
            headline = News.get_news_headline(url)
            img_scr = News.get_img(url)
            self.news_dict[id] = {'original_text':news}
            self.news_dict[id]['headline'] = headline
            self.news_dict[id]['img'] = img_scr
            self.news_dict[id]['url'] = url
            self.news_dict[id]['summarized_text'] = '-'
        
    @staticmethod
    def clean_text(text, remove_stopwords=True):
        
        #Delete the last paragraph
        pattern = re.compile(r"Posted\d+h ago")
        # Find the last occurrence of the pattern
        match = pattern.search(text)
        if match:
            # Delete the last paragraph
            text = text[:match.start()]
            # print(modified_text)
        else: pass
        
        text = text.split()
        tmp = []
        f = open('contractions.json')
 
        contractions = json.load(f)
        
        for word in text:
            if word in contractions:
                tmp.append(contractions[word])
            else:
                tmp.append(word)
        text = ' '.join(tmp)

        text = re.sub(r'https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\<a href', ' ', text)
        text = re.sub(r'&amp;', '', text)
        text = re.sub(r'[_"\-;%()|+&=*%:#$@\[\]/]', ' ', text)
        text = re.sub(r'<br />', ' ', text)
        text = re.sub(r'\'', ' ', text)

        return text