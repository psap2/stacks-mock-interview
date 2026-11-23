# Interviewer guide — Stacks mock

**Do not share this folder.** Give your friend only `candidate/`.

This is mock #2. Same stack as Deskly (Flask + Pony ORM + SQLite) and the same
shape (extend the model → GET → POST → GET), but a different domain and
different traps, so it tests whether the lessons from last time transferred
rather than whether the answers were memorised.

## What this mock is (and is not) testing

It tests API design and judgement: what a route should accept, what it should
refuse, which status code says so, which fields the server owns, and whether
the candidate keeps the app running while they work.

It does **not** test recall of Pony or Python syntax. The starter has no
lambdas, the candidate README has a cheat sheet with every query and date
expression the tasks need, and nothing requires parsing a date. If they are
stuck on *how to spell* something for more than a minute, just tell them and
don't mark it down. Save the hints-with-a-cost for the design decisions and
the debugging traps.

## Before the session

1. Zip and send `candidate/` (without `venv/`) 5 minutes before, or share it
   live. Don't send it the night before.
2. Have them share their screen. Ask them to think out loud.
3. Keep `interviewer/solution/` open on your side for reference.

## Timeline (60 min)

| Time | What |
| --- | --- |
| 0–5 | Setup, they read the README and explore the code |
| 5–22 | Task 1 — three model fields + seed |
| 22–30 | Task 2 — `GET /api/books/<id>` |
| 30–40 | Task 3 — `POST /api/loans` |
| 40–48 | Task 4 — `GET /api/overdue` |
| 48–60 | Discussion questions (below) |

Task 1 is heavier than last time (three fields over two models, and the seed
*must* change for the app to work), so it gets a bigger slice. If they are
behind at minute 40, tell them to skip to whichever of Task 3 / 4 they prefer.
Always leave 10 minutes for discussion — that is where most of the design
signal comes from.

## The single most important thing: does it run?

Same as last time — the real feedback was "endpoints were correct but the code
couldn't run". Every 10 minutes or so, if they have not run anything, ask:
**"Can you show me that working?"**

Compare with mock #1. Things that should be visibly better this time:

- Runs `python seed.py` / `python app.py` / `curl` *before* changing anything.
- Adds **one field at a time** and runs after each, instead of adding all
  three and facing three errors at once.
- Re-seeds after a model change without being told (they hit this last time).
- Reads the traceback from the bottom up.

## The traps built into Task 1

Four distinct breakages, roughly in the order they will hit them. All are real
Pony/Flask behaviour. Let them struggle ~3 minutes on each, then hint.

**Trap A — relationship with no reverse.** Adding `donor = Optional(Member)`
to `Book` stops the app from starting:

```
pony.orm.core.ERDiagramError: Reverse attribute for Book.donor not found
```

Last time the error was *ambiguous* reverse and the fix was `reverse=`. This
time there is no candidate at all: `Member` needs a new attribute.

```python
# Member
donated_books = Set("Book")
# Book
donor = Optional(Member)
```

(`reverse=` is not needed here because there is only one Member↔Book link.
Adding it anyway is fine.)

- Hint 1: "What is the error message telling you is missing?"
- Hint 2: "Pony relationships are two-sided. What does `Loan.member` have on
  the `Member` side that `Book.donor` doesn't?"

**Trap B — a required field breaks the seed.** `due_date = Required(date)`
has no default, and the README says "every loan has one". Now `python seed.py`
— the thing they rely on to rebuild the database — fails:

```
ValueError: Attribute Loan.due_date is required
```

and so do all the existing tests (they seed too). The app is not runnable
again until `seed.py` is updated. Watch what they do:

- Good: update the seed (borrowed date + 14 days), re-run, move on.
- Acceptable with discussion: a callable default
  (`default=lambda: date.today() + timedelta(days=14)`).
- Bad: `default=date.today() + timedelta(days=14)` — evaluated **once at
  import**, so a server that has been up for a week hands out stale due dates.
  If they do this, ask "when is that expression evaluated?"
- Bad: quietly making it `Optional` to make the error go away. Ask whether a
  loan with no due date makes sense, and what `/api/overdue` does with it.

Also the usual `NameError: name 'date' is not defined` — the starter only
imports `datetime`.

**Trap C — stale database** (repeat from last time; they should be fast).
If they start the app before re-seeding:

```
pony.orm.dbapiprovider.OperationalError: no such column: Book.donor
```

`create_tables=True` never alters an existing table. Fix: `python seed.py`.
If this costs them more than a minute, note it — it was the headline lesson
of mock #1.

**Trap D — the date that doesn't crash.** This one is silent. If `to_json`
returns the raw `date` object, Flask happily serialises it as

