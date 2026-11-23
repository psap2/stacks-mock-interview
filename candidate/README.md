# Stacks — Web App Challenge

Stacks runs a small community library. **Members** borrow **books**; every
borrowing is recorded as a **loan**. The library owns exactly one copy of each
book. It is a Flask app backed by SQLite through
[Pony ORM](https://docs.ponyorm.org/).

You have **60 minutes**. Work through the tasks in order. Working, runnable
code matters more than finishing everything — a task only counts if the app
still starts and the endpoint actually responds.

You may search online, read documentation, and ask the interviewer questions
at any time. Please think out loud.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python seed.py      # (re)creates stacks.sqlite with sample data
python app.py       # http://localhost:5000
pytest              # existing tests
```

Try it:

```bash
curl localhost:5000/api/books
curl localhost:5000/api/members/3/loans
curl -X POST localhost:5000/api/members \
     -H 'Content-Type: application/json' \
     -d '{"name": "Ada", "email": "ada@example.com"}'
```

## Layout

| File | What it is |
| --- | --- |
| `app.py` | Flask app and all routes |
| `models.py` | Pony ORM entities: `Member`, `Book`, `Loan` |
| `seed.py` | Deletes and rebuilds the database with sample data |
| `templates/index.html` | The book list page at `/` |
| `tests/` | Tests for the existing behaviour |

## Existing API

| Method | Path | |
| --- | --- | --- |
| GET | `/api/members` | List members |
| GET | `/api/members/<id>` | One member |
| POST | `/api/members` | Create a member |
| GET | `/api/members/<id>/loans` | A member's loans |
| GET | `/api/books` | List books. Optional `?author=<exact name>` |
| GET | `/api/loans` | List all loans |

Errors are returned as `{"error": "<message>"}` with a suitable status code.

## Cheat sheet

We are not testing whether you have Pony or `datetime` memorised. Everything
the tasks need is below or already used somewhere in `app.py` / `seed.py`.

```python
# Look up one row (None when there is no match)
Member.get(email="ada@example.com")

# Yes/no question, answered by the database. None matches an empty column.
Book.exists(author="Various", year=None)

# Filter and sort in the database
select(b for b in Book if b.year is None or b.year < 1970).order_by(Book.year)

# Dates
date.today() + timedelta(days=14)        # a date two weeks from now
(date.today() - some_date).days          # whole days between two dates
```

---

## Tasks

### Task 1 — Extend the models

Right now a loan only records who borrowed what and when. The librarians need
to know when a book is due back and whether it has come back. Add:

On `Loan`:

- **`due_date`** — the day the book is due back. A calendar date, not a
  timestamp. Every loan has one.
- **`returned_at`** — the moment the book was handed back. Empty while the
  book is still out.

On `Book`:

- **`donor`** — the member who donated the book to the library. Most books
  were bought, so a book may have no donor.

Then:

- Include `due_date` (as `"YYYY-MM-DD"`) and `returned_at` (ISO timestamp, or
  `null` while the book is out) in the loan JSON everywhere a loan is returned.
- Include `donor_id` (`null` when there is none) in the book JSON everywhere a
  book is returned.
- Update `seed.py` so the sample data is realistic: loans are due 14 days
  after they were borrowed, some have been returned, some are still out, at
  least one is overdue, and a couple of books have a donor. No book should be
  out with two members at once.

### Task 2 — `GET /api/books/<id>`

Return a single book: the usual book JSON plus

- `available` — `true` when nobody currently has the book, and
- `loans` — the book's full loan history, oldest first.

```json
{
  "id": 1,
  "title": "The Left Hand of Darkness",
  "author": "Ursula K. Le Guin",
  "year": 1969,
  "donor_id": null,
  "available": false,
  "loans": [
    {"id": 1, "book_id": 1, "member_id": 1, "borrowed_at": "2026-01-02T10:15:00", "due_date": "2026-01-16", "returned_at": "2026-01-12T16:40:00"},
    {"id": 3, "book_id": 1, "member_id": 2, "borrowed_at": "2026-01-22T09:05:00", "due_date": "2026-02-05", "returned_at": null}
  ]
}
```

Unknown id → `404`.

### Task 3 — `POST /api/loans`

A member borrows a book. JSON body:

```json
{"book_id": 6, "member_id": 5}
```

- The loan is due 14 days from today. The server sets this, not the client.
- A book that is currently out cannot be borrowed again until it is returned.
- On success return `201` and the new loan's JSON (including its `id`).
- A request that should not succeed must **not** create a loan and must return
  a `4xx` with an error message. Which requests those are, and which status
  code each one gets, is your call — be ready to explain your choices.

### Task 4 — `GET /api/overdue`

The list the librarians chase up every morning: every loan that has not been
returned and whose due date has passed, **most overdue first**. Each item is
the usual loan JSON plus `days_overdue`.

```json
[
  {"id": 2, "book_id": 3, "member_id": 3, "borrowed_at": "...", "due_date": "2026-01-10", "returned_at": null, "days_overdue": 21},
  {"id": 3, "book_id": 1, "member_id": 2, "borrowed_at": "...", "due_date": "2026-01-25", "returned_at": null, "days_overdue": 6}
]
```

A loan that is due today is not overdue yet. A loan that was returned late is
not on the list. Nothing overdue → `[]`.

### If you have time

Pick whichever you like:

- `POST /api/loans/<id>/return` — mark a loan as returned.
- Show the donor and whether each book is available on the page at `/`.
- Tests for what you built.

Toward the end we will also talk about how you would evolve this app:
performance with far more books and loans, changing the schema of a live
database, and anything else you would improve.
