import datetime
from flask_wtf import Form
from wtforms import (StringField, TextAreaField, PasswordField, IntegerField)
from wtforms.fields.html5 import DateField
#from wtforms.ext.dateutil.fields import DateField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp
from wtforms.widgets import HiddenInput
from models import Entry


def title_exists(form, field):
    entry_id = form.entry_id.data
    if Entry.select().where(
            (Entry.title == field.data) & (Entry.id != entry_id)
    ).exists():
            raise ValidationError('Entry with that title already exists.')


class EntryForm(Form):
    title = StringField(
        'Title',
        validators=[
            DataRequired(),
            Length(max=255),
            title_exists
        ]
    )
    date = DateField(
        'Date',
#        parse_kwargs={
#            'dayfirst': True,
#            'yearfirst': False
#        },
#        display_format='%d.%m.%Y'
    )
    time_spent = StringField(
        'Time Spent',
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )
    learned = TextAreaField(
        'What I learned',
        validators=[
            DataRequired()
        ]
    )
    to_remember = TextAreaField(
        'Resources to remember',
        validators=[
            DataRequired()
        ]
    )
    tags = StringField(
        'Tags',
        validators=[
            Length(max=255),
            Regexp(
                r'^[\w\s-]*$',
                message="Multiple tags should be separated by space."
            )
        ]
    )
    entry_id = IntegerField(
        widget=HiddenInput()
    )


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
