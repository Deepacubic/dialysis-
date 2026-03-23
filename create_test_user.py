from app import app, db, Patient

def create_test_user():
    with app.app_context():
        # Check if user exists
        user = Patient.query.filter_by(email='test@example.com').first()
        if not user:
            new_user = Patient(
                name='Test User',
                email='test@example.com',
                password='password',
                age=45,
                dialysis_type='Hemodialysis',
                kidney_condition='CKD',
                ckd_stage='Stage 3'
            )
            db.session.add(new_user)
            db.session.commit()
            print("Test user created.")
        else:
            print("Test user already exists.")

if __name__ == "__main__":
    create_test_user()
