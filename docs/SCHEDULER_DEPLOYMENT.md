# Deploying the Report Scheduler

To run the report scheduler on a production server (like Render, Heroku, or a VPS), follow these guidelines to ensure reliability and avoid duplicate emails.

## Preferred Method: Dedicated Background Worker

Running the scheduler as a separate process is the most robust way to manage dynamic report schedules.

### 1. The Worker Script
I have created a dedicated script [scheduler_worker.py](file:///d:/Project/Workouts/hrm/scheduler_worker.py). This script initializes the app context and keeps the scheduler running in a single process.

### 2. Configuration for Web Service
If you are using a WSGI server like Gunicorn with multiple workers (e.g., `gunicorn -w 4 app:app`), you should **disable** the scheduler in your web workers to prevent them from all starting their own schedulers.

- **Environment Variable**: Set `ENABLE_SCHEDULER=False` in your Web Service's environment variables.

### 3. Configuration for Background Worker
Create a new **Background Worker** (on Render) or a separate process with:
- **Command**: `python scheduler_worker.py`
- **Environment Variables**: Use the same variables as your Web Service (DATABASE_URL, etc.), but ensure `ENABLE_SCHEDULER` is set to `True` (or omitted, as it defaults to True in the worker script).

## Alternative: Render Cron Job (For Fixed-Time Reports)

If you only have a few reports and they all run at the same fixed time (e.g., daily at 8:00 AM), you can use a **Render Cron Job** instead of a persistent worker to save resources.

### 1. Unified Trigger Script
You can use the existing `services/daily_cron_runner.py`, which I've updated to include **Phase 3: Scheduled Reports**. This runs auto-closing, EOD processing, and scheduled reports in one go.

### 2. Configure Render Cron Job
- **Command**: `python services/daily_cron_runner.py`
- **Schedule**: `0 0 * * *` (Daily at Midnight UTC).
- **Environment Variables**: Use the same as your Web Service.

> [!NOTE]
> This is now the **preferred method** for daily report delivery if you already have the attendance cron job set up on Render.

## Summary of Files
- [app.py](file:///d:/Project/Workouts/hrm/app.py): Updated to check for `ENABLE_SCHEDULER`.
- [scheduler_worker.py](file:///d:/Project/Workouts/hrm/scheduler_worker.py): Recommended for high-frequency or multi-timeframe dynamic scheduling.
- [daily_cron_runner.py](file:///d:/Project/Workouts/hrm/services/daily_cron_runner.py): Unified script for all midnight tasks (Attendance + Reports).
