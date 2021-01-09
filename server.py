import urllib
from datetime import datetime
from http.client import HTTPException
from urllib.parse import urlsplit

from flask import Flask, render_template, request
from ftfy import fix_text
from scrapy.http import HtmlResponse

from src.models.postgresql import Postgresql
from src.utils.helper import parse_meta_from_tags, normalize_published_date, normalize_whole_item

app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello():
    return render_template("home.html")


@app.route("/check_existed_domain", methods=['POST'])
def check_existed_domain():
    request_payload = request.json
    if request_payload is None or request_payload['domain'] == '':
        raise HTTPException("Bad request")

    try:
        result = Postgresql.getInstance().get_domain_by_name(request_payload['domain'])
        return "existed" if result is not None and result[2] is not None and result[3] is not None else "Not existed"
    except Exception as err:
        print(str(err))
        return "failed"


@app.route("/submit", methods=['POST'])
def submit_pg():
    request_payload = request.json
    if request_payload is None:
        raise HTTPException("Bad request")

    try:
        Postgresql.getInstance().check_postgres_data(request_payload)
        return "success"
    except Exception as err:
        print(str(err))
        return "failed"


@app.route("/parse", methods=['POST'])
def parse():
    image_sources, video_sources, share_content, content, tag, author, raw_html = [], [], [], '', '', '', []
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
    published_time_xp = request.form.get('published_time_xp')

    scrapy_request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    con = urllib.request.urlopen(scrapy_request)
    new_response = con.read()
    new_response_text = fix_text(str(new_response, 'utf-8'))
    response = HtmlResponse(url=url, encoding='utf-8', body=new_response_text)
    try:
        domain = urlsplit(response.url).netloc
        title, description, published_time, tag_str = parse_meta_from_tags(response.text)

        if published_time == '':
            time = response.xpath("//meta[@property='article:published_time']/@content").get()
            published_time = normalize_published_date(time)
            try:
                datetime.strptime(published_time, "%d/%m/%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
            except:
                try:
                    datetime.strptime(published_time, "%Y/%m/%d %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
                except:
                    published_time = ''

        if published_time == '' and published_time_xp is not None and published_time_xp != '':
            parsed = response.xpath(published_time_xp).getall()
            if parsed:
                if len(parsed) == 1:
                    published_time = normalize_published_date(parsed[0].strip())
                elif len(parsed) > 1:
                    time = " ".join(parsed)
                    published_time = normalize_published_date(time.strip())

        try:
            datetime.strptime(published_time + " 00:00:00", "%d-%m-%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
            published_time = published_time + " 00:00:00"
        except Exception as e:
            print("Parse : " + str(e))

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
            tag = ",".join(response.xpath(tag_xp).getall())

        if author_xp is not None and author_xp != '':
            author = response.xpath(author_xp).get()

        if raw_html_xp is not None and raw_html_xp != '':
            raw_html = response.xpath(raw_html_xp).getall()

    except Exception as e:
        print("Parse error : " + str(e))

    parsed_item = {
        'raw_url': url,
        'domain': domain,
        'title': title,
        'summary': description,
        'content': content,
        'image_sources': image_sources,
        'video_sources': video_sources,
        'share_content': share_content,
        'author_display_name': author,
        'tag': tag,
        'raw_html': raw_html,
    }

    normalized_item = normalize_whole_item(parsed_item)

    return render_template("home.html", all_links=all_links, all_links_xp=all_links_xp,
                           all_subs=all_subs, all_subs_xp=all_subs_xp,
                           raw_url=normalized_item.get('raw_url'),
                           domain=normalized_item.get('domain'),
                           title=normalized_item.get('title'),
                           description=normalized_item.get('summary'),
                           published_time=published_time, published_time_xp=published_time_xp,
                           tag=normalized_item.get('tag'), tag_xp=tag_xp,
                           image_sources=normalized_item.get('image_sources'), images_xp=images_xp,
                           video_sources=normalized_item.get('video_sources'), videos_xp=videos_xp,
                           share_content=normalized_item.get('share_content'), share_content_xp=share_content_xp,
                           author=normalized_item.get('author_display_name'), author_xp=author_xp,
                           raw_html=normalized_item.get('raw_html'), raw_html_xp=raw_html_xp,
                           content=normalized_item.get('content'), content_xp=content_xp)


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
