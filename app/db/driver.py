from neo4j import GraphDatabase
from app.core.config import get_settings

settings = get_settings()

driver = GraphDatabase.driver(
    settings.cognodb_uri,
    auth=(settings.cognodb_username, settings.cognodb_password),
)

def verify_database_connection() -> None:
    driver.verify_connectivity()

def close_database() -> None:
    driver.close()
