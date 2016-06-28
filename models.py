import datetime

from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *
from slugify import slugify


DATABASE = SqliteDatabase('learning_journal.db')


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


class Entry(Model):
    title = CharField(max_length=255)
    created_at = DateField(default=datetime.datetime.now)
    learned = TextField()
    to_remember = TextField()
    time_spent = CharField(max_length=100)
    slug = CharField()

    def save(self, *args, **kwargs):
        # Generate a slug based on the entry title.
        slug = slugify(self.title)
        # Ensures uniqueness of slug by appending -1, -2, -3 etc if necessary.
        count = Entry.select().where(Entry.slug == slug).count()
        if count:
            slug += '-' + str(count)
        self.slug = slug
        super(Entry, self).save(*args, **kwargs)

    def get_tags(self):
        """Returns entry tags."""
        return Tag.select().join(EntryTag).join(Entry).where(
            Entry.id == self.id)

    class Meta:
        database = DATABASE
        order_by = ('-created_at',)


class Tag(Model):
    name = CharField(max_length=100)

    def get_entries(self):
        """Returns all entries with the current tag."""
        return Entry.select().join(EntryTag).join(Tag).where(Tag.id == self.id)

    def __str__(self):
        return self.name

    class Meta:
        database = DATABASE


class EntryTag(Model):
    entry = ForeignKeyField(Entry)
    tag = ForeignKeyField(Tag)

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry, Tag, EntryTag], safe=True)
    DATABASE.close()
