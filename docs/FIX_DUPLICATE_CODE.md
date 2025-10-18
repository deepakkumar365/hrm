# Fix for Duplicate Code in routes.py

## Problem
The `auto_syntax_fix.py` created a complete version of the `claims_approve` function, but the incomplete version was left in the file as well. This caused:
- Duplicate `elif action == 'reject':` blocks
- Duplicate exception handlers
- **IndentationError** because the second elif is badly indented (3 spaces instead of 8)

## Solution Implemented

Three files work together to fix this automatically:

### 1. **cleanup_duplicate_code.py** (NEW)
- Runs **first** when the app starts
- Scans routes.py for the badly indented elif (starts with exactly 3 spaces)
- Removes all duplicate code from that point onwards
- Leaves the file with a clean, complete claims_approve function

### 2. **auto_syntax_fix.py** (EXISTING)
- Runs **second** 
- Checks if the claims_approve function is complete
- Adds any missing components if needed
- Safe to run multiple times

### 3. **main.py** (UPDATED)
- Now imports cleanup_duplicate_code BEFORE auto_syntax_fix
- This ensures duplicates are removed before any repair attempts

## How It Works

When you run `python main.py`:

```
main.py starts
  ↓
cleanup_duplicate_code.py imported
  ↓
cleanup_routes() executes (module-level)
  ↓
Finds badly indented elif and removes lines 2935-2949
  ↓
routes.py is now clean (ends at line 2934)
  ↓
auto_syntax_fix.py imported
  ↓
Verifies claims_approve is complete
  ↓
routes.py imported (should be syntax-valid now!)
  ↓
App runs successfully
```

## To Apply This Fix

Simply run from PyCharm or terminal:

```bash
python main.py
```

The fix runs automatically on startup.

## Verification

You should see these messages:

```
✅ Cleaned up duplicate code - removed X lines from routes.py
✅ Fixed syntax error in routes.py
✅ Default master data created successfully!
 * Running on http://127.0.0.1:5000
```

## What Gets Removed

The cleanup removes lines 2935-2949 which contain:
- Badly indented `elif action == 'reject':`
- Duplicate claim status and rejection_reason code
- Duplicate `db.session.commit()` and return statements
- Duplicate exception handlers

The properly formatted versions remain at lines 2921-2934.

## If It Still Doesn't Work

Check:
1. Did you see the "Cleaned up duplicate code" message?
2. Did you see the "Fixed syntax error" message?
3. Try: `python verify_syntax_fix.py` to see detailed status

If the syntax error persists, check that `cleanup_duplicate_code.py` is in the root directory and `main.py` has the import statement.