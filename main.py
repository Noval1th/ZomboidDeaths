import os
import time
import ftplib
import re
import requests
import json
from datetime import datetime, timedelta
from io import BytesIO
from collections import defaultdict

# Configuration - Set these as environment variables
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
FTP_HOST = os.getenv('FTP_HOST')
FTP_PORT = int(os.getenv('FTP_PORT', '34231'))
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')
LOG_BASE_PATH = os.getenv('LOG_BASE_PATH', '/Logs')  # Base logs directory
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '30'))  # seconds
DEATH_STATS_FILE = 'death_stats.json'

# Track last processed position per file
file_positions = {}
last_deaths = set()  # Prevent duplicate notifications
death_counts = defaultdict(int)  # Track deaths per player

def load_death_stats():
    """Load death statistics from file"""
    global death_counts, file_positions
    try:
        if os.path.exists(DEATH_STATS_FILE):
            with open(DEATH_STATS_FILE, 'r') as f:
                data = json.load(f)
                death_counts = defaultdict(int, data.get('death_counts', {}))
                file_positions = data.get('file_positions', {})
            print(f"✓ Loaded death stats: {len(death_counts)} players tracked")
    except Exception as e:
        print(f"⚠️ Could not load death stats: {e}")
        death_counts = defaultdict(int)
        file_positions = {}

