import os
import sys
import platform
import time
import datetime
import webbrowser
import subprocess

import speech_recognition as sr
import pyttsx3

SYSTEM = platform.system()

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    HAS_PYCAW = SYSTEM == "Windows"
except ImportError:
    HAS_PYCAW = False

try:
    import screen_brightness_control as sbc
    HAS_BRIGHTNESS = True
except ImportError:
    HAS_BRIGHTNESS = False

engine = pyttsx3.init()
engine.setProperty("rate", 175)

def speak(text: str):
    print(f"[Agent] {text}")
    engine.say(text)
    engine.runAndWait()

def shutdown_pc():
    if SYSTEM == "Windows":
        os.system("shutdown /s /t 10")
    elif SYSTEM == "Linux":
        os.system("shutdown -h +0.17")
    elif SYSTEM == "Darwin":
        os.system("sudo shutdown -h +0")
    speak("Shutting down in 10 seconds. Say cancel shutdown to stop it.")

def cancel_shutdown():
    if SYSTEM == "Windows":
        os.system("shutdown /a")
    elif SYSTEM == "Linux":
        os.system("shutdown -c")
    speak("Shutdown cancelled.")

def restart_pc():
    if SYSTEM == "Windows":
        os.system("shutdown /r /t 10")
    elif SYSTEM == "Linux":
        os.system("shutdown -r +0.17")
    elif SYSTEM == "Darwin":
        os.system("sudo shutdown -r +0")
    speak("Restarting in 10 seconds. Say cancel shutdown to stop it.")

def lock_pc():
    if SYSTEM == "Windows":
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif SYSTEM == "Linux":
        os.system("xdg-screensaver lock")
    elif SYSTEM == "Darwin":
        os.system("pmset displaysleepnow")
    speak("Screen locked.")

def sleep_pc():
    if SYSTEM == "Windows":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif SYSTEM == "Linux":
        os.system("systemctl suspend")
    elif SYSTEM == "Darwin":
        os.system("pmset sleepnow")
    speak("Going to sleep.")

APPS = {
    "notepad": {"Windows": "notepad.exe", "Linux": "gedit", "Darwin": "open -a TextEdit"},
    "calculator": {"Windows": "calc.exe", "Linux": "gnome-calculator", "Darwin": "open -a Calculator"},
    "file explorer": {"Windows": "explorer.exe", "Linux": "nautilus", "Darwin": "open ."},
    "browser": {"Windows": "start chrome", "Linux": "xdg-open http://google.com", "Darwin": "open -a Safari"},
    "task manager": {"Windows": "taskmgr.exe", "Linux": "gnome-system-monitor", "Darwin": "open -a 'Activity Monitor'"},
    "command prompt": {"Windows": "start cmd", "Linux": "gnome-terminal", "Darwin": "open -a Terminal"},
    "settings": {"Windows": "start ms-settings:", "Linux": "gnome-control-center", "Darwin": "open -a 'System Preferences'"},
}

def open_app(name: str):
    cmd = APPS.get(name, {}).get(SYSTEM)
    if cmd:
        os.system(cmd)
        speak(f"Opening {name}.")
    else:
        speak(f"I don't have {name} mapped for this OS.")

def open_website(url: str, spoken_name: str):
    webbrowser.open(url)
    speak(f"Opening {spoken_name}.")

def _get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def volume_up():
    if not HAS_PYCAW:
        speak("Volume control isn't available on this OS in this script.")
        return
    vol = _get_volume_interface()
    level = min(vol.GetMasterVolumeLevelScalar() + 0.1, 1.0)
    vol.SetMasterVolumeLevelScalar(level, None)
    speak("Volume up.")

def volume_down():
    if not HAS_PYCAW:
        speak("Volume control isn't available on this OS in this script.")
        return
    vol = _get_volume_interface()
    level = max(vol.GetMasterVolumeLevelScalar() - 0.1, 0.0)
    vol.SetMasterVolumeLevelScalar(level, None)
    speak("Volume down.")

def mute_volume():
    if not HAS_PYCAW:
        speak("Volume control isn't available on this OS in this script.")
        return
    vol = _get_volume_interface()
    vol.SetMute(1, None)
    speak("Muted.")

def unmute_volume():
    if not HAS_PYCAW:
        speak("Volume control isn't available on this OS in this script.")
        return
    vol = _get_volume_interface()
    vol.SetMute(0, None)
    speak("Unmuted.")

def brightness_up():
    if not HAS_BRIGHTNESS:
        speak("Brightness control isn't available.")
        return
    try:
        current = sbc.get_brightness()[0]
        sbc.set_brightness(min(current + 10, 100))
        speak("Brightness increased.")
    except Exception:
        speak("Couldn't change brightness on this device.")

