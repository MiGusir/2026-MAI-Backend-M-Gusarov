"""Seed demo data for mini-NetBox."""

from database import SessionLocal
from models import Category, Profile, Server, Tag, User


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(User).first():
            print("Seed skipped: data already exists.")
            return

        user_admin = User(username="admin", email="admin@netbox.local")
        user_ops = User(username="ops", email="ops@netbox.local")
        db.add_all([user_admin, user_ops])
        db.flush()

        db.add_all(
            [
                Profile(user_id=user_admin.id, full_name="System Admin", role="admin"),
                Profile(user_id=user_ops.id, full_name="Operations Engineer", role="operator"),
            ]
        )

        cat_compute = Category(slug="compute", title="Compute")
        cat_network = Category(slug="network", title="Network")
        db.add_all([cat_compute, cat_network])
        db.flush()

        tag_prod = Tag(name="prod")
        tag_edge = Tag(name="edge")
        tag_vm = Tag(name="vm")
        db.add_all([tag_prod, tag_edge, tag_vm])
        db.flush()

        srv1 = Server(
            hostname="srv-app-01",
            ip_address="10.10.1.11",
            status="active",
            category_id=cat_compute.id,
            owner_id=user_admin.id,
        )
        srv2 = Server(
            hostname="srv-edge-01",
            ip_address="10.10.2.21",
            status="active",
            category_id=cat_network.id,
            owner_id=user_ops.id,
        )
        db.add_all([srv1, srv2])
        db.flush()

        srv1.tags.extend([tag_prod, tag_vm])
        srv2.tags.extend([tag_prod, tag_edge])

        db.commit()
        print("Seed completed successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
