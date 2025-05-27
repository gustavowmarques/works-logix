import os
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from app import create_app, db
from app.models import User

# Init Flask app
app = create_app()
with app.app_context():
    print("Connected to:", db.engine.url)


# SQLite source
sqlite_engine = create_engine('sqlite:///instance/worklogix.db')
SqliteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SqliteSession()

with app.app_context():
    # ✅ Print the actual database your app is using
    print("Connected to:", db.engine.url)

    # PostgreSQL session using your app's config
    PostgresSession = sessionmaker(bind=db.engine)
    postgres_session = PostgresSession()

    # Reflect the SQLite user table
    metadata = MetaData()
    metadata.reflect(bind=sqlite_engine)
    user_table = metadata.tables['user']

    # Fetch rows with dict support
    rows = sqlite_session.execute(user_table.select()).mappings().all()
    print(f"Found {len(rows)} users to migrate...")

    # Clear existing PostgreSQL users
    print("🧹 Clearing existing users in PostgreSQL...")
    postgres_session.query(User).delete()
    postgres_session.commit()

    for row_data in rows:
        user = User(
            username=row_data['username'],
            email=row_data['email'],
            password_hash=row_data['password_hash'],
            role=row_data['role'],
            business_type=row_data['business_type']
        )
        postgres_session.add(user)

    try:
        postgres_session.commit()
        print("✅ Users migrated successfully!")
    except Exception as e:
        postgres_session.rollback()
        print(f"❌ Failed to commit: {e}")

    postgres_session.close()

sqlite_session.close()
