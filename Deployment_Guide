# Project Zomboid Death Monitor

Automatically track player deaths on your Project Zomboid server and post notifications to Discord with death counts, coordinates, and leaderboards!

![Discord Example](https://img.shields.io/badge/Discord-Webhook-7289DA?style=for-the-badge&logo=discord&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## Features

- 🎮 **Real-time death notifications** - Posts to Discord within 30 seconds of a death
- 📊 **Persistent death tracking** - Tracks total deaths per player across server restarts
- 🏆 **Automatic leaderboards** - Posts leaderboards twice daily (noon & midnight) and after active play sessions
- 📍 **Death coordinates** - Shows exact location where each player died
- ⚔️ **Death type detection** - Distinguishes between PVP and environment/zombie deaths
- 💀 **Progressive emojis** - Different emojis based on death count (💀 → ☠️ → ⚰️ → 👻 → 🏴‍☠️)
- 🎨 **Color-coded embeds** - Embed colors change based on death count
- 🔄 **Zero maintenance** - Runs 24/7 on free cloud hosting

---

## Requirements

- Project Zomboid server with FTP access (tested on G-Portal)
- Discord server with webhook permissions
- GitHub account (for deployment)
- Render.com account (free tier is sufficient)

---

## Quick Start

### 1. Get Your Discord Webhook

1. Go to your Discord server → **Server Settings** → **Integrations** → **Webhooks**
2. Click **"Create Webhook"**
3. Set the name and channel where you want notifications
4. Click **"Copy Webhook URL"** and save it

### 2. Deploy to Render.com

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

1. **Fork this repository** to your GitHub account
2. Sign up/login to [Render.com](https://render.com)
3. Click **"New +"** → **"Background Worker"**
4. Connect your GitHub account and select this repository
5. Configure the service:
   - **Name**: `zomboid-death-monitor`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`

### 3. Add Environment Variables

In Render's Environment section, add these variables:

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DISCORD_WEBHOOK_URL` | Your Discord webhook URL | ✅ Yes | `https://discord.com/api/webhooks/...` |
| `FTP_HOST` | Your server's FTP hostname | ✅ Yes | `176.57.165.115` |
| `FTP_PORT` | FTP port number | ✅ Yes | `34231` |
| `FTP_USER` | FTP username | ✅ Yes | `your_ftp_username` |
| `FTP_PASS` | FTP password | ✅ Yes | `your_ftp_password` |
| `LOG_BASE_PATH` | Base path to server logs | ❌ No | `/Logs` (default) |
| `CHECK_INTERVAL` | Seconds between checks | ❌ No | `30` (default) |

### 4. Deploy!

Click **"Create Background Worker"** and Render will deploy your bot. Check the logs to verify it's working.

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

- Connects to your server via FTP every 30 seconds
- Reads only new content from log files (efficient!)
- Parses death events from Project Zomboid logs
- Tracks file positions to prevent duplicate notifications
- Persists death counts to `death_stats.json`
- Automatically handles log file rotation

---

## Configuration

### Finding Your FTP Credentials

**G-Portal:**
1. Go to your server dashboard
2. Click **"FTP"** in the sidebar
3. Copy the Host, Port, Username, and Password

**Other Hosts:**
- Check your hosting provider's control panel
- FTP access is usually in "File Management" or "Advanced" sections

### Adjusting Check Frequency

To check logs more or less frequently:
```bash
CHECK_INTERVAL=60  # Check every 60 seconds instead of 30
```

Lower values = more real-time, but uses slightly more resources

### Custom Log Path

If your server stores logs in a different location:
```bash
LOG_BASE_PATH=/path/to/logs
```

Common paths:
- `/Logs/` (default, works for most servers)
- `/Zomboid/Logs/`
- `/server/logs/`

Connect via FTP to explore your server's directory structure.

---

## Monitoring & Maintenance

### Viewing Logs

Check if the bot is working:
1. Go to your Render dashboard
2. Click on your service
3. Click the **"Logs"** tab

You should see:
```
==================================================
Project Zomboid Death Monitor Started
==================================================
FTP Server: 176.57.165.115:34231
Log Base Path: /Logs
Check Interval: 30s
Tracking deaths for 5 players
==================================================

Waiting for deaths...
```

### Updating the Bot

To update the code:
1. Edit files in your GitHub repository
2. Commit and push changes
3. Render automatically detects and redeploys

### Service Status

- Render's free tier provides 750 hours/month (enough for 24/7)
- The service automatically restarts if it crashes
- Death counts persist across restarts

---

## Troubleshooting

### No notifications appearing

**Check Render logs for errors:**
```
✗ FTP Error: [Errno 111] Connection refused
```

**Solutions:**
- Verify FTP credentials are correct
- Check that FTP access is enabled on your server
- Ensure your IP isn't blocked by firewall

### Wrong log format detected

If the regex isn't matching your logs:
1. Connect to FTP and download a sample log file
2. Look for lines containing "died at"
3. Open an issue with the log format so we can update the parser

### Duplicate notifications

- Ensure only ONE instance is running
- Check that you haven't deployed multiple times
- The bot should automatically prevent duplicates

### Missing deaths

- Verify `LOG_BASE_PATH` points to the correct folder
- Check that log files are named `*_user.txt`
- Increase `CHECK_INTERVAL` if needed

---

## Example Discord Output

### Death Notification
> 💀 **xCATZx has died for the 1st time!**
> **Total Deaths: 1**
> 📍 Location: (10879, 9446, 0)
> 
> 🧟 Killed by the environment/zombies

### Leaderboard
> 💀 **Death Leaderboard** 💀
> 🥇 Billy-Wayne: **12** deaths
> 🥈 Travis-Lee: **8** deaths
> 🥉 Bobby-Gene: **5** deaths
> **4.** Jimmy-Dale: **3** deaths
> **5.** Dale-Ray: **2** deaths
> 
> Total tracked players: 15

---

## Project Structure

```
zomboid-death-monitor/
├── main.py              # Main bot script
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── death_stats.json    # Generated by bot (death counts & file positions)
```

---

## Technical Stack

- **Python 3.8+** - Core language
- **ftplib** - FTP connection and file retrieval
- **requests** - Discord webhook integration
- **regex** - Log parsing
- **Render.com** - Free cloud hosting

---

## Contributing

Contributions are welcome! Here are some ideas:

- [ ] Add more death cause detection (starvation, dehydration, falls)
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

## FAQ

**Q: Does this require any server-side mods?**  
A: No! It only reads log files via FTP.

**Q: Will this work with other hosting providers?**  
A: Yes, as long as you have FTP access to the logs.

**Q: Does it cost money?**  
A: No, Render's free tier is sufficient for 24/7 operation.

**Q: Can I run this on my own hardware?**  
A: Yes! Just run `python main.py` with the environment variables set.

**Q: What if my server has multiple log files?**  
A: The bot automatically finds and processes all `*_user.txt` files.

**Q: Does it track deaths across server wipes?**  
A: Yes, death counts persist in `death_stats.json` until you delete it.

**Q: Can I customize the Discord messages?**  
A: Yes! Edit the `send_discord_notification()` and `send_leaderboard()` functions in `main.py`.

**Q: What about player name changes?**  
A: Death counts are tied to the exact name in logs. Name changes will create a new entry.

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- Project Zomboid by The Indie Stone
- Discord for webhook API
- Render.com for free hosting

---

## Support

Having issues? Here's how to get help:

1. **Check the logs** - Most issues show up in Render's logs
2. **Review troubleshooting section** - Common fixes are documented above
3. **Open an issue** - Include error logs and your configuration (minus passwords!)
4. **Check discussions** - Someone may have had the same problem

---

**Made with 💀 for the Project Zomboid community**

*Stay alive out there... or don't. We're tracking either way.*
