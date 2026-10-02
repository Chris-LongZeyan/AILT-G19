import os
import pytest
from sqlalchemy import inspect
from lostfound.database import connect_database, initialize, list_items, dataset_hash, read_seed

def test_sqlite_persistence_and_idempotent_seed(tmp_path):
    url = "sqlite:///" + str(tmp_path / "items.db")
    engine = connect_database(url)
    initialize(engine)
    initialize(engine)
    records = list_items(engine)
    assert len(records) == 30
    assert list_items(engine, "Bottle")[0].id == "LF-001"
    assert len(list_items(engine, "Bottle")) == 3
    assert inspect(engine).get_table_names() == ["items"]
    engine.dispose()
    reopened = connect_database(url)
    assert dataset_hash(list_items(reopened)) == dataset_hash(read_seed())
    reopened.dispose()

@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="Requires a dedicated PostgreSQL test database")
def test_postgresql_roundtrip():
    engine = connect_database(os.environ["TEST_DATABASE_URL"])
    assert engine.dialect.name == "postgresql"
    initialize(engine)
    initialize(engine)
    assert len(list_items(engine)) == 30
    assert len(list_items(engine, "Bottle")) == 3
    engine.dispose()
