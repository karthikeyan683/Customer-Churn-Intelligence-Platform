from app.db.base import Base
from app.db.session import engine
from app.models import User


print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully! ✅")
