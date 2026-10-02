import hashlib
import json
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, select
from sqlalchemy.engine import make_url
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from .config import ROOT
from .models import Item

metadata = MetaData()
items_table = Table("items", metadata,
    Column("id", String(16), primary_key=True),
    Column("type", String(80), nullable=False, index=True),
    Column("colour", String(60), nullable=False),
    Column("features", JSON, nullable=False),
    Column("description", String(600), nullable=False))
# Initial schema v1: only synthetic catalogue records; no query or profile tables.

def read_seed():
    data = json.loads((ROOT / "data/items.json").read_text(encoding="utf-8"))
    records = [Item.model_validate(row) for row in data]
    if len(records) != 30 or len({r.id for r in records}) != 30:
        raise ValueError("Seed must contain exactly 30 unique fictional items.")
    return records

def dataset_hash(records):
    raw = json.dumps([r.model_dump() for r in sorted(records, key=lambda r: r.id)],
                     sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()

def connect_database(database_url):
    if database_url.startswith("postgres://"):
        database_url = "postgresql+psycopg://" + database_url[len("postgres://"):]
    elif database_url.startswith("postgresql://"):
        database_url = "postgresql+psycopg://" + database_url[len("postgresql://"):]
    url = make_url(database_url)
    if url.get_backend_name() == "sqlite":
        if url.database and url.database != ":memory:":
            path = Path(url.database)
            if not path.is_absolute():
                path = ROOT / path
            path.parent.mkdir(parents=True, exist_ok=True)
            url = url.set(database=str(path))
        return create_engine(url, connect_args={"check_same_thread": False, "timeout": 15})
    if url.drivername != "postgresql+psycopg":
        raise ValueError("Use SQLite or PostgreSQL with psycopg.")
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 10})

def initialize(engine):
    records = read_seed()
    metadata.create_all(engine)
    insert = sqlite_insert if engine.dialect.name == "sqlite" else pg_insert
    with engine.begin() as conn:
        conn.execute(insert(items_table).values([r.model_dump() for r in records])
                     .on_conflict_do_nothing(index_elements=["id"]))
    return len(records)

def list_items(engine, category=None):
    stmt = select(items_table).order_by(items_table.c.id)
    if category and category != "All items":
        stmt = stmt.where(items_table.c.type == category)
    with engine.connect() as conn:
        return [Item.model_validate(dict(row)) for row in conn.execute(stmt).mappings()]

if __name__ == "__main__":
    from .config import load_settings
    engine = connect_database(load_settings().database_url)
    initialize(engine)
    print(f"Database ready: {len(list_items(engine))} synthetic items.")
