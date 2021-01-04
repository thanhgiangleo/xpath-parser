import sys
from urllib.parse import urlparse

import psycopg2

from src.models import config
from src.utils.helper import normalize_xpath


class Postgresql:
    __instance = None
    connection_str = None

    @staticmethod
    def getInstance():
        if Postgresql.__instance is None:
            Postgresql()
        return Postgresql.__instance

    def __init__(self):
        if Postgresql.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            try:
                self.connection_str = "host={} port={} dbname={} user={} password={}".format(config.POSTGRES_HOST,
                                                                                             config.POSTGRES_PORT,
                                                                                             config.POSTGRES_DB,
                                                                                             config.POSTGRES_USER,
                                                                                             config.POSTGRES_PASSWORD)
            except Exception as error:
                print(f"got exception while init postgresql {str(error)}")
                sys.exit()
            Postgresql.__instance = self

    def check_postgres_data(self, data):
        url = data['url']
        domain = urlparse(url).netloc
        scheme = urlparse(url).scheme
        existed = self.get_domain_by_name(domain)

        if existed is not None:
            print(existed)
            self.update_domain_info(domain, data, scheme)
        else:
            self.insert(scheme=scheme,
                        domain=domain,
                        all_links=normalize_xpath(data['all_links']),
                        all_subs=normalize_xpath(data['all_subs']),
                        next_page=normalize_xpath(data['next_page']),
                        content=normalize_xpath(data['content']),
                        image_sources=normalize_xpath(data['image_sources']),
                        video_sources=normalize_xpath(data['video_sources']),
                        author=normalize_xpath(data['author_display_name']),
                        tags=normalize_xpath(data['tags']),
                        published_time=normalize_xpath(data['published_time']),
                        share_content=normalize_xpath(data['share_content']),
                        raw_html=normalize_xpath(data['raw_html']) if 'raw_html' in data else '')

    def insert(self, scheme, domain, all_links, all_subs, next_page, content, image_sources, video_sources, author,
               tags, published_time, share_content, raw_html):
        con = None
        mycursor = None
        try:
            con = psycopg2.connect(self.connection_str)
            mycursor = con.cursor()

            insert_query = """
                INSERT INTO crawler.domain(domain,all_links,all_subs,next_page,content,image_sources,video_sources,author_display_name,tags,published_time,share_content,raw_html,scheme)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            record_to_insert = (domain, all_links, all_subs, next_page, content, image_sources,
                                video_sources, author, tags, published_time, share_content, raw_html, scheme)
            mycursor.execute(insert_query, record_to_insert)
            con.commit()
        except Exception as error:
            print(error)
        finally:
            if mycursor is not None:
                mycursor.close()
            if con is not None:
                con.close()

    def get_domain_by_name(self, name):
        result = None
        con = None
        mycursor = None
        try:
            con = psycopg2.connect(self.connection_str)
            mycursor = con.cursor()
            mycursor.execute("SELECT * FROM crawler.domain WHERE domain LIKE '%{}%'".format(name))
            result = mycursor.fetchone()
            return result
        except Exception as error:
            print(error)
        finally:
            if mycursor is not None:
                mycursor.close()
            if con is not None:
                con.close()
        return result

    def update_domain_info(self, name, xpaths, scheme):
        con = None
        mycursor = None
        try:
            con = psycopg2.connect(self.connection_str)
            mycursor = con.cursor()

            update_query = """
                UPDATE crawler.domain SET all_links=%s,all_subs=%s,content=%s,image_sources=%s,
                video_sources=%s,author_display_name=%s,tags=%s,published_time=%s,share_content=%s,raw_html=%s,scheme=%s
                WHERE domain LIKE %s
            """
            record_to_update = (xpaths['all_links'], xpaths['all_subs'], xpaths['content'],
                                xpaths['image_sources'], xpaths['video_sources'], xpaths['author_display_name'],
                                xpaths['tags'], xpaths['published_time'], xpaths['share_content'], xpaths['raw_html'],
                                scheme, name)

            mycursor.execute(update_query, record_to_update)
            con.commit()

            row_count = mycursor.rowcount
            print(f"{row_count} has been updated - domain {name}")

        except Exception as error:
            print(error)
        finally:
            if mycursor is not None:
                mycursor.close()
            if con is not None:
                con.close()
