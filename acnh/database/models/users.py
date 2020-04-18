from acnh.database import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.BIGINT, primary_key=True)
    report_count = db.Column(db.Integer, default=0)
    turnip_banned = db.Column(db.Boolean, default=False)
    reports_created_count = db.Column(db.Integer, default=0)
