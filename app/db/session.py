from contextlib import contextmanager
from app.db.driver import driver

@contextmanager
def get_session():
    session = driver.session()
    try:
        yield session
    finally:
        session.close()
