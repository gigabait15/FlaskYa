import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('NAME')}@{os.getenv('HOST')}/{os.getenv('DB')}"


app = Flask(__name__)

app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['SECRET_KEY']:str = Config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI']:str = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']:bool = False
app.config['SESSION_COOKIE_SECURE']:bool = False

YANDEX_API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"
# https://disk.yandex.ru/d/ZR99TbwXbnvQtQ