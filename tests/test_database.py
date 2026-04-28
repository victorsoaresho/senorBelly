from sqlalchemy import text
from app.database import get_db_session


def test_database_connection():
    session = get_db_session()
    result = session.execute(text("SELECT 1")).scalar()

    assert result == 1
