"""Stacks - a small community library.

Run with:  python app.py
"""
import os

from flask import Flask, jsonify, render_template, request
from pony.flask import Pony
from pony.orm import select

from models import Book, Loan, Member, init_db

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


# --------------------------------------------------------------------------
# Loans
# --------------------------------------------------------------------------

@app.get("/api/loans")
def list_loans():
    loans = select(l for l in Loan).order_by(Loan.id)
    return jsonify([l.to_json() for l in loans])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
