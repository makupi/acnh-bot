from acnh.database import db


class Guild(db.Model):
    __tablename__ = "guilds"

    id = db.Column(db.BIGINT, primary_key=True)
    prefix = db.Column(db.String)
    local_turnips = db.Column(db.Boolean, default=False)
