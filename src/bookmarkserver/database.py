from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow, fields
from marshmallow import fields as ma_fields
db = SQLAlchemy()
ma = Marshmallow()
class ShortUrl(db.Model):
    nameLength = 255
    maxUrlLength = 2000
    __tablename__ = 'shorturls'
    id = db.Column(db.Integer, primary_key=True)
    shortname = db.Column(db.String(255), nullable=False)
    longuri = db.Column(db.String(maxUrlLength))
    iconurl = db.Column(db.String)
    icondata = db.Column(db.String)

    def __repr__(self):
        representation = str()
        representation += "<"+\
        str(self.__class__.__name__)+ \
        ": id=" + str(self.id) +", "+ \
        "shortname=" + str(self.shortname) +", " + \
        'longuri="'+ str(self.longuri) + \
        'iconurl="' + str(self.iconurl) + '">'
        return representation

class ShortUrlSchema(ma.ModelSchema):
    class Meta:
        model = ShortUrl
        strict=True
        fields=('id', 'shortname', 'longuri', 'iconurl', 'icondata')
    # longuri = ma_fields.Url()
short_url_schema = ShortUrlSchema()