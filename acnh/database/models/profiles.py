from acnh.database import db


class Profile(db.Model):
    __tablename__ = "profiles"

    user_id = db.Column(db.BIGINT, primary_key=True)
    friend_code = db.Column(db.Text, default="Not Set")
    island_name = db.Column(db.Text, default="Not Set")
    user_name = db.Column(db.Text, default="Not Set")
    fruit = db.Column(db.Text, default="Not Set")
    is_northern = db.Column(db.Boolean)
    timezone = db.Column(db.Text)
    flower = db.Column(db.Text)
    airport = db.Column(db.Text)
