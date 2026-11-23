"""Database models for Stacks, defined with Pony ORM.

Docs: https://docs.ponyorm.org/
"""
from datetime import date, datetime

from pony.orm import Database, Optional, Required, Set

db = Database()

LOAN_DAYS = 14


class Member(db.Entity):
    name = Required(str)
    email = Required(str, unique=True)
    joined_at = Required(datetime, default=datetime.now)
    loans = Set("Loan")
    # Pony relationships are two-sided: Book.donor needs this reverse.
    donated_books = Set("Book")

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
    donor = Optional(Member)
    loans = Set("Loan")

    def is_available(self):
        # Asks the database a yes/no question; does not load the loan history.
        return not Loan.exists(book=self, returned_at=None)

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "donor_id": self.donor.id if self.donor else None,
        }


class Loan(db.Entity):
    book = Required(Book)
    member = Required(Member)
    borrowed_at = Required(datetime, default=datetime.now)
    due_date = Required(date)
    returned_at = Optional(datetime)  # NULL while the book is still out

    def to_json(self):
        return {
            "id": self.id,
            "book_id": self.book.id,
            "member_id": self.member.id,
            "borrowed_at": self.borrowed_at.isoformat(),
            # isoformat() on purpose: jsonify would render a raw date as
            # "Tue, 24 Nov 2026 00:00:00 GMT".
            "due_date": self.due_date.isoformat(),
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
        }


def init_db(filename):
    """Bind the database to a SQLite file and create any missing tables.

    Note: this creates tables that do not exist yet. It does NOT alter
    tables that already exist.
    """
    db.bind(provider="sqlite", filename=filename, create_db=True)
    db.generate_mapping(create_tables=True)
