from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src.config import db


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password) -> None:
        """
        функция для хеширования пароля
        :param password: принимает пароль
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        """
        функия для проверки пароля. берет пароль из бд и пароль из шаблона и сравнивает хеш,
        возраващет booltype
        :param password:пароль из шаблона
        :return:booltype
        """
        return check_password_hash(self.password_hash, password)
