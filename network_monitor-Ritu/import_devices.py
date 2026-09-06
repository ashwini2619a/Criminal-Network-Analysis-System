import csv
from app import app
from models import db, Device


def import_devices(csv_path):
    print(f"Reading File: {csv_path}")

    added = 0
    skipped = 0

    with app.app_context():
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                ip = row["ip"].strip()
                device_type = row["device_type"].strip()
                location = row["location"].strip()

                existing = Device.query.filter_by(ip=ip).first()
                if existing:
                    print(f"Skipped {ip}: already in database")
                    skipped += 1
                else:
                    device = Device(ip=ip, device_type=device_type, location=location)
                    db.session.add(device)
                    added += 1
                    print(f"Added {ip} | {device_type} | {location}")

            db.session.commit()

    print(f"Added: {added} | Skipped: {skipped} | Total: {skipped + added}")


# ── Run directly to import devices ──
if __name__ == "__main__":
    import_devices('data/devices.csv')