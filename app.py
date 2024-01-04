from flask import Flask, render_template
from datetime import datetime
from scrap_news import News
import requests

import pytz
from config import Config
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
@app.route('/',methods=['GET'])


def index():
    timezone = 'Australia/Perth'
    py_timezone = pytz.timezone(timezone)
    my_date = datetime.now(py_timezone)
    
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
    # API_TOKEN = os.environ.get('API_TOKEN')
    API_TOKEN = app.config['API_TOKEN']
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
	
    for id,v in news_dictionary.items():
        
        output = query({"inputs": v['original_text']})
        articles.news_dict[id]['summarized_text'] = output[0]['summary_text']
        
    
    return render_template('index.html',my_date=my_date,news_dictionary = articles.news_dict)

if __name__=='__main__':
    app.run(debug=False)