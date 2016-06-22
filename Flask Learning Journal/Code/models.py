import datetime
from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *
from slugify import slugify


DATABASE = SqliteDatabase('learning_journal.db')


class Entry(Model):
    title = CharField(max_length=255)
    created_at = DateField(default=datetime.datetime.now)
    learned = TextField()
    to_remember = TextField()
    time_spent = CharField(max_length=100)
    slug = CharField()
    tags = CharField(max_length=255, default='')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Entry, self).save(*args, **kwargs)

    class Meta:
        database = DATABASE
        order_by = ('-created_at',)


class User(UserMixin, Model):
    username = CharField(max_length=100, unique=True)
    password = CharField(max_length=100)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    password=generate_password_hash(password)
                )
        except IntegrityError:
            raise ValueError("User already exists!")


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry], safe=True)
    DATABASE.close()
