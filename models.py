from config import db
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# Due to version conflicts, the project will use pure sqlalchemy modules on its
# own, and not the flask_sqlalchemy extension.
Base = declarative_base()
Session = sessionmaker(bind=db.engine)
session = Session()


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    lname = Column(String(32), unique=True)
    fname = Column(String(32))
    timestamp = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PersonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        load_instance = True
        sqla_session = session


person_schema = PersonSchema()
people_schema = PersonSchema(many=True)