def save_death_stats():
    """Save death statistics to file"""
    try:
        with open(DEATH_STATS_FILE, 'w') as f:
            json.dump({
                'death_counts': dict(death_counts),
                'file_positions': file_positions
            }, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save death stats: {e}")

def get_death_ordinal(count):
    """Convert death count to ordinal (1st, 2nd, 3rd, etc.)"""
    if 10 <= count % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(count % 10, 'th')
    return f"{count}{suffix}"

def get_death_emoji(count):
    """Get emoji based on death count"""
    if count == 1:
        return "💀"
    elif count <= 3:
        return "☠️"
    elif count <= 5:
        return "⚰️"
    elif count <= 10:
        return "👻"
    else:
        return "🏴‍☠️"

def send_discord_notification(player_name, details, death_count, coordinates):
    """Send death notification to Discord with death count"""
    
    ordinal = get_death_ordinal(death_count)
    emoji = get_death_emoji(death_count)
    
    # Build title with death count
    title = f"{emoji} {player_name} has died for the {ordinal} time!"
    
    # Add death count and coordinates to details
    full_details = f"**Total Deaths: {death_count}**\n📍 Location: {coordinates}\n\n{details}"
    
    # Choose color based on death count
    if death_count == 1:
        color = 0xFF0000  # Red
    elif death_count <= 3:
        color = 0xFF6600  # Orange
    elif death_count <= 5:
        color = 0xFF9900  # Dark orange
    elif death_count <= 10:
        color = 0xFFCC00  # Yellow-orange
    else:
        color = 0x990000  # Dark red
    
    embed = {
        "title": title,
        "description": full_details,
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "Project Zomboid Death Logger"
        }
    }
    
    payload = {
        "username": "Zomboid Deaths",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code in [200, 204]:
            print(f"✓ Notification sent for {player_name} (Death #{death_count})")
            return True
        else:
            print(f"✗ Failed to send notification: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error sending notification: {e}")
        return False

def send_leaderboard(top_n=10):
    """Send a death leaderboard to Discord"""
    if not death_counts:
        return
    
    # Sort players by death count
    sorted_deaths = sorted(death_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    # Build leaderboard text
    leaderboard_lines = []
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (player, deaths) in enumerate(sorted_deaths):
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        leaderboard_lines.append(f"{medal} {player}: **{deaths}** death{'s' if deaths != 1 else ''}")
    
    leaderboard_text = "\n".join(leaderboard_lines)
    
    embed = {
        "title": "💀 Death Leaderboard 💀",
        "description": leaderboard_text,
        "color": 0x9900FF,  # Purple
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": f"Total tracked players: {len(death_counts)}"
        }
    }
    
    payload = {
        "username": "Zomboid Deaths",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code in [200, 204]:
            print(f"✓ Leaderboard sent")
            return True
        else:
            print(f"✗ Failed to send leaderboard: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error sending leaderboard: {e}")
        return False

def parse_death_from_log(line):
    """
    Parse death information from log line
    Example: [02-10-25 19:32:30.600] user xCATZx died at (10879,9446,0) (non pvp).
    Note: Username can contain spaces, so we use .+? (non-greedy match) instead of \S+
    """
    # Pattern for Project Zomboid death logs
    pattern = r'\[.*?\]\s+user\s+(.+?)\s+died\s+at\s+\((\d+),(\d+),(\d+)\)\s+\((.*?)\)'
    
    match = re.search(pattern, line)
    if match:
        player_name = match.group(1)
        x = match.group(2)
        y = match.group(3)
        z = match.group(4)
        death_type = match.group(5)
        
        coordinates = f"({x}, {y}, {z})"
        
        # Determine death details based on type
        details = []
        
        if "pvp" in death_type.lower() and "non" not in death_type.lower():
            details.append("⚔️ Killed in PVP combat")
        elif "non pvp" in death_type.lower():
            details.append("🧟 Killed by the environment/zombies")
        
        details_text = "\n".join(details) if details else "💀 Met their demise"
        
        return player_name, details_text, coordinates
    
    return None, None, None

def get_log_folders_to_check(ftp):
    """
    Get list of log folders to check
    First checks /Logs/ directly, then falls back to most recent logs_DD-MM folder
    """
    folders = []
    
    # First priority: Check /Logs/ directly (active logs)
    folders.append("")  # Empty string means just /Logs/
    
    # Second priority: Find the most recent archived logs_DD-MM folder
    try:
        ftp.cwd(LOG_BASE_PATH)
        all_items = ftp.nlst()
        
        # Filter for logs_DD-MM folders
        log_folders = [item for item in all_items if item.startswith('logs_') and '-' in item]
        
        if log_folders:
            # Sort to get most recent (this works because DD-MM format sorts correctly within a month)
            log_folders.sort(reverse=True)
            most_recent = log_folders[0]
            folders.append(most_recent)
            print(f"ℹ️ Found archived log folder: {most_recent}")
    
    except Exception as e:
        print(f"⚠️ Could not list archived log folders: {e}")
        # Fallback: Try today's and yesterday's folder names
        today = datetime.now()
        folders.append(f"logs_{today.strftime('%d-%m')}")
        yesterday = today - timedelta(days=1)
        folders.append(f"logs_{yesterday.strftime('%d-%m')}")
    
    return folders

def list_user_logs_in_folder(ftp, folder_path):
    """List all *_user.txt files in a specific log folder"""
    try:
        files = []
        ftp.cwd(folder_path)
        file_list = ftp.nlst()
        
        for filename in file_list:
            if filename.endswith('_user.txt'):
                files.append(filename)
        
        return sorted(files)  # Sort to process in chronological order
    except Exception as e:
        print(f"⚠️ Could not list files in {folder_path}: {e}")
        return []

def download_log_tail(ftp, log_path, from_position=0):
    """Download the log file from FTP starting from last position"""
    try:
        # Get file size
        file_size = ftp.size(log_path)
        
        if file_size is None:
            print(f"✗ Could not determine size of {log_path}")
            return None, from_position
        
        # If file was rotated (smaller than last position), start from beginning
        if file_size < from_position:
            from_position = 0
            print(f"ℹ️ Log file {log_path} rotated, starting from beginning")
        
        # If no new content, return
        if file_size == from_position:
            return "", from_position
        
        # Download from last position
        buffer = BytesIO()
        ftp.retrbinary(f'RETR {log_path}', buffer.write, rest=from_position)
        
        content = buffer.getvalue().decode('utf-8', errors='ignore')
        new_position = file_size
        
        return content, new_position
        
    except Exception as e:
        print(f"✗ Error reading {log_path}: {e}")
        return None, from_position

def monitor_server():
    """Main monitoring loop"""
    global last_deaths, file_positions
    
    # Load existing death statistics
    load_death_stats()
    
    print("=" * 50)
    print("Project Zomboid Death Monitor Started")
    print("=" * 50)
    print(f"FTP Server: {FTP_HOST}:{FTP_PORT}")
    print(f"Log Base Path: {LOG_BASE_PATH}")
    print(f"Check Interval: {CHECK_INTERVAL}s")
    print(f"Discord Webhook: {DISCORD_WEBHOOK_URL[:30]}...")
    print(f"Tracking deaths for {len(death_counts)} players")
    print("=" * 50)
    print("\nWaiting for deaths...\n")
    
    consecutive_errors = 0
    max_errors = 5
    check_count = 0
    leaderboard_check_interval = 100  # Check every 100 cycles
    deaths_since_last_leaderboard = False
    last_daily_leaderboard_date = None
    
    while True:
        try:
            # Connect to FTP
            ftp = ftplib.FTP()
            ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
            ftp.login(FTP_USER, FTP_PASS)
            
            # Get folders to check (active logs first, then most recent archive)
            log_folders = get_log_folders_to_check(ftp)
            
            for folder_name in log_folders:
                # Build full path (empty string means just base path)
                folder_path = f"{LOG_BASE_PATH}/{folder_name}" if folder_name else LOG_BASE_PATH
                
                try:
                    # Get list of user log files in this folder
                    user_logs = list_user_logs_in_folder(ftp, folder_path)
                    
                    for log_filename in user_logs:
                        log_path = f"{folder_path}/{log_filename}"
                        
                        # Get last position for this file
                        last_pos = file_positions.get(log_path, 0)
                        
                        # Download new content
                        new_content, new_pos = download_log_tail(ftp, log_path, last_pos)
                        
                        if new_content:
                            consecutive_errors = 0  # Reset error counter
                            file_positions[log_path] = new_pos
                            
                            lines = new_content.split('\n')
                            
                            for line in lines:
                                if not line.strip():
                                    continue
                                
                                player_name, details, coordinates = parse_death_from_log(line)
                                
                                if player_name:
                                    # Create unique death identifier
                                    death_id = f"{player_name}_{coordinates}_{datetime.now().strftime('%Y%m%d%H%M')}"
                                    
                                    if death_id not in last_deaths:
                                        # Increment death count
                                        death_counts[player_name] += 1
                                        current_deaths = death_counts[player_name]
                                        
                                        print(f"💀 Death detected: {player_name} at {coordinates} (Death #{current_deaths})")
                                        
                                        if send_discord_notification(player_name, details, current_deaths, coordinates):
                                            last_deaths.add(death_id)
                                            deaths_since_last_leaderboard = True  # Mark that we had a death
                                            save_death_stats()
                                            
                                            # Keep only last 200 deaths in memory
                                            if len(last_deaths) > 200:
                                                last_deaths = set(list(last_deaths)[-200:])
                
                except Exception as e:
                    print(f"⚠️ Error processing folder {folder_path}: {e}")
                    continue
            
            ftp.quit()
            
            # Check for daily leaderboard at noon (12:00) or midnight (00:00)
            current_time = datetime.now()
            current_date = current_time.date()
            current_hour = current_time.hour
            current_minute = current_time.minute
            
            # Send daily leaderboard at noon or midnight (within first minute of the hour)
            if current_minute == 0 and last_daily_leaderboard_date != current_date:
                if current_hour == 12 or current_hour == 0:
                    if death_counts:
                        print(f"\n📊 Sending scheduled {'noon' if current_hour == 12 else 'midnight'} leaderboard...")
                        send_leaderboard()
                        last_daily_leaderboard_date = current_date
                        deaths_since_last_leaderboard = False
            
            # Activity-based leaderboard: every 100 checks IF there have been deaths
            check_count += 1
            if check_count % leaderboard_check_interval == 0:
                if deaths_since_last_leaderboard and death_counts:
                    print(f"\n📊 Sending activity-based leaderboard (after {leaderboard_check_interval} checks)...")
                    send_leaderboard()
                    deaths_since_last_leaderboard = False
            
            # Save stats periodically
            if check_count % 10 == 0:
                save_death_stats()
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\nStopping death monitor...")
            save_death_stats()
            break
        except Exception as e:
            consecutive_errors += 1
            print(f"✗ Unexpected error: {e}")
            if consecutive_errors >= max_errors:
                print(f"⚠️ Too many errors, waiting longer before retry...")
                time.sleep(CHECK_INTERVAL * 3)
                consecutive_errors = 0
            else:
                time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # Validate required configuration
    required_vars = {
        'DISCORD_WEBHOOK_URL': DISCORD_WEBHOOK_URL,
        'FTP_HOST': FTP_HOST,
        'FTP_USER': FTP_USER,
        'FTP_PASS': FTP_PASS
    }
    
    missing_vars = [name for name, value in required_vars.items() if not value]
    
    if missing_vars:
        print("❌ ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these environment variables before running.")
        exit(1)
    
    monitor_server()
