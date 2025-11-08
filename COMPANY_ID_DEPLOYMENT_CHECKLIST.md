# Company-Specific Employee ID - Deployment Checklist

## Pre-Deployment Verification

### Code Changes Review
- [ ] **models.py** - CompanyEmployeeIdConfig model added (lines 183-211)
- [ ] **routes.py** - Import statements updated (lines 16-19, 23-25)
- [ ] **routes.py** - employee_add() function updated (lines 626-677)
- [ ] **utils.py** - get_company_employee_id() function added (lines 119-158)

### Files Created
- [ ] init_company_employee_id_config.py
- [ ] test_company_employee_id.py
- [ ] COMPANY_EMPLOYEE_ID_IMPLEMENTATION_SUMMARY.md
- [ ] COMPANY_ID_SETUP.md
- [ ] docs/COMPANY_EMPLOYEE_ID_CONFIG.md
- [ ] COMPANY_ID_DEPLOYMENT_CHECKLIST.md

---

## Development Environment Testing

### Step 1: Database Setup
```bash
# [ ] Run migrations
flask db migrate -m "Add company employee ID configuration"
flask db upgrade

# Expected: Migration should complete without errors
# Check: hrm_company_employee_id_config table exists
```

### Step 2: Initialize Data
```bash
# [ ] Run initialization script
python init_company_employee_id_config.py

# Expected Output:
# - ✨ Configuration Initialization Complete!
# - Created: X configs
# - Total: Y companies
```

### Step 3: Verify System
```bash
# [ ] Run test script
python test_company_employee_id.py

# Expected Output:
# - ✨ All tests completed successfully!
# - All test results: ✅ PASS
```

### Step 4: Manual Testing
- [ ] Add new employee from Company A
  - Expected: ID format is COMPANY_A001
  - Verify: No errors in logs
  - Check: ID is unique in database

- [ ] Add another employee from Company A
  - Expected: ID format is COMPANY_A002
  - Verify: Sequence incremented correctly

- [ ] Add new employee from Company B
  - Expected: ID format is COMPANY_B001 (NOT COMPANY_B003)
  - Verify: Companies have independent sequences

- [ ] Edit existing employee
  - Expected: Employee ID does not change
  - Verify: Other fields update normally

---

## Staging Environment Testing

### Data Consistency
- [ ] Check database constraints
  ```sql
  SELECT COUNT(*) FROM hrm_company_employee_id_config;
  -- Should be >= number of companies with employees
  ```

- [ ] Verify no duplicate company_ids
  ```sql
  SELECT company_id, COUNT(*) 
  FROM hrm_company_employee_id_config 
  GROUP BY company_id 
  HAVING COUNT(*) > 1;
  -- Should return 0 rows
  ```

- [ ] Check employee ID uniqueness
  ```sql
  SELECT employee_id, COUNT(*) 
  FROM hrm_employee 
  GROUP BY employee_id 
  HAVING COUNT(*) > 1;
  -- Should return 0 rows
  ```

### Functional Testing
- [ ] Create 10 test employees per company
- [ ] Verify IDs follow pattern: COMPANY_CODE###
- [ ] Verify sequences are independent
- [ ] Test with special company codes (with numbers, lowercase)

### Performance Testing
- [ ] Bulk create 100 employees
  - [ ] Measure: Response time < 5 seconds
  - [ ] Check: No database locks
  - [ ] Verify: All IDs generated correctly

- [ ] Concurrent employee creation (5 parallel requests)
  - [ ] Verify: No duplicate IDs generated
  - [ ] Check: All requests succeed

### Rollback Testing
- [ ] Can rollback database to pre-implementation state
- [ ] Old employee IDs are preserved
- [ ] System continues to work with old ID format

---

## Production Deployment

### Pre-Deployment
- [ ] Database backup created
  ```bash
  # Backup production database before deployment
  pg_dump hrms_production > hrms_backup_$(date +%Y%m%d).sql
  ```

- [ ] Notify team of maintenance window
- [ ] Prepare rollback plan

### Deployment Steps
```bash
# Step 1: Deploy code changes
# [ ] Update code files (models.py, routes.py, utils.py)

# Step 2: Run migrations
# [ ] flask db upgrade
#     Expected: Migration completes without errors

# Step 3: Initialize configurations
# [ ] python init_company_employee_id_config.py
#     Expected: All companies configured

# Step 4: Verify installation
# [ ] python test_company_employee_id.py
#     Expected: All tests pass
```

