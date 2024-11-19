from flask import redirect, url_for, flash, render_template
from flask_login import current_user, login_user, login_required, logout_user
from src.config import app, db, login_manager
from src.forms import RegistrationForm, LoginForm
from src.models import User
import sqlalchemy as sa

login_manager.login_view = 'index'

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))
@app.route('/index')
@app.route('/')
def index():
    return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        print(user)
        if user is None or not user.check_password(form.password.data):
            flash('неверный логин или пароль')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'), code=302)

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