```
"due_date": "Tue, 24 Nov 2026 00:00:00 GMT"
```

The README asks for `"YYYY-MM-DD"`. The fix is `self.due_date.isoformat()` —
exactly what the existing code already does for `borrowed_at`. A candidate
who curls their endpoint and *reads the output* catches it; one who only
checks for a 200 does not. Don't hint unless they move on to Task 2 without
noticing; then: "Compare your output with the example in the README."

And the `None` case: `self.returned_at.isoformat()` blows up with
`AttributeError: 'NoneType' object has no attribute 'isoformat'` for loans
that are still out (same shape of bug as `assignee.id` last time). Same for
`self.donor.id`.

## What good looks like, per task

**Task 1.** `due_date = Required(date)`, `returned_at = Optional(datetime)`,
`donor = Optional(Member)` + the reverse `Set` on `Member`. All three in
`to_json` with the `None` cases handled. Seed updated so that it runs, has
returned / out / overdue loans, and no book is out twice. Existing tests pass
again.

**Task 2.** Mirrors `get_member` / `list_member_loans` rather than inventing
a new style; 404 through the `error()` helper; loans ordered. For `available`
the cheat sheet gives them the one-liner:

```python
available = not Loan.exists(book=book, returned_at=None)
```

Any correct version passes, including a plain Python loop over `book.loans`.
If they wrote the loop, don't mark it down — ask "what does this do for a
book that has been borrowed 5,000 times?" and score the answer. Bonus if they
put the check in a helper/method, because Task 3 needs it again.

**Task 3.** Short on purpose: no optional fields, no parsing. The code is
about fifteen lines copied from the shape of `create_member`; the signal is
in the decisions. Must-haves:

- Bad or non-object JSON → 4xx, not 500 (`create_member` shows how).
- Missing / wrong-type `book_id` or `member_id` → 400.
- Unknown book or member → 4xx, not 500.
- Book already out → refused, no loan created. Reuses the Task 2 check.
- `due_date` is today + 14, worked out per request on the server.
- 201 with the new loan including its `id` (`flush()`, as in `create_member`).

Then ask them to defend the choices. There is more than one right answer;
you want a reason, not a specific code:

- **"Which status did you use for an unknown `book_id`, and why?"** 404, 400
  and 422 are all defensible. "The URL exists, the thing the body points at
  doesn't" is the tension to hear.
- **"And for a book that's already out?"** Ideally 409: the request is
  well-formed, it conflicts with current state. 400 with a clear message is
  acceptable if they can say why.
- **"What if I send `returned_at` or `borrowed_at` in the body?"** Want: the
  server owns those; ignore or reject, never store.
- **"What should the error body tell the client?"** Want: which field, what
  was wrong — enough for a front end to show something useful.

**Task 4.** Good:

```python
today = date.today()
select(l for l in Loan if l.returned_at is None and l.due_date < today) \
    .order_by(Loan.due_date)
```

then `days_overdue = (today - l.due_date).days` while building the JSON. Both
expressions are in the cheat sheet in a different shape, so this is about
adapting an example, not remembering one.

If they load every loan and filter/sort in Python, it still passes; ask how
it behaves after ten years of loans. Check the edges, which are the real
content of the task: due today is **not** overdue (`<`, not `<=`);
returned-late loans are excluded; empty list rather than an error.

## Checking their work

From the repo root, after the session (or during, on your own machine if you
have their code):

```bash
candidate/venv/bin/pytest interviewer/test_tasks.py -v                        # their code
APP_DIR=interviewer/solution candidate/venv/bin/pytest interviewer/test_tasks.py -v   # reference: 26 pass
```

Against their code the stretch test is skipped unless they built the return
route. Every test errors until Task 1 is done, because the test data uses the
new fields.

If you only have a screen share, use these curls (after `python seed.py`).
Ids assume they kept the seed's members and books in the original order.

```bash
curl -i localhost:5000/api/loans                              # due_date "YYYY-MM-DD", returned_at null or timestamp
curl -i localhost:5000/api/books/1                            # available + loans
curl -i localhost:5000/api/books/999                          # 404
curl -i -X POST localhost:5000/api/loans -H 'Content-Type: application/json' \
     -d '{"book_id":6,"member_id":5}'                         # 201, due in 14 days
curl -i -X POST localhost:5000/api/loans -H 'Content-Type: application/json' \
     -d '{"book_id":6,"member_id":4}'                         # 4xx (409): already out
curl -i -X POST localhost:5000/api/loans -H 'Content-Type: application/json' \
     -d '{"book_id":7}'                                       # 400
curl -i -X POST localhost:5000/api/loans -H 'Content-Type: application/json' \
     -d '{"book_id":7,"member_id":999}'                       # 4xx, not 500
curl -i -X POST localhost:5000/api/loans -d 'hello'           # 400, not 500
curl -i localhost:5000/api/overdue                            # most overdue first
```

