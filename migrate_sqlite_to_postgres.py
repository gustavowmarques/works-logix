import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

# SQLite source
SQLITE_URL = 'sqlite:///worklogix.db'

# PostgreSQL target (Render DB)
POSTGRES_URL = 'postgresql://works_logix_db_user:FM68PNcP6ic1WyyfZIAJmnCuMwHJgDc9@dpg-d0d8f13e5dus73a7armg-a.oregon-postgres.render.com/works_logix_db'

# Connect to both engines
sqlite_engine = sa.create_engine(SQLITE_URL)
postgres_engine = sa.create_engine(POSTGRES_URL)

# Create sessions
SqliteSession = sessionmaker(bind=sqlite_engine)
PostgresSession = sessionmaker(bind=postgres_engine)

sqlite_session = SqliteSession()
postgres_session = PostgresSession()

# Reflect metadata from SQLite
metadata = MetaData()
metadata.reflect(bind=sqlite_engine)

# Create the same tables in PostgreSQL
metadata.create_all(bind=postgres_engine)

# Migrate each table
for table_name in metadata.tables:
    print(f"🔄 Migrating table: {table_name}")
    table = Table(table_name, metadata, autoload_with=sqlite_engine)

    try:
        rows = sqlite_session.execute(table.select()).fetchall()

        if rows:
            insert_stmt = table.insert().values([dict(row) for row in rows])
            postgres_session.execute(insert_stmt)
            postgres_session.commit()
            print(f"✅ Inserted {len(rows)} rows into {table_name}")
        else:
            print(f"⚠️ No data to migrate for {table_name}")
    except SQLAlchemyError as e:
        print(f"❌ Error migrating {table_name}: {e}")

# Close sessions
sqlite_session.close()
postgres_session.close()

print("🎉 Migration complete.")
