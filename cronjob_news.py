from scrap_news import News
import requests
import os

# from config import Config
from dotenv import load_dotenv
load_dotenv()
import psycopg2 


def get_news():
    articles = News()
    articles.get_news_id()
    articles.get_news_dict()
    
    news_dictionary= articles.news_dict
    
    for idx,art in articles.news_dict.items():
        try:
            articles.news_dict[idx]['original_text']=News.clean_text(art['original_text'].split('Key points:')[1],remove_stopwords=False)
        except:
            articles.news_dict[idx]['original_text'] = News.clean_text(art['original_text'],remove_stopwords=False)
    
    #Summarize the news
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    API_TOKEN = os.environ.get('API_TOKEN')
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
	
    for id,v in news_dictionary.items():
        
        output = query({"inputs": v['original_text']})
        articles.news_dict[id]['summarized_text'] = output[0]['summary_text']
        
    return articles.news_dict

def store_data(json_file):
    DATABASE_URL = os.environ.get('DATABASE_URL')   
    conn = psycopg2.connect(DATABASE_URL)
    # conn = psycopg2.connect(database="postgres", user="postgres", 
    #                         password="root", host="localhost", port="5432") 
    cursor = conn.cursor()

    cursor.execute(
        '''
        DROP TABLE IF EXISTS news_summary
        '''
    )

    cursor.execute(
                '''
                CREATE TABLE news_summary (id TEXT PRIMARY KEY,original_text TEXT, \
                headline TEXT, img TEXT, url TEXT, summarized_text TEXT);
                '''
            )

    # Iterate through the JSON data and insert into PostgreSQL
    for key in json_file.keys():
        cursor.execute(
            """
            INSERT INTO news_summary (id,original_text, headline, img,url, summarized_text)
            VALUES (%s,%s, %s, %s,%s,%s);
            """,
            (key,json_file[key]['original_text'], json_file[key]['headline'], json_file[key]['img'],json_file[key]['url'],json_file[key]['summarized_text'])
        )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__=='__main__':
    json_file=get_news()
    store_data(json_file)