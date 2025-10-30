import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

logger = logging.getLogger(__name__)

# Scheduler instance
scheduler = BackgroundScheduler()

# This is a placeholder for the function that sends the message.
# It will be set from app.py to avoid circular imports.
send_message_func = None

def start_scheduler():
    """Starts the background scheduler if it's not already running."""
    if not scheduler.running:
        scheduler.start()
        logger.info("BackgroundScheduler started.")

def set_send_message_func(func):
    """Sets the function to send messages, injected from app.py."""
    global send_message_func
    send_message_func = func

def add_reminder(sender_id: str, time_str: str, message: str) -> str:
    """
    Adds a reminder job to the scheduler.
    time_str can be '10m' (minutes) or '1h' (hours).
    """
    
    time_str = time_str.lower().strip()
    delay_seconds = 0
    
    try:
        if time_str.endswith('m'):
            minutes = int(time_str[:-1])
            delay_seconds = minutes * 60
        elif time_str.endswith('h'):
            hours = int(time_str[:-1])
            delay_seconds = hours * 3600
        else:
            return "⚠️ Invalid time format. Use '10m' for 10 minutes or '1h' for 1 hour."
            
        if delay_seconds <= 0:
            return "⚠️ Reminder time must be in the future."

        run_date = datetime.now() + timedelta(seconds=delay_seconds)
        
        # Define the job function that will be executed
        def reminder_job():
            logger.info(f"Executing reminder for {sender_id}: {message}")
            if send_message_func:
                reminder_text = f"🔔 *REMINDER* 🔔\n\n**From HOC/Asst HOC:**\n{message}"
                send_message_func(sender_id, reminder_text)
            else:
                logger.error("send_message_func not set in scheduler.py")

        # Add the job
        job = scheduler.add_job(
            reminder_job, 
            'date', 
            run_date=run_date, 
            id=f"reminder_{sender_id}_{run_date.timestamp()}",
            misfire_grace_time=300 # 5 minutes grace time
        )
        
        logger.info(f"Reminder set for {sender_id} at {run_date.strftime('%Y-%m-%d %H:%M:%S')}. Job ID: {job.id}")
        return f"✅ Reminder set! I will send the message in {time_str} at {run_date.strftime('%I:%M %p')}."

    except ValueError:
        return "⚠️ Could not parse the time or message. Usage: `/remind <time> <message>` (e.g., `/remind 10m Submit report`)"
    except Exception as e:
        logger.error(f"Error adding reminder: {e}")
        return "❌ An error occurred while setting the reminder."

def clear_reminders(sender_id: str) -> str:
    """Clears all scheduled reminders for the given sender_id (or all if not specified)."""
    
    jobs_cleared = 0
    for job in scheduler.get_jobs():
        # A simple check to see if the job ID contains the sender's ID (based on how we create the ID)
        if f"reminder_{sender_id}" in job.id:
            try:
                scheduler.remove_job(job.id)
                jobs_cleared += 1
            except JobLookupError:
                # Should not happen, but good to handle
                logger.warning(f"Attempted to clear non-existent job: {job.id}")
            except Exception as e:
                logger.error(f"Error removing job {job.id}: {e}")
                
    if jobs_cleared > 0:
        logger.info(f"Cleared {jobs_cleared} reminders for {sender_id}.")
        return f"✅ Cleared {jobs_cleared} scheduled reminders."
    else:
        return "ℹ️ No active reminders found to clear."

def get_active_reminders() -> list:
    """Returns a list of all active jobs for logging/debugging."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "next_run": job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else "None",
            "trigger": str(job.trigger)
        })
    return jobs

# Start the scheduler when this module is imported
start_scheduler()
