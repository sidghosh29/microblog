from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, session, g, \
current_app
from flask_login import current_user, login_required

import sqlalchemy as sa
from app import db
from app.models import User, Post
from urllib.parse import urlsplit

from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm

from flask_babel import _, get_locale
from langdetect import detect, LangDetectException
from app.translate import translate

from app.main import bp

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()
    
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
        # Post/Redirect/Get pattern (https://en.wikipedia.org/wiki/Post/Redirect/Get) avoids inserting duplicate posts 
        # when a user inadvertently refreshes the page after submitting a web form.

        '''
        It is a standard practice to always respond to a POST request generated by a web form submission with a redirect. 
        This helps mitigate an annoyance with how the refresh command is implemented in web browsers. 
        When you hit the refresh key, the web browser just re-issues the last request. 
        If the last request is a POST request with a form submission, then a refresh will re-submit the form. 
        Because this is unexpected, the browser is going to ask the user to confirm the duplicate submission, 
        but most users will not understand what the browser is asking them. If a POST request is answered with a redirect, 
        the browser is instructed to send a GET request to grab the page indicated in the redirect, so now the last request 
        is not a POST request anymore, and the refresh command works in a more predictable way.
        '''
    page = request.args.get('page', 1, type=int)
    pagination_obj = db.paginate(current_user.following_posts(), page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination_obj.items
    
    next_url = url_for('main.index', page=pagination_obj.next_num) \
        if pagination_obj.has_next else None
    prev_url = url_for('main.index', page=pagination_obj.prev_num) \
        if pagination_obj.has_prev else None
    
    return render_template('index.html', title='Home', posts = posts, form = form, next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    pagination_obj = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=pagination_obj.next_num) \
        if pagination_obj.has_next else None
    prev_url = url_for('main.explore', page=pagination_obj.prev_num) \
        if pagination_obj.has_prev else None
    posts = pagination_obj.items
    return render_template("index.html", title='Explore', posts=posts, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    # In the case that there are no results, the db.first_or_404 method automatically sends a 404 error back to the client.
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    pagination_obj = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    posts = pagination_obj.items
    next_url = url_for('main.user', username=user.username, page=pagination_obj.next_num) \
        if pagination_obj.has_next else None
    prev_url = url_for('main.user', username=user.username, page=pagination_obj.prev_num) \
        if pagination_obj.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))
    


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    data = request.get_json()
    return {'text': translate(data['text'],
                              data['source_language'],
                              data['dest_language'])}


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)

