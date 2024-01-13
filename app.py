from flask import Flask, render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import pytz
# import json
import os

app = Flask(__name__)

#Connecting to database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class YourTable(db.Model):
    __tablename__ = 'news_summary'
    id = db.Column(db.String, primary_key=True)
    original_text = db.Column(db.String)
    headline = db.Column(db.String)
    img = db.Column(db.String)
    url = db.Column(db.String)
    summarized_text = db.Column(db.String)



@app.route('/',methods=['GET'])
def index():
    timezone = 'Australia/Perth'
    py_timezone = pytz.timezone(timezone)
    my_date = datetime.now(py_timezone)
    
    # Create the tables (if not already created)
    db.create_all()

    # Query the data from the table
    data = YourTable.query.all()
    news_dictionary = [{"headline": item.headline, "img": item.img,"url": item.url,"summarized_text": item.summarized_text} for item in data]
    return render_template('index.html',my_date=my_date,news_dictionary = news_dictionary)

if __name__=='__main__':
    app.run(debug=False)