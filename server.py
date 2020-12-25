from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

POSTGRES = {
    'user': 'postgres',
    'pw': '123',
    'db': 'mh',
    'host': 'mh-x1',
    'port': '5431',
}

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db = SQLAlchemy(app)
#
# db.create_all()


# class DomainModel(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     domain = db.Column(db.TEXT)
#     all_links = db.Column(db.TEXT)
#     all_subs = db.Column(db.TEXT)
#     next_page = db.Column(db.TEXT)
#     author_display_name = db.Column(db.TEXT)
#     published_time = db.Column(db.TEXT)
#     content = db.Column(db.TEXT)
#     image_sources = db.Column(db.TEXT)
#     video_sources = db.Column(db.TEXT)
#     tags = db.Column(db.TEXT)
#     share_content = db.Column(db.TEXT)
#     raw_html = db.Column(db.TEXT)
#
#     def __init__(self, domain, all_links, all_subs, next_page, author_display_name, published_time,
#                  content, image_sources, video_sources, tags, share_content, raw_html):
#         self.domain = domain
#         self.all_links = all_links
#         self.all_subs = all_subs
#         self.next_page = next_page
#         self.author_display_name = author_display_name
#         self.published_time = published_time
#         self.content = content
#         self.image_sources = image_sources
#         self.video_sources = video_sources
#         self.tags = tags
#         self.share_content = share_content
#         self.raw_html = raw_html
#
#     def __repr__(self):
#         return f"<Car {self.domain}>"


@app.route("/", methods=['GET'])
def hello():
    # domains = DomainModel.query.all()
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
