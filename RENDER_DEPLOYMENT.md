# Render Deployment Guide for Daily Attendance Auto-Creation

Since Render uses Linux containers, the Windows batch file won't work. Here are several solutions for automating daily attendance creation on Render:

## Option 1: Manual Trigger (Recommended for Start)

### How it works:
- Use the "Auto Create" button in the Bulk Management interface
- HR/Admin can manually create attendance records for any date
- Perfect for getting started and testing

### Usage:
1. Go to **Attendance** → **Bulk Management**
2. Select the date you want to create records for
3. Click the **"Auto Create"** button
4. All active employees will get attendance records with "Present" status

## Option 2: External Cron Service with API (Recommended for Production)

### How it works:
- Use external services like GitHub Actions, Heroku Scheduler, or cron-job.org
- Call the API endpoint daily to create attendance records
- Most reliable and cost-effective solution

### Setup Steps:

#### 1. Set Environment Variable in Render:
```
ATTENDANCE_API_KEY=your-super-secret-api-key-here
```

#### 2. Use GitHub Actions (Free):
- The `.github/workflows/daily-attendance.yml` file is already created
- Add these secrets to your GitHub repository:
  - `APP_URL`: Your Render app URL (e.g., `https://your-app.onrender.com`)
  - `ATTENDANCE_API_KEY`: Same key as set in Render environment

#### 3. Alternative: Use cron-job.org:
- Sign up at https://cron-job.org
- Create a new cron job with:
  - URL: `https://your-app.onrender.com/api/attendance/auto-create`
  - Method: POST
  - Headers: `X-API-Key: your-super-secret-api-key-here`
  - Schedule: Daily at 00:01

#### 4. Test the API:
```bash
curl -X POST "https://your-app.onrender.com/api/attendance/auto-create" \
  -H "X-API-Key: your-super-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-01-15"}'
```

## Option 3: Render Cron Jobs (If Available)

### How it works:
- Use Render's Cron Jobs service (if available in your plan)
- Run the `render_cron.py` script daily

### Setup:
1. Create a new Cron Job service in Render
2. Set the command: `python render_cron.py`
3. Set the schedule: `0 0 * * *` (daily at midnight)
4. Connect to the same database as your web service

## Option 4: Background Task with APScheduler

### How it works:
- Add a background scheduler to your Flask app
- Automatically creates attendance records when the app starts

### Implementation:
Add this to your `app.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

def scheduled_attendance_creation():
    """Background task to create daily attendance"""
    with app.app_context():
        auto_create_daily_attendance()

# Start scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=scheduled_attendance_creation,
    trigger="cron",
    hour=0,
    minute=1,
    id='daily_attendance'
)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
```

**Note**: This only works if your Render service stays running 24/7, which may not be guaranteed on free plans.

## Recommended Approach for Render:

1. **Start with Option 1** (Manual Trigger) to test the system
2. **Move to Option 2** (External Cron + API) for production
3. Use **GitHub Actions** as it's free and reliable

## Security Notes:

- Always use a strong API key
- Store the API key in environment variables, never in code
- Consider adding IP whitelisting if using external services
- Monitor the API endpoint for unusual activity

## Troubleshooting:

### If attendance records aren't being created:
1. Check the API key is correct
2. Verify the app URL is accessible
3. Check Render logs for any errors
4. Test the API endpoint manually with curl

### If you get authentication errors:
1. Verify the `ATTENDANCE_API_KEY` environment variable is set in Render
2. Make sure the API key in your external service matches exactly
3. Check that the header name is `X-API-Key` (case-sensitive)

## Files Created for Render Deployment:

- `render_cron.py` - Direct script for Render Cron Jobs
- `run_daily_attendance.sh` - Linux shell script (alternative)
- `.github/workflows/daily-attendance.yml` - GitHub Actions workflow
- API endpoint: `/api/attendance/auto-create` - For external services
- Manual trigger: "Auto Create" button in Bulk Management interface

Choose the option that best fits your needs and Render plan!