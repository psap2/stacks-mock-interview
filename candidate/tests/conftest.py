import os
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Point the app at a throwaway database before it is imported.
_tmp = tempfile.mkdtemp()
os.environ["STACKS_DB"] = os.path.join(_tmp, "test.sqlite")

from app import app  # noqa: E402
from models import db  # noqa: E402
from seed import seed  # noqa: E402


@pytest.fixture()
def client():
    """A test client backed by a freshly seeded database."""
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    seed()
    return app.test_client()
