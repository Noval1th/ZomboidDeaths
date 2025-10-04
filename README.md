# Project Zomboid Death Monitor

Automatically track player deaths on your Project Zomboid server and post notifications to Discord with death counts, coordinates, and leaderboards!

![Discord Example](https://img.shields.io/badge/Discord-Webhook-7289DA?style=for-the-badge&logo=discord&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## Features

- 🎮 **Real-time death notifications** - Posts to Discord within 30 seconds of a death
- 📊 **Persistent death tracking** - Tracks total deaths per player across restarts
- 🏆 **Automatic leaderboards** - Posts leaderboards twice daily (noon & midnight) and after active play sessions
- 📍 **Death coordinates** - Shows exact location where each player died
- ⚔️ **Death type detection** - Distinguishes between PVP and environment/zombie deaths
- 💀 **Progressive emojis** - Different emojis based on death count (💀 → ☠️ → ⚰️ → 👻 → 🏴‍☠️)
- 🎨 **Color-coded embeds** - Embed colors change based on death count
- 💻 **Runs locally** - No cloud hosting needed, runs on your own PC

---

## Requirements

- Project Zomboid server with FTP access (tested on G-Portal)
- Discord server with webhook permissions
- Python 3.8 or higher installed
- Windows, Linux, or Mac computer

---

## Quick Start

### 1. Install Python

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer and **CHECK** "Add Python to PATH"
3. Verify: Open Command Prompt and type `python --version`

**Mac:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Download This Repository

**Option A: Using Git**
```bash
git clone https://github.com/Noval1th/ZomboidDeaths.git
cd ZomboidDeaths
```

**Option B: Manual Download**
1. Click the green **"Code"** button at the top of this page
2. Click **"Download ZIP"**
3. Extract the ZIP file to a folder you'll remember (e.g., `C:\zomboid-monitor\`)

### 3. Install Dependencies

Open terminal/command prompt in the project folder:

```bash
pip install -r requirements.txt
```

### 4. Get Your Discord Webhook

1. Go to your Discord server → **Server Settings** → **Integrations** → **Webhooks**
2. Click **"Create Webhook"**
3. Set the name and channel where you want notifications
4. Click **"Copy Webhook URL"** and save it

### 5. Set Up Environment Variables

You'll need your server's FTP credentials. For G-Portal:
1. Go to your server dashboard
2. Click **"FTP"** in the sidebar
3. Copy the Host, Port, Username, and Password

**Windows:**

Create a file called `start_monitor.bat` in the project folder with this content:

```batch
@echo off
set DISCORD_WEBHOOK_URL=your_webhook_url_here
set FTP_HOST=your_ftp_host_here
set FTP_PORT=your_ftp_port_here
set FTP_USER=your_ftp_username_here
set FTP_PASS=your_ftp_password_here
set LOG_BASE_PATH=/Logs
set CHECK_INTERVAL=30

python main.py
pause
```

Replace the `your_*_here` values with your actual credentials.

**Mac/Linux:**

Create a file called `start_monitor.sh`:

```bash
#!/bin/bash
export DISCORD_WEBHOOK_URL="your_webhook_url_here"
export FTP_HOST="your_ftp_host_here"
export FTP_PORT="your_ftp_port_here"
export FTP_USER="your_ftp_username_here"
export FTP_PASS="your_ftp_password_here"
export LOG_BASE_PATH="/Logs"
export CHECK_INTERVAL="30"

python3 main.py
```

Make it executable:
```bash
chmod +x start_monitor.sh
```

### 6. Test It!

**Windows:** Double-click `start_monitor.bat`  
**Mac/Linux:** Run `./start_monitor.sh`

You should see:
```
==================================================
Project Zomboid Death Monitor Started
==================================================
FTP Server: your.server.ip:34231
Log Base Path: /Logs
Check Interval: 30s
Tracking deaths for 0 players
==================================================

Waiting for deaths...
```

Have someone die in your server to test it! Within 30 seconds, you should see a Discord notification.

---

## Auto-Start on PC Boot

### Windows - Using Task Scheduler

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create a New Task**
   - Click **"Create Task..."** (NOT "Create Basic Task")
   - Name it: `Zomboid Death Monitor`
   - Check **"Run whether user is logged on or not"**
   - Check **"Run with highest privileges"**

3. **Triggers Tab**
   - Click **"New..."**
   - Begin the task: **"At startup"**
   - Click **OK**

4. **Actions Tab**
   - Click **"New..."**
   - Action: **"Start a program"**
   - Program/script: `C:\Windows\System32\cmd.exe`
   - Add arguments: `/c "C:\path\to\your\start_monitor.bat"`
   - Replace `C:\path\to\your\` with your actual path
   - Click **OK**

5. **Conditions Tab**
   - Uncheck **"Start the task only if the computer is on AC power"** (for laptops)

6. **Settings Tab**
   - Check **"If the task fails, restart every: 1 minute"**
   - Attempt to restart up to: **3 times**

7. Click **OK** and enter your Windows password if prompted

**To test:** Restart your computer and check Task Scheduler's "Task Status" to verify it's running.

### Mac - Using launchd (NOTE AI Wrote this ENTIRE section with no oversight by me because I don't have access to MacOS to test this process myself)

1. Create a plist file at `~/Library/LaunchAgents/com.zomboid.deathmonitor.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.zomboid.deathmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/your/start_monitor.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/zomboid-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/zomboid-monitor-error.log</string>
</dict>
</plist>
```

2. Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.zomboid.deathmonitor.plist
```

3. Start it:
```bash
launchctl start com.zomboid.deathmonitor
```

### Linux - Using systemd (NOTE AI Wrote this ENTIRE section with no oversight by me because I am too lazy to spin up an entire linux environment just to test this process myself)

1. Create a service file at `/etc/systemd/system/zomboid-monitor.service`:

```ini
[Unit]
Description=Project Zomboid Death Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/zomboid-death-monitor
ExecStart=/usr/bin/python3 /path/to/zomboid-death-monitor/main.py
Environment="DISCORD_WEBHOOK_URL=your_webhook_url"
Environment="FTP_HOST=your_ftp_host"
Environment="FTP_PORT=your_ftp_port"
Environment="FTP_USER=your_ftp_user"
Environment="FTP_PASS=your_ftp_pass"
Environment="LOG_BASE_PATH=/Logs"
Environment="CHECK_INTERVAL=30"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable zomboid-monitor.service
sudo systemctl start zomboid-monitor.service
```

3. Check status:
```bash
sudo systemctl status zomboid-monitor.service
```

---

## Configuration

### Environment Variables

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `DISCORD_WEBHOOK_URL` | Your Discord webhook URL | ✅ Yes | - | `https://discord.com/api/webhooks/...` |
| `FTP_HOST` | Your server's FTP hostname | ✅ Yes | - | `176.57.165.115` |
| `FTP_PORT` | FTP port number | ✅ Yes | - | `34231` |
| `FTP_USER` | FTP username | ✅ Yes | - | `your_username` |
| `FTP_PASS` | FTP password | ✅ Yes | - | `your_password` |
| `LOG_BASE_PATH` | Base path to server logs | ❌ No | `/Logs` | `/Logs` or `/Zomboid/Logs/` |
| `CHECK_INTERVAL` | Seconds between checks | ❌ No | `30` | `30` or `60` |

### Finding Your FTP Credentials

**G-Portal:**
1. Server dashboard → Select the gamecloud server in question
2. On the status page, scroll down to the "Access Data" Section
3. Copy Host, Port, Username, Password

**Other Hosts:**
- Check hosting provider's control panel
- Usually in "File Management" or "Advanced" sections

### Adjusting Check Frequency

Lower values = more real-time (but slightly more resource usage):
```batch
set CHECK_INTERVAL=15  # Check every 15 seconds
```

Higher values = less frequent checks:
```batch
set CHECK_INTERVAL=60  # Check every 60 seconds
```

### Custom Log Path

If your server stores logs elsewhere:
```batch
set LOG_BASE_PATH=/Zomboid/Logs
```

Connect via FTP to explore your server's directory structure.

---

## How It Works

### Death Notifications

When a player dies, the bot posts an embed to Discord:

```
💀 PlayerName has died for the 3rd time!
Total Deaths: 3
📍 Location: (10879, 9446, 0)

🧟 Killed by the environment/zombies
```

The embed color changes based on death count:
- 1 death: Red
- 2-3 deaths: Orange  
- 4-5 deaths: Dark Orange
- 6-10 deaths: Yellow-Orange
- 11+ deaths: Dark Red

### Leaderboards

Leaderboards are posted automatically:

**Scheduled** - Twice daily at 12:00 PM and 12:00 AM
```
💀 Death Leaderboard 💀
🥇 Billy-Wayne: 12 deaths
🥈 Travis-Lee: 8 deaths
🥉 Bobby-Gene: 5 deaths
```

**Activity-Based** - Every ~50 minutes if there have been deaths since the last leaderboard

### Technical Details

- Connects to your server via FTP every 30 seconds (configurable)
- Reads only new content from log files (efficient!)
- Parses death events from Project Zomboid logs
- Tracks file positions to prevent duplicate notifications
- Persists death counts to `death_stats.json`
- Automatically handles log file rotation

---

## Monitoring & Maintenance

### Checking if It's Running

**Windows:**
- Check Task Manager → Details tab → Look for `python.exe`
- Or check Task Scheduler status

**Mac:**
```bash
launchctl list | grep zomboid
```

**Linux:**
```bash
sudo systemctl status zomboid-monitor.service
```

### Viewing Logs

The console window will show all activity:
```
💀 Death detected: PlayerName at (10879, 9446, 0) (Death #3)
✓ Notification sent for PlayerName (Death #3)
```

### Stopping the Bot

**Windows:**
- Close the console window
- Or: Task Scheduler → Right-click task → Disable

**Mac:**
```bash
launchctl stop com.zomboid.deathmonitor
```

**Linux:**
```bash
sudo systemctl stop zomboid-monitor.service
```

### Updating the Bot

1. Download the latest version or pull from Git
2. Restart the bot (or just restart your PC)

---

## Troubleshooting

### Bot not starting

**Check Python installation:**
```bash
python --version
```
Should show Python 3.8 or higher.

**Check dependencies:**
```bash
pip install -r requirements.txt
```

### No notifications appearing

**Check the console for errors:**
- `✗ FTP Error: Connection refused` → Check FTP credentials
- `✗ Failed to send notification` → Check Discord webhook URL
- `⚠️ Could not list files` → Check LOG_BASE_PATH

**Verify FTP access manually:**
- Use FileZilla or another FTP client
- Connect with your credentials
- Browse to `/Logs/` and verify you can see `*_user.txt` files

### Duplicate notifications

- Ensure only ONE instance is running
- Check Task Manager/Activity Monitor for multiple `python.exe` processes

### High CPU/RAM usage

This bot should use almost nothing (<1% CPU, <50MB RAM). If you see high usage:
- Close and restart the bot
- Check for other Python scripts running
- Verify you're running the correct script

### Bot stops after closing terminal

- Make sure you set up auto-start (see above)
- On Windows, Task Scheduler should keep it running in background
- Don't run from terminal if you want it persistent - use the batch file with Task Scheduler

---

## Project Structure

```
zomboid-death-monitor/
├── main.py              # Main bot script
├── requirements.txt     # Python dependencies  
├── README.md           # This file
├── .gitignore          # Git ignore rules
├── LICENSE             # MIT License
├── start_monitor.bat   # Windows startup script (you create this)
├── start_monitor.sh    # Mac/Linux startup script (you create this)
└── death_stats.json    # Generated by bot (death counts & positions)
```

---

## Power & Cost

### Typical Power Usage
- Idle PC with bot: ~50-100W
- Cost per month: $5-15 (depending on electricity rates)
- Way cheaper than cloud hosting ($7-20/month)

### Is It Safe to Leave My PC On?
**Yes!** Modern PCs are designed for 24/7 operation:
- ✅ Components are rated for continuous use
- ✅ Idle power usage is minimal
- ✅ Most components sleep/throttle when not in use
- ✅ Gaming puts more stress on hardware than running idle

**Tips:**
- Clean dust from your PC every few months
- Ensure good airflow/cooling
- Consider a UPS for power outage protection

---

## FAQ

**Q: Does this require any server-side mods?**  
A: No! It only reads log files via FTP.

**Q: Will this work with other hosting providers?**  
A: Yes, as long as you have FTP access to the logs.

**Q: Can I run this on a Raspberry Pi?**  
A: Yes! Follow the Linux instructions.

**Q: Does it use a lot of internet bandwidth?**  
A: Very minimal - it only downloads new log content (usually just a few KB per check).

**Q: What if my PC restarts?**  
A: If you set up auto-start, the bot will automatically resume.

**Q: Can I run multiple instances for different servers?**  
A: Yes! Just create separate folders with different configuration files.

**Q: Does it track deaths across server wipes?**  
A: Yes, death counts persist in `death_stats.json` until you delete it.

**Q: Can I customize the Discord messages?**  
A: Yes! Edit the `send_discord_notification()` and `send_leaderboard()` functions in `main.py`.

**Q: What if I want to reset the death counts?**  
A: Delete the `death_stats.json` file.

**Q: Can I host this on a VPS or cloud server instead?**  
A: Yes! Just follow the Linux systemd instructions on your VPS.

---

## Contributing

Contributions are welcome! Ideas:

- [ ] Support for additional log formats
- [ ] Web dashboard for viewing stats
- [ ] Configurable leaderboard schedules
- [ ] Player stats tracking (survival time, kill counts)
- [ ] Multiple Discord channel support

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

MIT License - See LICENSE file for details

---

## Support

Having issues?

1. **Check the console output** - Most issues show error messages
2. **Review troubleshooting section** - Common fixes are documented above
3. **Open an issue** - Include error messages and your configuration (minus passwords!)
4. **Check discussions** - Someone may have had the same problem

---

**Made with 💀 for the Project Zomboid community**

*Stay alive out there... or don't. We're tracking either way.*
