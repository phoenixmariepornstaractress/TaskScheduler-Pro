#
import schedule
import time
import logging
import signal
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Configuration
class Config:
    LOG_FILE = os.getenv('SCHEDULER_LOG_FILE', 'scheduler.log')
    LOG_FORMAT = os.getenv('SCHEDULER_LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
    LOG_MAX_BYTES = int(os.getenv('SCHEDULER_LOG_MAX_BYTES', 10**6))  # 1MB default
    LOG_BACKUP_COUNT = int(os.getenv('SCHEDULER_LOG_BACKUP_COUNT', 5))  # 5 backup files
    SHUTDOWN_GRACE_PERIOD = int(os.getenv('SCHEDULER_SHUTDOWN_GRACE_PERIOD', 5))  # 5 seconds

# Logging setup
def setup_logging():
    """Set up logging with a rotating file handler."""
    file_handler = RotatingFileHandler(Config.LOG_FILE, maxBytes=Config.LOG_MAX_BYTES, backupCount=Config.LOG_BACKUP_COUNT)
    file_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
    return logging.getLogger(__name__)

logger = setup_logging()

# Signal Handling
shutdown_flag = False

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_flag
    logger.info("Received shutdown signal (SIGINT or SIGTERM)...")
    shutdown_flag = True

    # Wait for a grace period before exiting
    logger.info(f"Waiting for {Config.SHUTDOWN_GRACE_PERIOD} seconds before shutdown...")
    time.sleep(Config.SHUTDOWN_GRACE_PERIOD)
    logger.info("Shutdown complete.")
    sys.exit(0)

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

# Task Definitions
def task_morning():
    logger.info("Good morning! Time to start the day with some coffee.")

def task_afternoon():
    logger.info("Good afternoon! Time for a quick walk.")

def task_evening():
    logger.info("Good evening! Time to wind down and relax.")

def task_midnight():
    logger.info("It's midnight! Time to review your day and plan for tomorrow.")

def task_interval():
    logger.info("This is a recurring task running every 10 minutes.")
    
def task_weekly():
    logger.info("This is your weekly Monday 9:00 AM reminder.")

# Scheduler Setup
def log_scheduled_tasks():
    """Log all currently scheduled tasks."""
    logger.info("Scheduled tasks:")
    for job in schedule.get_jobs():
        logger.info(f" - {job}")

def setup_schedule():
    """Set up the scheduled tasks."""
    # Daily tasks
    schedule.every().day.at("08:00").do(task_morning)
    schedule.every().day.at("12:00").do(task_afternoon)
    schedule.every().day.at("18:00").do(task_evening)
    schedule.every().day.at("00:00").do(task_midnight)

    # Recurring tasks
    schedule.every(10).minutes.do(task_interval)

    # Weekly tasks
    schedule.every().monday.at("09:00").do(task_weekly)

    # Log the tasks
    log_scheduled_tasks()

# Scheduler Execution
def run_scheduler():
    """Run the scheduler and process tasks."""
    global shutdown_flag
    while not shutdown_flag:
        schedule.run_pending()
        time.sleep(1)

    logger.info("Scheduler is shutting down...")

# Main Execution
def main():
    """Main entry point for the script."""
    setup_signal_handlers()
    logger.info("Setting up the scheduler...")
    setup_schedule()
    logger.info("Scheduler started successfully!")
    run_scheduler()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Scheduler encountered an unexpected error: %s", str(e))
