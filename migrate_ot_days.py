from app import app, db
from sqlalchemy import text

def migrate_ot_days():
    with app.app_context():
        print("Starting OT Type migration...")
        
        try:
            with db.engine.connect() as conn:
                # 1. Add day boolean columns
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for day in days:
                    try:
                        # Establish defaults: standard workdays true, weekends false
                        default_val = 'TRUE' if day not in ['saturday', 'sunday'] else 'FALSE'
                        conn.execute(text(f"ALTER TABLE hrm_ot_type ADD COLUMN {day} BOOLEAN DEFAULT {default_val}"))
                        print(f"Added {day} column.")
                    except Exception as e:
                        print(f"Skipping {day} (may exist): {str(e)}")

                # 2. Drop obsolete applicable_days column
                try:
                    conn.execute(text("ALTER TABLE hrm_ot_type DROP COLUMN applicable_days"))
                    print("Dropped applicable_days column.")
                except Exception as e:
                    print(f"Skipping drop applicable_days: {str(e)}")

                conn.commit()
                print("Migration completed.")

        except Exception as e:
            print(f"Migration failed: {str(e)}")

if __name__ == '__main__':
    migrate_ot_days()
