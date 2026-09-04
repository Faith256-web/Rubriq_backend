# backup_db.py
import os
import shutil
from datetime import datetime

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "app.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

def run_backup():
    print("🤖 Starting Rubriq Africa Database Backup...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database file not found at {DB_PATH}")
        return False
        
    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"app_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_file)
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Success! Database backed up successfully.")
        print(f"📁 Backup file path: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Error performing backup: {e}")
        return False

if __name__ == "__main__":
    run_backup()
