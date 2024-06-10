import connexion
import pathlib
import sqlalchemy

from flask_marshmallow import Marshmallow

basedir = pathlib.Path(__file__).parent.resolve()
connex_app = connexion.App(__name__, specification_dir=basedir)

SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'people.db'}"

app = connex_app.app
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
ma = Marshmallow(app)
