from backend.database.database import engine
from backend.database.models import Base

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")