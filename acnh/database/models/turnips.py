from acnh.database import db


class Turnip(db.Model):
    __tablename__ = "turnips"

    user_id = db.Column(db.BIGINT, primary_key=True)
    guild_id = db.Column(db.BIGINT)
    is_selling = db.Column(db.Boolean)
    invite_key = db.Column(db.String)
    price = db.Column(db.Integer)
    open_time = db.Column(db.TIMESTAMP)
