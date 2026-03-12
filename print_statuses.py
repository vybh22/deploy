from app import create_app
from app.models import db, Donation

app = create_app()
with app.app_context():
    statuses = [d.status for d in Donation.query.all()]
    print(statuses)
