#!/usr/bin/env python3
"""
Diagnostic script to verify OTDailySummary setup
"""
import os
import sys
from datetime import datetime, date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import OTDailySummary, OTRequest, Employee

with app.app_context():
    print("\n" + "="*80)
    print("OT DAILY SUMMARY DIAGNOSTIC CHECK")
    print("="*80 + "\n")
    
    # Check 1: Table Exists
    print("1️⃣  CHECKING IF TABLE EXISTS...")
    try:
        # Try to query the table
        count = db.session.query(OTDailySummary).count()
        print(f"   ✅ hrm_ot_daily_summary table EXISTS")
        print(f"   📊 Total records in table: {count}\n")
    except Exception as e:
        print(f"   ❌ ERROR: Table doesn't exist!")
        print(f"   Details: {str(e)}\n")
        print("   FIX: Run migrations with: python -m flask db upgrade\n")
        sys.exit(1)
    
    # Check 2: Recent OTDailySummary records
    print("2️⃣  CHECKING FOR TODAY'S RECORDS...")
    today = date.today()
    today_records = db.session.query(OTDailySummary).filter_by(ot_date=today).all()
    print(f"   📅 Date checked: {today}")
    print(f"   📊 Records found: {len(today_records)}\n")
    
    if today_records:
        print("   ✅ TODAY'S RECORDS FOUND:\n")
        for record in today_records:
            emp = Employee.query.get(record.employee_id)
            emp_name = f"{emp.first_name} {emp.last_name}" if emp else "Unknown"
            print(f"      • {emp_name} (ID: {emp.employee_id if emp else 'N/A'})")
            print(f"        OT Hours: {record.ot_hours}")
            print(f"        OT Rate: ₹{record.ot_rate_per_hour}")
            print(f"        OT Amount: ₹{record.ot_amount}")
            print(f"        Status: {record.status}")
            print()
    else:
        print("   ⚠️  NO RECORDS FOUND FOR TODAY")
        print("   This could mean:")
        print("      1. No manager approved OT yet today")
        print("      2. OTDailySummary creation is failing silently\n")
    
    # Check 3: Pending OT Approvals (not yet converted to OTDailySummary)
    print("3️⃣  CHECKING FOR PENDING MANAGER APPROVALS...")
    from models import OTApproval
    pending = db.session.query(OTApproval).filter_by(
        level='L1',
        status='pending_manager'
    ).count()
    print(f"   📊 Pending manager approvals: {pending}\n")
    
    # Check 4: Recently completed approvals
    print("4️⃣  CHECKING RECENT APPROVED OT (Last 7 days)...")
    from sqlalchemy import and_
    recent_approvals = db.session.query(OTApproval).filter(
        and_(
            OTApproval.level == 'L1',
            OTApproval.status == 'manager_approved'
        )
    ).all()
    
    if recent_approvals:
        print(f"   ✅ Found {len(recent_approvals)} approved OT records:\n")
        for approval in recent_approvals[:5]:  # Show first 5
            ot_req = approval.ot_request
            emp = Employee.query.get(ot_req.employee_id)
            emp_name = f"{emp.first_name} {emp.last_name}" if emp else "Unknown"
            
            # Check if corresponding OTDailySummary exists
            summary = db.session.query(OTDailySummary).filter_by(
                employee_id=ot_req.employee_id,
                ot_date=ot_req.ot_date
            ).first()
            
            summary_status = "✅ HAS SUMMARY" if summary else "❌ NO SUMMARY"
            print(f"      • {emp_name} (Date: {ot_req.ot_date}) - {summary_status}")
    else:
        print("   ℹ️  No recent manager-approved OT records\n")
    
    # Check 5: Database Connection
    print("5️⃣  DATABASE CONNECTION TEST...")
    try:
        result = db.session.execute(db.text("SELECT 1")).scalar()
        print("   ✅ Database connection successful\n")
    except Exception as e:
        print(f"   ❌ Database connection failed: {str(e)}\n")
    
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"  Table exists: ✅")
    print(f"  Today's records: {len(today_records)}")
    print(f"  Pending approvals: {pending}")
    print(f"  Recent approved OT: {len(recent_approvals)}")
    print("="*80 + "\n")