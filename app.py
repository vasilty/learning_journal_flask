import datetime
from flask import (Flask, render_template, url_for, redirect, g, request,
                   abort, flash)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, logout_user,
                             login_required)

import forms
import models

from peewee import *

DEBUG = True

app = Flask(__name__)
app.secret_key = 'sdo^3n*@49HD370hdfu!@U*4gjp;5(#(*'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash("Your username or password doesn't match!")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Hello {}!".format(user.username))
                return redirect(url_for('index'))
            else:
                flash("Your username or password doesn't match!")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out. Come back soon!")
    return redirect(url_for('index'))


@app.route('/tags/<tag>')
def tag(tag):
    """Shows a list of entries with a specific tag."""
    tag = models.Tag.get(models.Tag.name == tag)
    stream = tag.get_entries().limit(100)
    if stream:
        return render_template('index.html', stream=stream)
    else:
        abort(404)


@app.route('/')
@app.route('/entries')
def index():
    """Shows a list of recent entries."""
    stream = models.Entry.select().limit(100)

    for tag in models.Tag.select():
        print(tag)
    for tag in models.EntryTag.select():
        print(tag)
    return render_template('index.html', stream=stream)


@app.route('/entry', methods=('GET', 'POST'))
@login_required
def new():
    """Creates a new entry."""
    form = forms.EntryForm()
    if request.method == 'GET':
        # Fill form field with today's date.
        form.created_at.data = datetime.datetime.now()
    elif request.method == 'POST':
        form = forms.EntryForm()
        if form.validate_on_submit():
            # Create a new entry.
            entry = models.Entry.create(
                title=form.title.data.strip(),
                learned=form.learned.data.strip(),
                to_remember=form.to_remember.data.strip(),
                time_spent=form.time_spent.data.strip(),
                created_at=form.created_at.data
            )

            # For each input tag
            for tag_name in form.tags.data:
                # Check that tag with that name exists.
                try:
                    tag = models.Tag.get(models.Tag.name == tag_name)
                # If not, create the tag.
                except models.Tag.DoesNotExist:
                    tag = models.Tag.create(name=tag_name)
                # Link tag to the entry.
                models.EntryTag.create(tag=tag, entry=entry)

            return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries/<slug>')
@login_required
def detail(slug):
    """Shows entry details."""
    try:
        entry = models.Entry.get(models.Entry.slug == slug)
    except models.DoesNotExist:
        abort(404)
    else:
        return render_template('detail.html', entry=entry)


@app.route('/entries/edit/<slug>', methods=('GET', 'POST'))
@login_required
def edit(slug):
    """Edits an entry."""

    # Check that entry with that slug exists.
    try:
        entry = models.Entry.get(models.Entry.slug == slug)
    except models.DoesNotExist:
        abort(404)
    else:
        old_tags = entry.get_tags()
        old_tag_names = [tag.name for tag in old_tags]
        # print(existing_tag_names)
        if request.method == 'GET':
            # Populate the form with the entry data.
            form = forms.EntryForm(obj=entry)
            form.tags.data = old_tag_names
        if request.method == 'POST':
            form = forms.EntryForm()
            if form.validate_on_submit():

                # Delete the links between current entry and tags.
                query = models.EntryTag.delete().where(
                    models.EntryTag.entry == entry)
                query.execute()

                # Update the entry.
                entry.title = form.title.data.strip()
                entry.learned = form.learned.data.strip()
                entry.to_remember = form.to_remember.data.strip()
                entry.time_spent = form.time_spent.data.strip()
                entry.created_at = form.created_at.data
                entry.save()

                # For each new tag
                for tag_name in form.tags.data:
                    # Check that tag with that name exists.
                    # If not, create the tag.
                    tag, created = models.Tag.get_or_create(name=tag_name)

                    # Link tag to the entry.
                    models.EntryTag.create(tag=tag, entry=entry)

                # For each old tag
                for old_tag in old_tags:
                    # Check that the tag is linked to any entry.
                    try:
                        models.EntryTag.get(
                            models.EntryTag.tag == old_tag)
                    # If this tag is not linked, delete the tag.
                    except models.EntryTag.DoesNotExist:
                        tag = models.Tag.get(
                            models.Tag.name == old_tag.name)
                        tag.delete_instance()

                return redirect(url_for('index'))
        return render_template('edit.html', form=form)


@app.route('/entries/delete/<slug>')
@login_required
def delete(slug):
    """Deletes an entry."""
    try:
        entry = models.Entry.get(models.Entry.slug == slug)
    except models.DoesNotExist:
        abort(404)
    else:
        entry_tags = entry.get_tags()
        # for tag in entry_tags:
        #     print(tag)
        # print(entry_tags.count())

        # Delete the links between tags and current entry.
        # query = models.EntryTag.delete().where(
        #     models.EntryTag.entry == entry)
        # query.execute()

        # For each previously existing tag
        for entry_tag in entry_tags:
            print('deleted entry tag: {}'.format(entry_tag))

            # Check that the tag is linked to any other entry.
            try:
                models.EntryTag.get(
                    (models.EntryTag.tag == entry_tag) & (
                    models.EntryTag.entry != entry)
                )
            # If this tag is not linked, delete the tag.
            except models.EntryTag.DoesNotExist:
                tag = models.Tag.get(
                    models.Tag.name == entry_tag.name)
                tag.delete_instance()
                # entry_tag.deleted = True
                # entry_tag.save()

        # Delete entry and all its links.
        entry.delete_instance(recursive=True)


        return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='tatiana',
            password='password'
        )
    except ValueError:
        pass
    app.run(debug=DEBUG)
