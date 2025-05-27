from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import Contractor
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
    contractor_table = metadata.tables['contractor']

    rows = sqlite_session.execute(contractor_table.select()).mappings().all()
    print(f"Found {len(rows)} contractors to migrate...")

    postgres_session.query(Contractor).delete()
    postgres_session.commit()

    for row in rows:
        contractor = Contractor(
            company_name=row['company_name'],
            company_registration_number=row['company_registration_number'],
            email=row['email'],
            telephone=row['telephone'],
            accounts_contact_name=row['accounts_contact_name'],
            accounts_contact_email=row['accounts_contact_email'],
            address=row['address'],
            business_type=row['business_type']
        )
        postgres_session.add(contractor)

    try:
        postgres_session.commit()
        print("✅ Contractors migrated successfully!")
    except Exception as e:
        postgres_session.rollback()
        print(f"❌ Failed to commit: {e}")

    postgres_session.close()

sqlite_session.close()
