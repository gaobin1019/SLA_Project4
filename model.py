from app import db
#table schema for tao quotes 
class TaoQuotes(db.Model):
    tag = db.Column(db.String(25),primary_key=True)
    quote = db.Column(db.String(1024),primary_key=True)

    def __init__(self,category,quote):
        self.tag = tag
        self.quote = quote

    def __repr__(self):
        return '<tag %s,quote %s>' % (self.tag,self.quote)
