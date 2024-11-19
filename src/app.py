import os
import requests
from flask import redirect, url_for, flash, render_template, request, send_file
from flask_login import current_user, login_user, login_required, logout_user
from src.config import app, db, login_manager, YANDEX_API_URL
from src.forms import RegistrationForm, LoginForm
from src.models import User
import sqlalchemy as sa
from urllib.parse import urlparse, urljoin

login_manager.login_view = 'pub_link'


@login_manager.user_loader
def load_user(user_id: int) -> User:
    """
    Загружает пользователя по его идентификатору.

    :param user_id: Идентификатор пользователя в базе данных.
    :return: Объект пользователя, если найден, иначе None.
    """
    return db.session.query(User).get(int(user_id))


def is_safe_url(target: str) -> bool:
    """
    Проверяет, что URL безопасен для редиректа.

    :param target: URL, который требуется проверить.
    :return: True, если URL безопасен, иначе False.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/register', methods=['GET', 'POST'])
def register() -> str:
    """
    Обрабатывает регистрацию нового пользователя.

    :return: Шаблон страницы регистрации или редирект на страницу входа.
    """
    if current_user.is_authenticated:
        return redirect(url_for('pub_link'))

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
def login() -> str:
    """
    Обрабатывает процесс входа пользователя.

    :return: Шаблон страницы входа или редирект на страницу после успешного входа.
    """
    if current_user.is_authenticated:
        return redirect(url_for('pub_link'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль', 'error')
            return redirect(url_for('login'))

        login_user(user)
        next_page = request.args.get('next')
        if not next_page or not is_safe_url(next_page):
            next_page = url_for('pub_link')
        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout() -> str:
    """
    Обрабатывает выход пользователя.

    :return: Редирект на страницу входа после выхода.
    """
    logout_user()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def pub_link() -> str:
    """
    Главная страница, где пользователь может ввести публичный ключ.

    :return: Шаблон главной страницы с формой ввода публичного ключа.
    """
    if request.method == 'POST':
        public_key = request.form.get('public_key')
        if not public_key:
            flash("Пожалуйста, введите публичную ссылку", "error")
            return redirect(url_for('pub_link'))
        return redirect(url_for('view_files', public_key=public_key))
    return render_template('index.html')


@app.route('/view_files')
@login_required
def view_files() -> str:
    """
    Отображает файлы на основе публичного ключа.

    :return: Шаблон с файлами, если данные успешно получены, иначе редирект на главную страницу.
    """
    public_key = request.args.get('public_key')
    if not public_key:
        flash("Публичная ссылка отсутствует!", "error")
        return redirect(url_for('pub_link'))

    response = requests.get(YANDEX_API_URL, params={"public_key": public_key})
    if response.status_code == 200:
        data = response.json()
        files = data.get('_embedded', {}).get('items', [])
        return render_template('view_files.html', files=files, public_key=public_key)
    else:
        flash("Не удалось получить данные с Яндекс.Диска", "error")
        return redirect(url_for('index'))


@app.route('/download_file')
@login_required
def download_file() -> str:
    """
    Загружает файл по URL и возвращает его пользователю.

    :return: Файл для скачивания или редирект на главную страницу с сообщением об ошибке.
    """
    file_url = request.args.get('file_url')
    file_name = request.args.get('file_name')
    if not file_url or not file_name:
        flash("Ошибка при загрузке файла", "error")
        return redirect(url_for('pub_link'))

    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        local_path = os.path.join('downloads', file_name)
        os.makedirs('downloads', exist_ok=True)
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return send_file(local_path, as_attachment=True)
    else:
        flash("Не удалось загрузить файл", "error")
        return redirect(url_for('pub_link'))


if __name__ == '__main__':
    app.run(debug=False)
