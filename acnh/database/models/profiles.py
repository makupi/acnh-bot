from acnh.database import db


class Profile(db.Model):
    __tablename__ = "profiles"

    user_id = db.Column(db.BIGINT, db.ForeignKey("users.user_id"), primary_key=True)
    friend_code = db.Column(db.Text)
    island_name = db.Column(db.Text)
    user_name = db.Column(db.Text)
    fruit = db.Column(db.Text)
    is_northern = db.Column(db.Boolean)
