from config import db
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Due to version conflicts, the project will use pure sqlalchemy modules on its
# own, and not the flask_sqlalchemy extension.
Base = declarative_base()
Session = sessionmaker(bind=db.engine)
session = Session()


class Note(Base):
    __tablename__ = "note"
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.id"))
    content = Column(String, nullable=False)
    timestamp = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    lname = Column(String(32), unique=True)
    fname = Column(String(32))
    timestamp = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Define relationship to a Note
    notes = relationship(
        # This could either be a string or a class, but a string is easier as
        # the editor won't throw any errors.
        'Note',
        # Each instance of Note will contain an attribute called .person. This
        # attribute references the parent object that a particular Note instance
        # is related to.
        backref='person',
        # This parameter determines how to treat Note instances when changes are
        # made to the parent Person instance. For example, if a Person objected
        # is deleted, all of its associated Notes will be deleted as well.
        cascade='all, delete, delete-orphan',
        # This is required if 'delete-orphan' is part of the cascade parameter.
        # This tells SQLAlchemy not to allow an orphaned Note instance to exist
        # because each Note has a single parent.
        single_parent=True,
        # This tells SQLAlchemy how to sort the Note instances associated with
        # a Person object. When a Person is retrieved, by default the notes
        # attribute list will be in an unknown order. This ensures the notes
        # get returned in descending order, from newest to oldest.
        order_by='desc(Note.timestamp)'
    )


class PersonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        load_instance = True
        sqla_session = session


person_schema = PersonSchema()
people_schema = PersonSchema(many=True)
