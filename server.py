import urllib
from http.client import HTTPException
from urllib.parse import urlsplit

from flask import Flask, render_template, request
from ftfy import fix_text
from scrapy.http import HtmlResponse

from src.utils.helper import parse_meta_from_tags

app = Flask(__name__)

POSTGRES = {
    'user': 'postgres',
    'pw': '123',
    'db': 'mh',
    'host': 'mh-x1',
    'port': '5431',
}


@app.route("/", methods=['GET'])
def hello():
    return render_template("home2.html")


@app.route("/parse-meta", methods=['POST'])
def parse_meta():
    url = request.form.get('url')
    scrapy_request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    con = urllib.request.urlopen(scrapy_request)
    new_response = con.read()
    new_response_text = fix_text(str(new_response, 'utf-8'))
    response = HtmlResponse(url=url, encoding='utf-8', body=new_response_text)
    title, description, published_time, tag_str = parse_meta_from_tags(response.text)
    domain = urlsplit(response.url).netloc

    return render_template("home2.html", raw_url=url, domain=domain, title=title,
                           description=description, published_time=published_time)


@app.route("/parse", methods=['POST'])
def parse():
    image_sources, video_sources, share_content, tag, author, raw_html = [], [], [], [], '', []

    url = request.form.get('url')
    if url is None or url == '':
        raise HTTPException("url cannot be empty")

    all_links = request.form.get('all_links')
    all_subs = request.form.get('all_subs')
    images = request.form.get('images')
    videos = request.form.get('videos')
    share_content = request.form.get('share_content')
    tag = request.form.get('tag')
    author = request.form.get('author')
    raw_html = request.form.get('raw_html')
    content = request.form.get('content')

    scrapy_request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    con = urllib.request.urlopen(scrapy_request)
    new_response = con.read()
    new_response_text = fix_text(str(new_response, 'utf-8'))
    response = HtmlResponse(url=url, encoding='utf-8', body=new_response_text)
    try:
        if all_links is not None and all_links != '':
            all_links = response.xpath(all_links).getall()

        if all_subs is not None and all_subs != '':
            all_subs = response.xpath(all_subs).getall()

        if content is not None and content != '':
            content = "".join(response.xpath(content).getall())

        if images is not None and images != '':
            image_sources = response.xpath(images).getall()

        if videos is not None and videos != '':
            video_sources = response.xpath(videos).getall()

        if share_content is not None and share_content != '':
            share_content = response.xpath(share_content).getall()

        if tag is not None and tag != '':
            tag = response.xpath(tag).getall()

        if author is not None and author != '':
            author = response.xpath(author).get()

        if raw_html is not None and raw_html != '':
            raw_html = response.xpath(raw_html).getall()
    except Exception as e:
        print(str(e))

    return render_template("home2.html", all_links=all_links, all_subs=all_subs, image_sources=image_sources,
                           video_sources=video_sources, share_content=share_content, tag=tag,
                           author=author, raw_html=raw_html, content=content)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
