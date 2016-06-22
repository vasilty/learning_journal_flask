import datetime
from flask import (Flask, render_template, url_for, redirect, g, request,
                   abort, flash)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, logout_user,
                             login_required)
from slugify import slugify
import forms
import models

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
    stream = []
    for entry in models.Entry.select():
        if tag in entry.tags:
            stream.append(entry)
    if stream:
        return render_template('tag.html', stream=stream)
    else:
        abort(404)


@app.route('/')
@app.route('/entries')
def index():
    """Shows a home page."""
    stream = models.Entry.select().limit(100)
    return render_template('index.html', stream=stream)


@app.route('/entry', methods=('GET', 'POST'))
@login_required
def new():
    """Creates a new entry."""
    form = forms.EntryForm(entry_id=-1)
    # Autofill form field with the today's date.
    if request.method == 'GET':
        form.date.data = datetime.datetime.now()
    elif request.method == 'POST':
        if form.validate_on_submit():
            models.Entry.create(
                title=form.title.data.strip(),
                learned=form.learned.data.strip(),
                to_remember=form.to_remember.data.strip(),
                time_spent=form.time_spent.data.strip(),
                tags=form.tags.data.strip()
            )
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
    try:
        entry = models.Entry.get(models.Entry.slug == slug)
    except models.DoesNotExist:
        abort(404)
    else:
        form = forms.EntryForm(entry_id=entry.id)
        if request.method == 'GET':
            # Populate the form field with current entry data.
            form.title.data = entry.title
            form.time_spent.data = entry.time_spent
            form.learned.data = entry.learned
            form.to_remember.data = entry.to_remember
            form.date.data = entry.created_at
            form.tags.data = entry.tags
        elif request.method == 'POST':
            if form.validate_on_submit():
                query = models.Entry.update(
                    title=form.title.data.strip(),
                    learned=form.learned.data.strip(),
                    to_remember=form.to_remember.data.strip(),
                    time_spent=form.time_spent.data.strip(),
                    created_at=form.date.data,
                    tags=form.tags.data.strip(),
                    slug=slugify(form.title.data.strip())
                ).where(models.Entry.slug == slug)
                query.execute()
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
        entry.delete_instance()
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
