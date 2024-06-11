# notes.py

from flask import abort, make_response

from config import db
from models import Note, note_schema, session


def read_one(note_id):
    # NOTE: .get() is specifically designed for use with primary keys, as
    #   opposed to session.query().filter_by() which is more general purpose.
    #   It still returns None if no object is found.
    note = session.get(Note, note_id)

    if note is not None:
        return note_schema.dump(note)
    else:
        abort(
            404, f"Note with ID {note_id} not found"
        )


def update(note_id, note):
    existing_note = session.get(Note, note_id)

    if existing_note:
        update_note = note_schema.load(note, session=session)
        existing_note.content = update_note.content
        session.merge(existing_note)
        session.commit()
        return note_schema.dump(existing_note), 201
    else:
        abort(404, f"Note with ID {note_id} not found")


def delete(note_id):
    existing_note = session.get(Note, note_id)

    if existing_note:
        session.delete(existing_note)
        session.commit()
        return make_response(f"{note_id} successfully deleted", 204)
    else:
        abort(404, f"Note with ID {note_id} not found")
