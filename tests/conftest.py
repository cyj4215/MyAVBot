import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.database import Base

TEST_DB_URL = os.environ.get("TEST_DB_URL", "sqlite:///:memory:")
test_engine = create_engine(TEST_DB_URL, echo=False)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    Base.metadata.create_all(bind=test_engine)
    import shared.database as db_mod
    monkeypatch.setattr(db_mod, "SessionLocal", TestSession)
    yield
    Base.metadata.drop_all(bind=test_engine)
