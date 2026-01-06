# Setting Up Daily Attendance Cron Job on Render

Follow these steps to configure the automatic daily attendance processing.

## Prerequisites
- You must have a Render account.
- Your web service should already be deployed and running.

## Step-by-Step Guide

### 1. Create the Cron Job
1.  Log in to your [Render Dashboard](https://dashboard.render.com).
2.  Click the **"New +"** button in the top right.
3.  Select **"Cron Job"**.

### 2. Configure Basic Details
-   **Name**: `daily-attendance-eod`
-   **Region**: Select the **same region** as your Database and Web Service (e.g., Oregon).
-   **Runtime**: `Python 3`
-   **Build Command**: `pip install -r requirements.txt`
-   **Schedule**: `0 0 * * *`
    -   This runs the job daily at **Midnight UTC**.
    -   *Note: If you are in Singapore (UTC+8), this will run at 8:00 AM SGT. Adjust if you need it to run closer to your local midnight (e.g. `0 16 * * *` for midnight SGT).*
-   **Command**: `python services/daily_attendance_task.py`

### 3. Environment Variables (Critical)
The script needs access to your database.

1.  Scroll down to the **"Environment Variables"** section.
2.  **Option A (Recommended)**: If you have an **Environment Group** for your project, click **"Link Environment Group"** and select it.
3.  **Option B (Manual)**: Add the following variables manually:
    -   `DATABASE_URL`: (Copy the *Internal Connection String* from your Render PostgreSQL dashboard)
    -   `FLASK_APP`: `main.py`
    -   `PYTHONPATH`: `.` (Optional, but good practice)

### 4. Deploy
1.  Click **"Create Cron Job"**.
2.  Render will verify the build (installing requirements) and run the job according to the schedule.

## Verification
1.  Wait for the scheduled time OR click **"Trigger Run"** in the Render dashboard to test it immediately.
2.  Log in to your **App Dashboard** as a Super Admin.
3.  Go to **Admin** -> **Job Monitoring**.
4.  You should see a new entry with status `Success`.

---
**Note:** The script `services/daily_attendance_task.py` automatically handles finding the project root and loading the Flask app context, so simply running it with python is sufficient as long as dependencies are installed.
