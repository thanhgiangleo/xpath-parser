import re
from datetime import datetime
from urllib.parse import urlparse

from extruct import JsonLdExtractor, RDFaExtractor, OpenGraphExtractor
from ftfy import fix_text


def normalize_xpath(xpath):
    if xpath.find("*") != -1:
        xpath = xpath.replace("*", "'*'")
    if xpath == '':
        return ''
    return xpath


def normalize_url(url):
    if url.find('https://') != -1 or url.find('http://') != -1:
        url = url.replace('https://', '').replace('http://', '')
    if url.find('www.') != -1:
        url = url.replace('www.', '')
    return url


def normalize_tag(text):
    if text:
        if text.find("\r\n") != -1 or text.find("\n") != -1 or text.find("\t") != -1 or text.find("#") != -1:
            text = text.replace("\r\n", "").replace("\n", "").replace("\t", "").replace("#", "")
        return fix_text(text).strip()
    return ""


def normalize_raw_content(text):
    if text:
        if text.find("\r\n") != -1 or text.find("\n") != -1 or text.find("\t") != -1:
            text = text.replace("\r\n", "").replace("\n", "").replace("\t", "")
        if text.find(",") == len(text) - 1:
            text = text[:-1]
        return fix_text(text.replace("\xa0", " ")).strip()
    return ""


def normalize_content(text):
    if text:
        if text.find("\r\n") != -1 or text.find("\n") != -1:
            text = text.replace("\r\n", "").replace("\n", "")
        if text.find(",") == len(text) - 1:
            text = text[:-1]
        return fix_text(text.replace("\xa0", " ")).strip()
    return ""


def normalize_author_display_name(name):
    if name:
        if name.find(",") == len(name) - 1 or name.find("-") == len(name) - 1:
            name = name[:-1]
        if name.startswith('Theo'):
            name = name.replace('Theo', '')
        if name.find("|") != -1:
            name = name.replace('|', '')
        if name.find("\r\n") != -1 or name.find("\n") != -1:
            name = name.replace("\r\n", "").replace("\n", "")
        return fix_text(name).strip()
    return None


