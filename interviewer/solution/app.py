"""Stacks - a small community library.

Run with:  python app.py
"""
import os
from datetime import date, datetime, timedelta

from flask import Flask, jsonify, render_template, request
from pony.flask import Pony
from pony.orm import select

from models import LOAN_DAYS, Book, Loan, Member, init_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.environ.get("STACKS_DB", os.path.join(BASE_DIR, "stacks.sqlite"))

app = Flask(__name__)
init_db(DB_FILE)
Pony(app)  # wraps every request in a pony db_session


def error(message, status):
    return jsonify({"error": message}), status


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

@app.get("/")
def index():
    books = select(b for b in Book).order_by(Book.id)[:]
    return render_template("index.html", books=books)


# --------------------------------------------------------------------------
# Members
# --------------------------------------------------------------------------

@app.get("/api/members")
def list_members():
    members = select(m for m in Member).order_by(Member.id)
    return jsonify([m.to_json() for m in members])


@app.get("/api/members/<int:member_id>")
def get_member(member_id):
    member = Member.get(id=member_id)
    if member is None:
        return error("member not found", 404)
    return jsonify(member.to_json())


@app.post("/api/members")
def create_member():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("request body must be a JSON object", 400)

    name = data.get("name")
    email = data.get("email")

    if not isinstance(name, str) or not name.strip():
        return error("name is required", 400)
    if not isinstance(email, str) or "@" not in email:
        return error("a valid email is required", 400)
    if Member.get(email=email) is not None:
        return error("email is already in use", 409)

    member = Member(name=name.strip(), email=email)
    member.flush()  # assigns member.id
    return jsonify(member.to_json()), 201


@app.get("/api/members/<int:member_id>/loans")
def list_member_loans(member_id):
    member = Member.get(id=member_id)
    if member is None:
        return error("member not found", 404)
    loans = select(l for l in Loan if l.member == member).order_by(Loan.id)
    return jsonify([l.to_json() for l in loans])


# --------------------------------------------------------------------------
# Books
# --------------------------------------------------------------------------

@app.get("/api/books")
def list_books():
    author = request.args.get("author")
    if author:
        books = select(b for b in Book if b.author == author).order_by(Book.id)
    else:
        books = select(b for b in Book).order_by(Book.id)
    return jsonify([b.to_json() for b in books])


# Task 2
@app.get("/api/books/<int:book_id>")
def get_book(book_id):
    book = Book.get(id=book_id)
    if book is None:
        return error("book not found", 404)
    data = book.to_json()
    data["available"] = book.is_available()
    loans = select(l for l in Loan if l.book == book).order_by(Loan.borrowed_at, Loan.id)
    data["loans"] = [l.to_json() for l in loans]
    return jsonify(data)


# --------------------------------------------------------------------------
# Loans
# --------------------------------------------------------------------------

@app.get("/api/loans")
def list_loans():
    loans = select(l for l in Loan).order_by(Loan.id)
    return jsonify([l.to_json() for l in loans])


# Task 3
@app.post("/api/loans")
def create_loan():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("request body must be a JSON object", 400)

    book_id = data.get("book_id")
    member_id = data.get("member_id")

    if not isinstance(book_id, int):
        return error("book_id is required and must be an integer", 400)
    if not isinstance(member_id, int):
        return error("member_id is required and must be an integer", 400)

    book = Book.get(id=book_id)
    if book is None:
        return error("book not found", 404)
    member = Member.get(id=member_id)
    if member is None:
        return error("member not found", 404)
    if not book.is_available():
        return error("book is already on loan", 409)

    # The server decides borrowed_at, due_date and returned_at; anything the
    # client sends for them is ignored.
    loan = Loan(book=book, member=member,
                due_date=date.today() + timedelta(days=LOAN_DAYS))
    loan.flush()  # assigns loan.id
    return jsonify(loan.to_json()), 201


# Task 4
@app.get("/api/overdue")
def list_overdue():
    today = date.today()
    # Filtering and ordering happen in SQL, not in Python.
    loans = select(
        l for l in Loan if l.returned_at is None and l.due_date < today
    ).order_by(Loan.due_date, Loan.id)

    result = []
    for l in loans:
        item = l.to_json()
        item["days_overdue"] = (today - l.due_date).days
        result.append(item)
    return jsonify(result)


# Stretch
@app.post("/api/loans/<int:loan_id>/return")
def return_loan(loan_id):
    loan = Loan.get(id=loan_id)
    if loan is None:
        return error("loan not found", 404)
    if loan.returned_at is not None:
        return error("loan was already returned", 409)
    loan.returned_at = datetime.now()
    return jsonify(loan.to_json())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
