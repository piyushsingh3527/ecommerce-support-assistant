from getpass import getpass

from app.core.security import hash_password
from app.db.models.user import User
from app.db.session import SessionLocal


db = SessionLocal()

try:
    name = input("Admin name: ")
    email = input("Admin email: ")
    password = getpass("Admin password: ")

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        print("A user with this email already exists.")
    else:
        admin = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("Admin user created successfully.")

finally:
    db.close()