def normalize_published_date(d):
    if d:
        split = d.split(",")
        if len(split) == 3:
            split2 = d.split(":")
            if len(split2) == 3:
                # Cập nhật: 14:36, Thứ 7, 07/11/2020
                date_str = (d.split(",")[2]).strip()
                time_str = (d.split(",")[0][-5:] + ":00").strip()
                date_time_str = date_str + " " + time_str
                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
                return date_time_obj
            elif len(split2) == 2:
                try:
                    # Thứ bảy, 31/10/2020, 08:22 (GMT+7)
                    date_str = (d.split(",")[1]).strip()
                    time_str = (d.split(",")[2][:6] + ":00").strip()
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                        "%Y/%m/%d %H:%M:%S")
                    return date_time_obj
                except:
                    # Cập nhật lúc 14:35, Thứ Ba, 17/11/2020 (GMT+7)
                    date_str = (d.split(",")[2][:11]).strip()
                    time_str = (d.split(",")[0][-5:] + ":00").strip()
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                        "%Y/%m/%d %H:%M:%S")
                    return date_time_obj
        elif len(split) == 2:
            split2 = d.split(":")
            if len(split2) == 2:
                try:
                    # 18:50, 08/11/2020
                    date_str = d.split(",")[1].strip()
                    time_str = d.split(",")[0].strip() + ":00"
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                        "%Y/%m/%d %H:%M:%S")
                    return date_time_obj
                except:
                    split3 = d.split(" ")
                    if len(split3) == 2:
                        # 16/11/2020, 09:06
                        date_str = d.split(",")[0].strip()
                        time_str = d.split(",")[1].strip() + ":00"
                        date_time_str = date_str + " " + time_str
                        date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                            "%Y/%m/%d %H:%M:%S")
                        return date_time_obj
                    elif len(split3) == 3:
                        # 6:37 PM, 04/12/2020
                        date_str = split3[2].strip()
                        time_str = split3[0].strip() + ":00"
                        date_time_str = date_str + " " + time_str
                        date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                            "%Y/%m/%d %H:%M:%S")
                        return date_time_obj
                    elif len(split3) == 5:
                        try:
                            # 11:09 | Thứ bảy, 12/12/2020
                            date_str = split[1].strip()
                            time_str = split3[0].strip() + ":00"
                            date_time_str = date_str + " " + time_str
                            date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                                "%Y/%m/%d %H:%M:%S")
                            return date_time_obj
                        except:
                            try:
                                # Thứ tư, 06/09/2017 | 07:25
                                date_str = split3[2].strip()
                                time_str = split3[4].strip() + ":00"
                                date_time_str = date_str + " " + time_str
                                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                                    "%Y/%m/%d %H:%M:%S")
                                return date_time_obj
                            except:
                                # Thứ Ba, 08/12/2020 2:51 CH
                                date_str = split3[2].strip()
                                time_str = split3[3].strip() + ":00"
                                date_time_str = date_str + " " + time_str
                                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                                    "%Y/%m/%d %H:%M:%S")
                                return date_time_obj
                    elif len(split3) == 10:
                        # Thứ sáu, ngày 27 tháng 11 năm 2020 | 12:0
                        date_str = (split3[3] + "/" + split3[5] + "/" + split3[7]).strip()
                        time_str = split3[9].strip() + ":00"
                        date_time_str = date_str + " " + time_str
                        date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                            "%Y/%m/%d %H:%M:%S")
                        return date_time_obj
                    elif len(split3) == 4:
                        try:
                            # Thứ Ba, 17/11/2020 18:09
                            date_str = d.split(" ")[2].strip()
                            time_str = d.split(" ")[3].strip() + ":00"
                            date_time_str = date_str + " " + time_str
                            date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                                "%Y/%m/%d %H:%M:%S")
                            return date_time_obj
                        except:
                            # Thứ Hai, 30/11/2020 11:2'(GMT+7)
                            date_str = split3[2].strip()
                            time_str = split3[3].replace("\'(GMT+7)", "") + ":00"
                            date_time_str = date_str + " " + time_str
                            date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                                "%Y/%m/%d %H:%M:%S")
                            return date_time_obj
                    elif len(split3) == 6:
                        try:
                            # Thứ Ba, 20/10/2020 18:38 GMT +7
                            date_str = split3[2].strip()
                            time_str = split3[3].strip() + ":00"
                            date_time_str = date_str + " " + time_str
                            date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                                "%Y/%m/%d %H:%M:%S")
                            return date_time_obj
                        except:
                            # Thứ bảy, 12/12/2020 | 22:00 GMT+7
                            date_str = split3[2].strip()
                            time_str = split3[4].strip() + ":00"
                            date_time_str = date_str + " " + time_str
                            date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                                "%Y/%m/%d %H:%M:%S")
                            return date_time_obj
            elif len(split2) == 3:
                try:
                    # 17:03:00 - Thứ 2, 07/12/2020                     |
                    date_str = split[1].replace("|", "").strip()
                    time_str = split[0][:8]
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
                    return date_time_obj
                except Exception as e:
                    print(str(e))
                    try:
                        # Chủ nhật, 03.01.2021 | 10:00:41
                        split3 = split[1].split("|")
                        date_str = split3[0].strip()
                        time_str = split3[1].strip()
                        date_time_str = date_str + " " + time_str
                        date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                            "%Y/%m/%d %H:%M:%S")
                        return date_time_obj
                    except Exception as e:
                        print(str(e))
            else:
                try:
                    # Thứ Bảy, ngày 31/10/2020 19:40 PM (GMT+7)
                    # Chủ nhật, 1/11/2020 09:38 (GMT+7)
                    # Thứ hai, 20/4/2020 06:30 (GMT+7)
                    parse = (d.split(",")[1]).strip()
                    date_str = parse[5:15]
                    time_str = parse[16:21] + ":00"
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
                    return date_time_obj
                except:
                    # Chủ nhật, 13.12.2020 | 09:06:22
                    parse = (d.split(",")[1]).strip()
                    date_str = parse[0:10]
                    time_str = parse[13:]
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d.%m.%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
                    return date_time_obj
        elif len(split) == 1:
            split2 = d.strip().split(" ")
            if len(split2) == 7:
                # Cập nhật ngày: 10/12/2020 22:14 (GMT +7)
                date_str = (split2[3]).strip()
                time_str = (split2[4] + ":00").strip()
                date_time_str = date_str + " " + time_str
                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
                return date_time_obj
            elif len(split2) == 6:
                try:
                    # Thứ Tư 25/11/2020 | 17:07 GMT+7
                    date_str = (split2[2]).strip()
                    time_str = (split2[4] + ":00").strip()
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
                    return date_time_obj
                except:
                    # 16/12/2020 17:52 Số lượt xem: 217
                    date_str = (split2[0]).strip()
                    time_str = (split2[1] + ":00").strip()
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
                    return date_time_obj
            elif len(split2) == 5:
                try:
                    # Cập nhật lúc 11:26 29/11/2013
                    date_str = (split2[4]).strip()
                    time_str = (split2[3] + ":00").strip()
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
                    return date_time_obj
                except:
                    # Đăng lúc: 08/12/2020 11:30 (GMT+7)
                    date_str = (split2[2]).strip()
                    time_str = (split2[3] + ":00").strip()
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime("%Y/%m/%d %H:%M:%S")
                    return date_time_obj
            elif len(split2) == 4:
                split3 = d.split("-")
                if len(split3) == 4:
                    # 04-11-2020 - 22:56 PM
                    date_str = (split2[0]).strip()
                    time_str = (split2[2][:5] + ":00").strip()
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d-%m-%Y %H:%M:%S").strftime(
                        "%Y/%m/%d %H:%M:%S")
                    return date_time_obj
                elif len(split3) == 3:
                    # Cập nhật: 17:18 21-11-2020
                    date_str = (split2[3]).strip()
                    time_str = (split2[2][:5] + ":00").strip()
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d-%m-%Y %H:%M:%S").strftime(
                        "%Y/%m/%d %H:%M:%S")
                    return date_time_obj
                elif len(split3) == 1:
                    # 22:00 | 01/01/2021 |
                    split4 = d.split("|")
                    if len(split4) == 3:
                        date_str = split4[1].strip()
                        time_str = split4[0].strip() + ":00"
                        date_time_str = date_str + " " + time_str
                        date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                            "%Y/%m/%d %H:%M:%S")
                        return date_time_obj
                else:
                    # Thứ Hai 02/11/2020 18:10(GMT+7)
                    date_str = (split2[2]).strip()
                    time_str = (split2[3][:5] + ":00").strip()
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                        "%Y/%m/%d %H:%M:%S")
                    return date_time_obj
            elif len(split2) == 3:
                try:
                    # 11/7/2020 4:35:08 PM
                    date_str = (split2[0]).strip()
                    time_str = (split2[1][:8]).strip()
                    date_time_str = date_str + " " + time_str
                    date_time_obj = datetime.strptime(date_time_str, "%m/%d/%Y %H:%M:%S").strftime(
                        "%Y/%m/%d %H:%M:%S")
                    return date_time_obj
                except:
                    try:
                        # 12/10/2020 14:20 (GMT+7)
                        date_str = (split2[0]).strip()
                        time_str = (split2[1][:8]).strip() + ":00"
                        date_time_str = date_str + " " + time_str
                        date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                            "%Y/%m/%d %H:%M:%S")
                        return date_time_obj
                    except:
                        try:
                            # 03:01 PM 18/11/2020
                            date_str = (split2[2][:8]).strip()
                            time_str = (split2[0]).strip() + ":00"
                            date_time_str = date_str + " " + time_str
                            date_time_obj = datetime.strptime(date_time_str, "%d/%m/%y %H:%M:%S").strftime(
                                "%Y/%m/%d %H:%M:%S")
                            return date_time_obj
                        except:
                            try:
                                date_str = split2[0].strip()
                                time_str = split2[1].strip() + ":00"
                                date_time_str = date_str + " " + time_str
                                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S") \
                                    .strftime("%Y/%m/%d %H:%M:%S")
                                return date_time_obj
                            except:
                                date_str = split2[0].strip()
                                time_str = split2[2].strip() + ":00"
                                date_time_str = date_str + " " + time_str
                                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S") \
                                    .strftime("%Y/%m/%d %H:%M:%S")
                                return date_time_obj
            elif len(split2) == 2:
                split3 = d.split(":")
                if len(split3) == 2:
                    # 23:38 30/10/2020
                    try:
                        time_str = (split2[0][:8]).strip() + ":00"
                        date_str = (split2[1]).strip()
                        date_time_str = date_str + " " + time_str
                        date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                            "%Y/%m/%d %H:%M:%S")
                        return date_time_obj
                    except:
                        try:
                            # 30/10/2020 23:38
                            date_str = (split2[0][:10]).strip()
                            time_str = (split2[1]).strip() + ":00"
                            date_time_str = date_str + " " + time_str
                            date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                                "%Y/%m/%d %H:%M:%S")
                            return date_time_obj
                        except:
                            # 14-12-2020 18:34
                            date_str = (split2[0][:10]).strip()
                            time_str = (split2[1]).strip() + ":00"
                            date_time_str = date_str + " " + time_str
                            date_time_obj = datetime.strptime(date_time_str, "%d-%m-%Y %H:%M:%S").strftime(
                                "%Y/%m/%d %H:%M:%S")
                            return date_time_obj
                elif len(split3) == 3:
                    try:
                        # 10:26:00 07/11/2020
                        time_str = (split2[0][:5] + ":00").strip()
                        date_str = (split2[1]).strip()
                        date_time_str = date_str + " " + time_str
                        date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y %H:%M:%S").strftime(
                            "%Y/%m/%d %H:%M:%S")
                        return date_time_obj
                    except:
                        # 2020-11-21 09:13:15
                        time_str = (split2[1]).strip()
                        date_str = (split2[0]).strip()
                        date_time_str = date_str + " " + time_str
                        date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S").strftime(
                            "%Y/%m/%d %H:%M:%S")
                        return date_time_obj
            elif len(split2) == 1:
                split3 = d.split("T")
                if len(split3) == 2:
                    try:
                        # 2020-11-24ICT20:16:23
                        date_time_obj = datetime.strptime(d, '%Y-%m-%dICT%H:%M:%S').strftime("%Y/%m/%d %H:%M:%S")
                    except:
                        # 2020-11-01T14:57:56+0700
                        # 2020-11-02T13:30:00
                        try:
                            date_time_obj = datetime.strptime(d, '%Y-%m-%dT%H:%M:%S%z').strftime(
                                "%Y/%m/%d %H:%M:%S")
                        except:
                            try:
                                date_time_obj = datetime.strptime(d, '%Y-%m-%dT%H:%M:%S').strftime(
                                    "%Y/%m/%d %H:%M:%S")
                            except:
                                try:
                                    date_time_obj = datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%f').strftime(
                                        "%Y/%m/%d %H:%M:%S")
                                except:
                                    # 2020-12-01T14:27:51.000+0700
                                    date_time_obj = datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%f%z').strftime(
                                        "%Y/%m/%d %H:%M:%S")
                    return date_time_obj
                elif len(split3) == 3:
                    # 2020-11-11T17:38:40T+07:00
                    date_time_obj = datetime.strptime(d.strip(), '%Y-%m-%dT%H:%M:%ST%z').strftime(
                        "%Y/%m/%d %H:%M:%S")
                    return date_time_obj
        return d