## Discussion questions (last 5–10 min)

Pick two or three. You want reasoning, not buzzwords.

1. **"Two members tap 'borrow' on the same book at the same instant. What
   happens?"** Want: the check-then-insert in Task 3 is a race; both can pass
   the availability check. Fixes: a database constraint (partial unique index
   on `book` where `returned_at IS NULL`), or a transaction with a row lock /
   serialisable isolation, and turning the constraint violation into a 409.
2. **"You added `due_date` as a required column by deleting the database.
   The live system has 200,000 loans. How do you ship it?"** Want: a
   migration; you cannot add a NOT NULL column with no default to a populated
   table — add it nullable, backfill (`borrowed_at + 14 days`), then tighten;
   deploy order of code vs schema; rollback.
3. **"The library has been open ten years. What gets slow first?"** Want:
   `/api/books` and `/api/loans` return everything → pagination;
   `/api/overdue` → index on `(returned_at, due_date)`; the `/` page runs
   `b.loans.count()` per row → N+1; `available` per book in a list would be
   another N+1.
4. **"What does 'today' mean?"** Want: `date.today()` is the server's local
   date; a library in another time zone, or a server in UTC, disagrees about
   when a loan becomes overdue. Store timestamps in UTC, decide the business
   time zone explicitly.
5. **"The library buys a second copy of a popular book. What changes?"**
   Want: a `copies` count or a separate `Copy` entity; availability becomes
   `copies - active loans`; which they'd choose and why.
6. **"Anyone can POST a loan for any member."** Want: authentication, member
   from the session, a librarian role for returns.
7. **"A librarian wants to set a custom due date when lending a book. How
   would you add that to `POST /api/loans`?"** Talk only, no code. Want: an
   optional field with a stated format (`YYYY-MM-DD`); what happens when it
   is malformed, in the past, or a year away; the default stays server-side;
   existing clients keep working.
8. **"`GET /api/loans` returns every loan ever. Design the next version."**
   Want: pagination (`limit`/`offset` or a cursor) with a capped default,
   filters such as `?member_id=` / `?returned=false`, and what the response
   envelope looks like.
9. **"How would you test `/api/overdue`?"** Want: the existing `tests/`
   pattern; build loans relative to today rather than hard-coded dates (or
   inject the clock); cover due-today and returned-late.

## Scoring rubric

Score each 1–4. Running code is weighted double.

| Area | 1 | 4 |
| --- | --- | --- |
| **Runs (×2)** | App does not start at the end | Every finished task demonstrated live with curl |
| **Navigating the codebase** | Starts typing before reading; ignores existing patterns | Explores first, reuses `error()`, `to_json`, validation style |
| **Debugging** | Guesses, edits randomly, stuck on tracebacks | Reads the error, forms a hypothesis, checks docs, fixes |
| **Correctness** | Happy path only, 500s on bad input, wrong date format | Input validated, edge cases handled, nothing saved on a refused request |
| **API design** | Status codes arbitrary; can't say what is invalid or why | Deliberate, consistent status codes and error bodies; clear about which fields the client controls; explains trade-offs |
| **Using what's there** | Ignores the cheat sheet and existing routes, reinvents | Adapts the cheat sheet / existing code quickly; asks when unsure of syntax |
| **Communication** | Silent; doesn't ask questions | Narrates, asks clarifying questions, states trade-offs |
| **Design discussion** | Vague | Concrete, prioritised improvements |

Rough bar: Tasks 1–3 working and demonstrated = pass. Task 4 plus a solid
discussion = strong. All four written but the app doesn't start = fail,
however good the code looks.

## Feedback to give afterwards

- How many minutes before they first ran the app? Before they first ran
  their own change? Better or worse than mock #1?
- Did they add the three fields one at a time or all at once?
- How long on each trap, and how many hints? Was Trap C (stale database)
  instant this time?
- Did they notice the date format (Trap D) themselves?
- Did anything they finished get broken by a later change?

## Things worth telling them to study if they struggled

- Pony: both sides of a relationship (`Required`/`Optional` ↔ `Set`),
  `Optional` vs `Required` and defaults (value vs callable), re-seeding after
  a model change.
- HTTP: when to use 400 / 404 / 409 / 422, what a useful error body
  contains, which fields belong to the server rather than the client.
- Flask: `request.get_json(silent=True)`, `request.args.get`, returning
  `jsonify(...), 201`, `<int:id>` converters, what `jsonify` does with types
  it wasn't designed for.
- Parsing JSON defensively: is it a dict, is the key there, is it the right
  type, does the referenced row exist, is the action allowed in the current
  state.
