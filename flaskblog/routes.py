import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, PortfolioForm
from .modelsWithNeo4j import User, Post, Portfolio
from flask_login import login_user, current_user, logout_user, login_required
from .db_utils import execute_query

@app.route("/blog")
def blog():
    posts = Post.query_all()
    return render_template('blog.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/database")
@login_required
def database():
    if current_user.is_authenticated:
        allPortfolios = Portfolio.query_all()
        return render_template('database.html', title='Database', results=allPortfolios)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        User.add_user(username=form.username.data, email=form.email.data, password=hashed_password)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User().get(email=form.email.data)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.update_user()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/portfolio/edit/<int:portfolio_id>", methods=['GET','POST'])
@login_required
def edit_portfolio(portfolio_id):
    portfolio = Portfolio().get_or_404(portfolio_id)
    return render_template('edit_portfolio.html', title=portfolio.name, portfolio = portfolio)


@app.route("/portfolio/new", methods=['GET', 'POST'])
@login_required
def new_portfolio():
    form = PortfolioForm()
    if form.validate_on_submit():
        Portfolio.add_portfolio(name=form.name.data, user=current_user)
        flash('Your empty portfolio has been created!', 'success')
        return redirect(url_for('database'))
    return render_template('create_portfolio.html', title='New Portfolio',
                           form=form, legend='New Portfolio')

@app.route("/post/delete/<int:portfolio_id>", methods=['POST'])
@login_required
def delete_portfolio(portfolio_id):
    portfolio = Portfolio().get_or_404(portfolio_id)
    Portfolio.delete_portfolio(portfolio)
    flash('Your portfolio has been deleted!', 'success')
    return redirect(url_for('database'))

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        Post.add_post(title=form.title.data, content=form.content.data, author=current_user)
        flash('Your post has been created!', 'success')
        return redirect(url_for('blog'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post().get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post().get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.update_post()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post().get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    Post.delete_post(post)
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))
