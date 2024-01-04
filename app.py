from flask import Flask, render_template, request, send_file, redirect, url_for
import time
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
import os

app = Flask(__name__)

def scrape_youtube_data(company_name):
    browser = webdriver.Chrome()

    link = 'https://www.google.com/search?q=' + company_name + 'youtube'
    browser.get(link)

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    for i in soup.find_all('div', class_='MjjYud'):
        link = i.find('a').get('href')
        break

    browser.get(link + '/' + 'videos')

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    for i in tqdm(range(0, 2500000, 1000)):
        browser.execute_script('window.scrollTo(0,' + str(i) + ')')
        time.sleep(0.1)

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    data = []
    for i in soup.find_all('ytd-rich-item-renderer', class_='style-scope ytd-rich-grid-row'):
        link = "https://www.youtube.com/" + i.find('a', class_='yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media').get('href')
        title = i.find('a', class_='yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media').get('title')
        views = (i.find('span', class_="inline-metadata-item style-scope ytd-video-meta-block").text.split(" ")[0])
        upload_time = (i.find_all('span', class_="inline-metadata-item style-scope ytd-video-meta-block")[1].text)
        data.append([link, title, views, upload_time])

    df = pd.DataFrame(data, columns=['Link', 'Title', 'Views', 'Upload Time'])

    df.to_csv('data.csv', index=False)
    browser.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_company = request.form['company']
        scrape_youtube_data(input_company)
        return redirect(url_for('download'))

    return render_template('index.html')

@app.route('/download')
def download():
    path = os.path.join(os.getcwd(), 'data.csv')
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)