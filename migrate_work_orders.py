from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import WorkOrder, User
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

app = create_app()

# SQLite source
sqlite_engine = create_engine('sqlite:///instance/worklogix.db')
SqliteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SqliteSession()

with app.app_context():
    print("Connected to:", db.engine.url)

    PostgresSession = sessionmaker(bind=db.engine)
    postgres_session = PostgresSession()

    metadata = MetaData()
    metadata.reflect(bind=sqlite_engine)
    wo_table = metadata.tables['work_order']

    rows = sqlite_session.execute(wo_table.select()).mappings().all()
    print(f"Found {len(rows)} work orders to migrate...")

    postgres_session.query(WorkOrder).delete()
    postgres_session.commit()

    inserted_count = 0
    skipped_count = 0

    for row in rows:
        # Skip if FK user IDs (contractor, preferred, second preferred) are invalid
        skip = False
        for fk_field in ['contractor_id', 'preferred_contractor_id', 'second_preferred_contractor_id']:
            fk_value = row.get(fk_field)
            if fk_value is not None:
                user_exists = db.session.query(User.id).filter_by(id=fk_value).first()
                if not user_exists:
                    print(f"⏭ Skipping work order '{row['title']}' — missing user id {fk_value} ({fk_field})")
                    skipped_count += 1
                    skip = True
                    break

        if skip:
            continue

        work_order = WorkOrder(
            title=row['title'],
            description=row['description'],
            status=row['status'],
            created_by=row['created_by'],
            created_at=row.get('created_at', datetime.now(timezone.utc)),

            client_id=row['client_id'],
            contractor_id=row['contractor_id'],
            business_type=row['business_type'],
            completion_photo=row['completion_photo'],
            occupant_apartment=row['occupant_apartment'],
            occupant_phone=row['occupant_phone'],
            occupant_name=row['occupant_name'],
            preferred_contractor_id=row['preferred_contractor_id'],
            second_preferred_contractor_id=row['second_preferred_contractor_id'],
            rejected_by=row['rejected_by']
        )
        postgres_session.add(work_order)
        inserted_count += 1

    try:
        postgres_session.commit()
        print(f"✅ Work orders migrated successfully! Inserted: {inserted_count}, Skipped: {skipped_count}")
    except Exception as e:
        postgres_session.rollback()
        print(f"❌ Failed to commit: {e}")

    postgres_session.close()

sqlite_session.close()
