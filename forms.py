from flask_wtf import Form
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length


class TagField(StringField):
    """Custom form field for entry tags."""
    def _value(self):
        if self.data:
            return ' '.join(self.data)
        else:
            return ''

    def __init__(self, label='', validators=None, remove_duplicates=True,
                 **kwargs):
        super(StringField, self).__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].split()
        else:
            self.data = []

        if self.remove_duplicates:
            self.data = list(self._remove_duplicates(self.data))

    @classmethod
    def _remove_duplicates(cls, seq):
        """Remove duplicates in a case insensitive, but case preserving
        manner."""
        d = {}
        for item in seq:
            if item.lower() not in d:
                d[item.lower()] = True
                yield item


class EntryForm(Form):
    title = StringField(
        'Title',
        validators=[
            DataRequired(),
            Length(max=255),
        ]
    )
    created_at = DateField(
        'Date',
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
    tags = TagField(
        'Tags',
        validators=[
             Length(max=255)
        ]
    )


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
