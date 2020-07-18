from acnh.database import db


class Listing(db.Model):
    __tablename__ = "listings"

    user_id = db.Column(db.BIGINT, primary_key=True)
    guild_id = db.Column(db.BIGINT, db.ForeignKey("guilds.id"))
    invite_key = db.Column(db.Text)
    open_time = db.Column(db.TIMESTAMP)
    message = db.Column(db.Text)
