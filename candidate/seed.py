"""Reset the database and load sample data.

Usage:  python seed.py

This DELETES the existing database file and rebuilds it from the current
models, so it is also how you pick up a change to models.py.
"""
import os
from datetime import datetime, timedelta

from pony.orm import db_session

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.environ.get("STACKS_DB", os.path.join(BASE_DIR, "stacks.sqlite"))


def seed():
    from models import Book, Loan, Member

    now = datetime.now()
    with db_session:
        priya = Member(name="Priya Nair", email="priya@example.com")
        tomas = Member(name="Tomas Silva", email="tomas@example.com")
        hana = Member(name="Hana Kim", email="hana@example.com")
        ben = Member(name="Ben Adeyemi", email="ben@example.com")
        Member(name="Clara Novak", email="clara@example.com")

        b1 = Book(title="The Left Hand of Darkness", author="Ursula K. Le Guin", year=1969)
        b2 = Book(title="A Wizard of Earthsea", author="Ursula K. Le Guin", year=1968)
        b3 = Book(title="Kindred", author="Octavia E. Butler", year=1979)
        b4 = Book(title="The Remains of the Day", author="Kazuo Ishiguro", year=1989)
        b5 = Book(title="Braiding Sweetgrass", author="Robin Wall Kimmerer", year=2013)
        Book(title="Invisible Cities", author="Italo Calvino", year=1972)
        Book(title="Allotment Notes (local zine)", author="Various")

        Loan(book=b1, member=priya, borrowed_at=now - timedelta(days=40))
        Loan(book=b3, member=hana, borrowed_at=now - timedelta(days=35))
        Loan(book=b1, member=tomas, borrowed_at=now - timedelta(days=20))
        Loan(book=b4, member=hana, borrowed_at=now - timedelta(days=12))
        Loan(book=b5, member=ben, borrowed_at=now - timedelta(days=6))
        Loan(book=b2, member=hana, borrowed_at=now - timedelta(days=2))


if __name__ == "__main__":
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    from models import init_db

    init_db(DB_FILE)
    seed()
    print("Seeded " + DB_FILE)