def brightness_down():
    if not HAS_BRIGHTNESS:
        speak("Brightness control isn't available.")
        return
    try:
        current = sbc.get_brightness()[0]
        sbc.set_brightness(max(current - 10, 0))
        speak("Brightness decreased.")
    except Exception:
        speak("Couldn't change brightness on this device.")

def take_screenshot():
    try:
        from PIL import ImageGrab
        folder = os.path.join(os.path.expanduser("~"), "Pictures", "VoiceAgentScreenshots")
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, f"screenshot_{int(time.time())}.png")
        img = ImageGrab.grab()
        img.save(filename)
        speak(f"Screenshot saved to {folder}.")
    except ImportError:
        speak("Screenshot needs the Pillow package. Install it with pip install Pillow.")
    except Exception as e:
        speak("Couldn't take a screenshot.")
        print(f"[Error] {e}")

def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"It's {now}.")

def tell_date():
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")
    speak(f"Today is {today}.")

def battery_status():
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            plugged = "and it's charging" if battery.power_plugged else "and it's not charging"
            speak(f"Battery is at {battery.percent} percent, {plugged}.")
        else:
            speak("No battery detected — this looks like a desktop.")
    except ImportError:
        speak("Battery status needs the psutil package. Install it with pip install psutil.")

def web_search(query: str):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    speak(f"Searching the web for {query}.")

SIMPLE_COMMANDS = {
    "system shutdown": (shutdown_pc, True),
    "shut down": (shutdown_pc, True),
    "cancel shutdown": (cancel_shutdown, False),
    "system restart": (restart_pc, True),
    "restart": (restart_pc, True),
    "lock screen": (lock_pc, False),
    "lock": (lock_pc, False),
    "sleep": (sleep_pc, False),

    "open notepad": (lambda: open_app("notepad"), False),
    "open calculator": (lambda: open_app("calculator"), False),
    "open file explorer": (lambda: open_app("file explorer"), False),
    "open browser": (lambda: open_app("browser"), False),
    "open task manager": (lambda: open_app("task manager"), False),
    "open command prompt": (lambda: open_app("command prompt"), False),
    "open settings": (lambda: open_app("settings"), False),

    "open youtube": (lambda: open_website("https://youtube.com", "YouTube"), False),
    "open gmail": (lambda: open_website("https://gmail.com", "Gmail"), False),
    "open whatsapp": (lambda: open_app("WhatsApp"), False),

    "volume up": (volume_up, False),
    "volume down": (volume_down, False),
    "mute": (mute_volume, False),
    "unmute": (unmute_volume, False),

    "brightness up": (brightness_up, False),
    "brightness down": (brightness_down, False),

    "take screenshot": (take_screenshot, False),
    "screenshot": (take_screenshot, False),

    "what time is it": (tell_time, False),
    "what's the time": (tell_time, False),
    "what's the date": (tell_date, False),
    "battery status": (battery_status, False),
    "battery level": (battery_status, False),
}

EXIT_PHRASES = {"stop listening", "exit agent", "quit agent"}
HELP_PHRASES = {"help", "what can you do", "list commands"}

def print_help():
    print("\n=== Available voice commands ===")
    for phrase in sorted(SIMPLE_COMMANDS.keys()):
        print(f"  - {phrase}")
    print("  - search for <anything>   (web search)")
    print("  - stop listening           (exit)")
    print("================================\n")

def confirm(recognizer, mic) -> bool:
    speak("Are you sure? Say yes to confirm.")
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
        reply = recognizer.recognize_google(audio).lower()
        print(f"[Heard] {reply}")
        return "yes" in reply
    except Exception:
        return False

def main():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print_help()
    speak("Voice agent ready. Say help to hear the command list.")

    while True:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("[Listening...]")
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)

            text = recognizer.recognize_google(audio).lower().strip()
            print(f"[Heard] {text}")

            if text in EXIT_PHRASES:
                speak("Exiting voice agent. Goodbye.")
                break

            if text in HELP_PHRASES:
                print_help()
                speak("Here's the command list, printed in the terminal.")
                continue

            if text.startswith("search for "):
                query = text.replace("search for ", "", 1)
                web_search(query)
                continue

            matched = False
            for phrase, (action, needs_confirm) in SIMPLE_COMMANDS.items():
                if phrase in text:
                    matched = True
                    if needs_confirm:
                        if confirm(recognizer, mic):
                            action()
                        else:
                            speak("Cancelled.")
                    else:
                        action()
                    break

            if not matched:
                print("[Agent] Command not recognized. Say 'help' for the list.")

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"[Error] Speech service unavailable: {e}")
            time.sleep(2)
        except KeyboardInterrupt:
            speak("Agent stopped.")
            break

if __name__ == "__main__":
    main()
