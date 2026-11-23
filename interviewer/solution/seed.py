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
    from models import LOAN_DAYS, Book, Loan, Member

    now = datetime.now()
    with db_session:
        priya = Member(name="Priya Nair", email="priya@example.com")
        tomas = Member(name="Tomas Silva", email="tomas@example.com")
        hana = Member(name="Hana Kim", email="hana@example.com")
        ben = Member(name="Ben Adeyemi", email="ben@example.com")
        clara = Member(name="Clara Novak", email="clara@example.com")

        b1 = Book(title="The Left Hand of Darkness", author="Ursula K. Le Guin", year=1969)
        b2 = Book(title="A Wizard of Earthsea", author="Ursula K. Le Guin", year=1968)
        b3 = Book(title="Kindred", author="Octavia E. Butler", year=1979)
        b4 = Book(title="The Remains of the Day", author="Kazuo Ishiguro", year=1989)
        b5 = Book(title="Braiding Sweetgrass", author="Robin Wall Kimmerer", year=2013,
                  donor=clara)
        Book(title="Invisible Cities", author="Italo Calvino", year=1972)
        Book(title="Allotment Notes (local zine)", author="Various", donor=priya)

        def loan(book, member, days_ago, returned_days_ago=None):
            borrowed = now - timedelta(days=days_ago)
            returned = None
            if returned_days_ago is not None:
                returned = now - timedelta(days=returned_days_ago)
            Loan(book=book, member=member, borrowed_at=borrowed,
                 due_date=borrowed.date() + timedelta(days=LOAN_DAYS),
                 returned_at=returned)

        loan(b1, priya, 40, returned_days_ago=30)  # returned on time
        loan(b3, hana, 35)                         # still out, 21 days overdue
        loan(b1, tomas, 20)                        # still out, 6 days overdue
        loan(b4, hana, 12, returned_days_ago=5)    # returned on time
        loan(b5, ben, 6)                           # out, not due yet
        loan(b2, hana, 2)                          # out, not due yet

if __name__ == "__main__":
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    from models import init_db

    init_db(DB_FILE)
    seed()
    print("Seeded " + DB_FILE)