def parse_meta_from_tags(response_text):
    title, description, published_time, tag, pubdate = '', '', '', '', ''

    # stupid case
    if response_text.replace("\n", "").find("},    </script>") != -1:
        response_text = response_text.replace("\n", "").replace("},    </script>", "}    </script>")

    response_text = re.sub(r'("[\s\w]*)"([\s\w]*")', r"\1\'\2", response_text)

    jsonLdExt = JsonLdExtractor()
    try:
        jsonLdData = jsonLdExt.extract(htmlstring=response_text)
        if jsonLdData and len(jsonLdData) > 0:
            for jsonLdDataItem in jsonLdData:
                if '@type' not in jsonLdDataItem:
                    continue
                if jsonLdDataItem['@type'] == 'NewsArticle' or jsonLdDataItem['@type'] == 'Article':
                    if 'headline' in jsonLdDataItem:
                        title = jsonLdDataItem['headline']
                    if 'description' in jsonLdDataItem:
                        description = jsonLdDataItem['description']
                    if 'datePublished' in jsonLdDataItem or 'uploadDate' in jsonLdDataItem:
                        published_time = jsonLdDataItem['datePublished'] if jsonLdDataItem['datePublished'] else \
                            jsonLdDataItem['uploadDate']
                if published_time == '' and 'uploadDate' in jsonLdDataItem:
                    published_time = jsonLdDataItem['uploadDate']
                if title == '' and 'name' in jsonLdDataItem:
                    title = jsonLdDataItem['name']
                if description == '' and 'description' in jsonLdDataItem:
                    description = jsonLdDataItem['description']
    except Exception as e:
        print(str(e))

    if title == '' and description == '' and published_time == '':
        rdfaExt = RDFaExtractor()
        rdfaData = rdfaExt.extract(htmlstring=response_text)
        if rdfaData and len(rdfaData) > 0:
            for rdfaDataItem in rdfaData:
                if 'http://ogp.me/ns#description' in rdfaDataItem:
                    description = rdfaDataItem['http://ogp.me/ns#description'][0]['@value']
                if 'http://ogp.me/ns#title' in rdfaDataItem:
                    title = rdfaDataItem['http://ogp.me/ns#title'][0]['@value']
                if 'http://ogp.me/ns/article#published_time' in rdfaDataItem:
                    published_time = rdfaDataItem['http://ogp.me/ns/article#published_time'][0]['@value']
                if 'http://ogp.me/ns/article#tag' in rdfaDataItem:
                    tag = rdfaDataItem['http://ogp.me/ns/article#tag'][0]['@value']

    if title == '' and description == '' and published_time == '':
        ogExt = OpenGraphExtractor()
        ogData = ogExt.extract(htmlstring=response_text)
        if ogData and len(ogData) > 0:
            for ogDataItem in ogData:
                if 'properties' not in ogDataItem:
                    continue
                if len(ogDataItem['properties']) > 0:
                    for ogDataSubItem in ogDataItem['properties']:
                        if ogDataSubItem[0] == 'og:title':
                            title = ogDataSubItem[1]
                        if ogDataSubItem[0] == 'og:description':
                            description = ogDataSubItem[1]

    if published_time != '' and len(published_time) > 10:
        # catch len(pubdate) > 10 for the case %Y-%M-%d only
        pubdate = normalize_published_date(published_time)

    return fix_text(title), fix_text(description), fix_text(pubdate), fix_text(tag)


