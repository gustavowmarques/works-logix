from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import ClientCompany
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

app = create_app()

sqlite_engine = create_engine('sqlite:///instance/worklogix.db')
SqliteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SqliteSession()

with app.app_context():
    print("Connected to:", db.engine.url)
    PostgresSession = sessionmaker(bind=db.engine)
    postgres_session = PostgresSession()

    metadata = MetaData()
    metadata.reflect(bind=sqlite_engine)
    client_table = metadata.tables['client']

    rows = sqlite_session.execute(client_table.select()).mappings().all()
    print(f"Found {len(rows)} clients to migrate...")

    postgres_session.query(Client).delete()
    postgres_session.commit()

    for row in rows:
        client = Client(
            name=row['name'],
            address=row['address'],
            registration_number=row['registration_number'],
            year_built=row['year_built'],
            number_of_units=row['number_of_units']
        )
        postgres_session.add(client)

    try:
        postgres_session.commit()
        print("✅ Clients migrated successfully!")
    except Exception as e:
        postgres_session.rollback()
        print(f"❌ Failed to commit: {e}")

    postgres_session.close()

sqlite_session.close()
