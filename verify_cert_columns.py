#!/usr/bin/env python
"""Verify certification columns added to Employee model"""
from models import Employee
from app import app, db

app.app_context().push()

# Get all columns
cols = [c.name for c in Employee.__table__.columns]

# Check for new columns
new_cols = ['hazmat_expiry', 'airport_pass_expiry', 'psa_pass_number', 'psa_pass_expiry']
present = [c in cols for c in new_cols]

print("=" * 60)
print("VERIFICATION: Certification Pass Renewal Fields")
print("=" * 60)
print()

for col, is_present in zip(new_cols, present):
    status = "✓" if is_present else "✗"
    print(f"{status} {col:<30} {'Present' if is_present else 'MISSING'}")

print()
print("=" * 60)
if all(present):
    print("✅ ALL COLUMNS VERIFIED - Database schema is correct!")
    print("=" * 60)
else:
    print("❌ COLUMNS MISSING - Database needs migration!")
    print("=" * 60)