def normalize_whole_item(item):
    # domain
    domain = item['domain']
    normalized_domain = normalize_url(item['domain'])
    item['domain'] = normalized_domain

    scheme = urlparse(item['raw_url']).scheme

    # title
    item['title'] = normalize_content(item['title'])

    # content
    item['content'] = normalize_content(item['content'])

    # summary
    item['summary'] = normalize_content(item['summary'])

    # share_content
    normalized_content = []
    for sc_resource in item['share_content']:
        if sc_resource == '':
            continue
        if sc_resource.startswith('/'):
            sc_resource = f'{domain}{sc_resource}'
        if 'https://' not in sc_resource and 'http://' not in sc_resource:
            sc_resource = f'{scheme}://{sc_resource}'
        normalized_content.append(sc_resource)
    item['share_content'] = normalized_content

    # images
    normalized_images = []
    for img_resource in item['image_sources']:
        img_resource = img_resource.strip()
        if img_resource == '':
            continue
        if img_resource.find(domain) != -1:
            if img_resource.startswith('/'):
                img_resource = f'{domain}{img_resource}'
            if 'https://' not in img_resource and 'http://' not in img_resource:
                img_resource = f'{scheme}://{img_resource}'
        else:
            if img_resource.startswith('/') or img_resource.startswith('//'):
                img_resource = f'{scheme}:{img_resource}'
        normalized_images.append(img_resource)
    item['image_sources'] = normalized_images

    # videos
    normalized_videos = []
    for vid_resource in item['video_sources']:
        if vid_resource == '':
            continue
        if vid_resource.startswith('//'):
            vid_resource = vid_resource.replace('//', '')
        if vid_resource.startswith('/'):
            vid_resource = f'{domain}{vid_resource}'
        if 'https://' not in vid_resource and 'http://' not in vid_resource:
            vid_resource = f'{scheme}://{vid_resource}'
        normalized_videos.append(vid_resource)
    item['video_sources'] = normalized_videos

    # author
    author = item['author_display_name']
    if author is None or (author and author.find("All about Football") != -1):
        author = ''
    item['author_display_name'] = normalize_author_display_name(author)

    # raw_html
    raw_html = []
    raw_html_parsed = item['raw_html']
    for raw_item in raw_html_parsed:
        raw_item_norm = normalize_raw_content(raw_item)
        if raw_item_norm != "":
            raw_html.append(raw_item_norm)
    item['raw_html'] = "".join(raw_html)

    # tag
    tag = item['tag']
    list_tags_normalize = []
    if tag and isinstance(tag, str):
        list_tags = re.split('[,;]', tag)
        for tag_item in list_tags:
            tag_item_norm = normalize_tag(tag_item)
            if tag_item_norm != "":
                list_tags_normalize.append(tag_item_norm)

    item['tag'] = list_tags_normalize

    return item