### Post-Deployment Verification
- [ ] Test employee creation on production
- [ ] Verify IDs follow company-specific pattern
- [ ] Check application logs for errors
- [ ] Verify database performance (no slowdowns)
- [ ] Test with mobile app (if applicable)

### Monitoring (First 24 Hours)
- [ ] Monitor error logs for CompanyEmployeeIdConfig errors
- [ ] Check database performance metrics
- [ ] Verify no duplicate employee IDs created
- [ ] Monitor employee creation latency
- [ ] Confirm all existing employees unaffected

---

## Rollback Plan (If Needed)

### Quick Rollback (< 30 minutes)
```bash
# If deployment failed before full initialization:

# 1. Restore database
psql hrms_production < hrms_backup_YYYYMMDD.sql

# 2. Revert code changes
git checkout HEAD~1 -- models.py routes.py utils.py

# 3. Restart application
systemctl restart flask_app
```

### Full Rollback
```bash
# If issues detected after deployment:

# 1. Delete configuration table
# [ ] Drop table hrm_company_employee_id_config

# 2. Restore database
# [ ] Restore from backup

# 3. Revert code
# [ ] Git revert all changes

# 4. Test
# [ ] Run manual tests
# [ ] Verify old system working
```

---

## Post-Deployment Monitoring

### Daily Checks (First Week)
- [ ] Monitor employee creation count
- [ ] Check for ID generation errors
- [ ] Verify configuration table updates
- [ ] Review application logs

### Weekly Checks
- [ ] Run test_company_employee_id.py
- [ ] Check configuration consistency
- [ ] Verify no ID gaps or duplicates

### Monthly Checks
- [ ] Analyze ID usage patterns
- [ ] Check table growth rate
- [ ] Performance metrics review
- [ ] User feedback collection

---

## Success Criteria

✅ All criteria must be met before considering deployment complete:

- [ ] All tests pass (both automated and manual)
- [ ] Employee IDs follow pattern: CompanyCode###
- [ ] Each company has independent sequence
- [ ] No duplicate employee IDs in database
- [ ] Database performance acceptable (< 100ms response)
- [ ] No errors in application logs
- [ ] Existing employees unaffected
- [ ] Old employee IDs preserved
- [ ] New employees receive correct IDs
- [ ] System scalable to 10,000+ employees

---

## Support & Documentation

### If Issues Occur
1. Check logs: Check application error logs for clues
2. Test connectivity: Run `python test_company_employee_id.py`
3. Check database: Verify hrm_company_employee_id_config data
4. Contact: Review documentation in `docs/COMPANY_EMPLOYEE_ID_CONFIG.md`

### Documentation References
- **Quick Setup:** `COMPANY_ID_SETUP.md`
- **Full Docs:** `docs/COMPANY_EMPLOYEE_ID_CONFIG.md`
- **Implementation Details:** `COMPANY_EMPLOYEE_ID_IMPLEMENTATION_SUMMARY.md`
- **Troubleshooting:** `docs/COMPANY_EMPLOYEE_ID_CONFIG.md` (Troubleshooting section)

---

## Sign-Off

### Development Team
- [ ] Code reviewed
- [ ] All tests passed
- [ ] Documentation complete
- Reviewed by: _________________ Date: _______

### QA Team  
- [ ] Testing completed
- [ ] Staging deployment verified
- [ ] Performance acceptable
- Approved by: _________________ Date: _______

### Operations Team
- [ ] Deployment procedure ready
- [ ] Monitoring setup configured
- [ ] Rollback plan documented
- [ ] Database backup created
- Approved by: _________________ Date: _______

### Manager Approval
- [ ] Ready for production
- [ ] Risk assessment complete
- [ ] Maintenance window approved
- Approved by: _________________ Date: _______

---

## Notes & Observations

```
[Use this section to document any issues, observations, or special notes during deployment]

Date: ________
Issue: _____________________________________________________________________
Resolution: _________________________________________________________________

---

Date: ________
Issue: _____________________________________________________________________
Resolution: _________________________________________________________________
```

---

## Completion Summary

**Status:** ⬜ Not Started | 🟡 In Progress | 🟢 Complete | ❌ Failed

- [ ] **Development Testing**: _______
- [ ] **Staging Deployment**: _______
- [ ] **Production Deployment**: _______
- [ ] **Post-Deployment Monitoring**: _______

**Final Status:** 🟢 Ready for Production | 🟡 Requires More Testing | ❌ Hold Deployment

---

**Last Updated:** [Date]
**Deployed By:** [Name]
**Deployment Date:** [Date]
**Version:** 1.0