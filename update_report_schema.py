from app import app, db
from sqlalchemy import text

def update_schema():
    with app.app_context():
        try:
            # Check and add company_id
            print("Adding company_id to hrm_report_schedule...")
            db.session.execute(text('ALTER TABLE hrm_report_schedule ADD COLUMN IF NOT EXISTS company_id UUID'))
            
            # Check and add date_filter_type
            print("Adding date_filter_type to hrm_report_schedule...")
            db.session.execute(text('ALTER TABLE hrm_report_schedule ADD COLUMN IF NOT EXISTS date_filter_type VARCHAR(50)'))
            
            # Add foreign key constraint if it doesn't exist
            # Note: Checking for existing constraint is harder in standard SQL without pg_catalog,
            # but usually ADD CONSTRAINT doesn't have IF NOT EXISTS in all PG versions.
            # We'll just try to add it and catch if it fails (likely because it exists).
            try:
                db.session.execute(text('ALTER TABLE hrm_report_schedule ADD CONSTRAINT fk_report_schedule_company FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE'))
            except Exception as e:
                print(f"Note: Could not add FK constraint (maybe it already exists): {e}")
            
            db.session.commit()
            print("Schema update complete!")
        except Exception as e:
            print(f"Error updating schema: {e}")
            db.session.rollback()

if __name__ == "__main__":
    update_schema()
