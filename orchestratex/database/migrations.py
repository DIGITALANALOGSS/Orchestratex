from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os

from .models import Base

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/orchestratex")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create database tables."""
    if not database_exists(engine.url):
        create_database(engine.url)
        print("Database created successfully!")
    
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

def drop_tables():
    """Drop all tables."""
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped successfully!")

def reset_database():
    """Reset the entire database."""
    drop_tables()
    create_tables()
    print("Database reset completed!")

def upgrade_database():
    """Upgrade database schema."""
    # Check if tables exist
    inspector = engine.dialect.inspector(engine)
    existing_tables = inspector.get_table_names()
    
    # Get all model tables
    model_tables = [table.__tablename__ for table in Base.__subclasses__()] + ["alembic_version"]
    
    # Create missing tables
    missing_tables = set(model_tables) - set(existing_tables)
    if missing_tables:
        print(f"Creating missing tables: {missing_tables}")
        create_tables()
    else:
        print("All tables exist. No upgrade needed.")

def main():
    """Main function for database migrations."""
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "create":
            create_tables()
        elif command == "drop":
            drop_tables()
        elif command == "reset":
            reset_database()
        elif command == "upgrade":
            upgrade_database()
        else:
            print("Usage: python migrations.py [create|drop|reset|upgrade]")
    else:
        print("Usage: python migrations.py [create|drop|reset|upgrade]")

if __name__ == "__main__":
    main()
