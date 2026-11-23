"""Database models for Stacks, defined with Pony ORM.

Docs: https://docs.ponyorm.org/
"""
from datetime import datetime

from pony.orm import Database, Optional, Required, Set

db = Database()


class Member(db.Entity):
    name = Required(str)
    email = Required(str, unique=True)
    joined_at = Required(datetime, default=datetime.now)
    loans = Set("Loan")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "joined_at": self.joined_at.isoformat(),
        }


class Book(db.Entity):
    title = Required(str)
    author = Required(str)
    year = Optional(int)
    loans = Set("Loan")

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
        }


class Loan(db.Entity):
    book = Required(Book)
    member = Required(Member)
    borrowed_at = Required(datetime, default=datetime.now)

    def to_json(self):
        return {
            "id": self.id,
            "book_id": self.book.id,
            "member_id": self.member.id,
            "borrowed_at": self.borrowed_at.isoformat(),
        }


def init_db(filename):
    """Bind the database to a SQLite file and create any missing tables.

    Note: this creates tables that do not exist yet. It does NOT alter
    tables that already exist.
    """
    db.bind(provider="sqlite", filename=filename, create_db=True)
    db.generate_mapping(create_tables=True)
