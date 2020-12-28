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
    image_sources, video_sources, share_content, content, tag, author, raw_html = [], [], [], '', [], '', []
    domain, title, description, published_time = '', '', '', ''
    all_links, all_subs = [], []

    url = request.form.get('url')
    if url is None or url == '':
        raise HTTPException("url cannot be empty")

    all_links_xp = request.form.get('all_links_xp')
    all_subs_xp = request.form.get('all_subs_xp')
    images_xp = request.form.get('images_xp')
    videos_xp = request.form.get('videos_xp')
    share_content_xp = request.form.get('share_content_xp')
    tag_xp = request.form.get('tag_xp')
    author_xp = request.form.get('author_xp')
    raw_html_xp = request.form.get('raw_html_xp')
    content_xp = request.form.get('content_xp')

    scrapy_request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    con = urllib.request.urlopen(scrapy_request)
    new_response = con.read()
    new_response_text = fix_text(str(new_response, 'utf-8'))
    response = HtmlResponse(url=url, encoding='utf-8', body=new_response_text)
    try:
        domain = urlsplit(response.url).netloc
        title, description, published_time, tag_str = parse_meta_from_tags(response.text)

        if all_links_xp is not None and all_links_xp != '':
            all_links = response.xpath(all_links_xp).getall()

        if all_subs_xp is not None and all_subs_xp != '':
            all_subs = response.xpath(all_subs_xp).getall()

        if content_xp is not None and content_xp != '':
            content = "".join(response.xpath(content_xp).getall())

        if images_xp is not None and images_xp != '':
            image_sources = response.xpath(images_xp).getall()

        if videos_xp is not None and videos_xp != '':
            video_sources = response.xpath(videos_xp).getall()

        if share_content_xp is not None and share_content_xp != '':
            share_content = response.xpath(share_content_xp).getall()

        if tag_xp is not None and tag_xp != '':
            tag = response.xpath(tag_xp).getall()

        if author_xp is not None and author_xp != '':
            author = response.xpath(author_xp).get()

        if raw_html_xp is not None and raw_html_xp != '':
            raw_html = response.xpath(raw_html_xp).getall()

    except Exception as e:
        print(str(e))

    return render_template("home2.html", raw_url=url,
                           domain=domain, title=title, description=description, published_time=published_time,
                           all_links=all_links, all_links_xp=all_links_xp,
                           all_subs=all_subs, all_subs_xp=all_subs_xp,
                           tag=tag, tag_xp=tag_xp,
                           image_sources=image_sources, images_xp=images_xp,
                           video_sources=video_sources, videos_xp=videos_xp,
                           share_content=share_content, share_content_xp=share_content_xp,
                           author=author, author_xp=author_xp,
                           raw_html=raw_html, raw_html_xp=raw_html_xp,
                           content=content, content_xp=content_xp)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
