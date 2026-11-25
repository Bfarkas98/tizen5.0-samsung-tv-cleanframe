"""Persistent TV shell state and local appliance capabilities."""
import json
import os
import platform
import re
import subprocess
import shutil
import socket
from pathlib import Path
from tempfile import NamedTemporaryFile

VERSION = "0.2.0"
MEDIA_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".mp3", ".flac", ".ogg", ".wav"}


class Preferences:
    def __init__(self, path):
        self.path = path
        self.warning = ""
        self.reset()
        try:
            with path.open(encoding="utf-8") as stream:
                data = json.load(stream)
            if not isinstance(data, dict) or data.get("version") != 1:
                raise ValueError("Unknown settings format")
            for field in ("favorites", "folders"):
                values = data.get(field)
                if isinstance(values, list):
                    setattr(self, field, list(dict.fromkeys(x for x in values if isinstance(x, str)))[:100])
            self.wallpaper = data.get("wallpaper") is not False
            self.resume = data.get("resume") is not False
        except FileNotFoundError:
            pass
        except (OSError, ValueError, RecursionError):
            self.warning = "Settings could not be read. Defaults are in use."

    def reset(self):
        self.favorites = []
        self.folders = []
        self.wallpaper = True
        self.resume = True

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = None
        try:
            with NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent, delete=False) as stream:
                temp = Path(stream.name)
                json.dump({"version": 1, "favorites": self.favorites, "folders": self.folders,
                           "wallpaper": self.wallpaper, "resume": self.resume}, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, self.path)
            self.warning = ""
        finally:
            if temp is not None:
                temp.unlink(missing_ok=True)

    def favorite(self, entry, shift=0):
        if shift:
            index = self.favorites.index(entry)
            other = index + shift
            if 0 <= other < len(self.favorites):
                self.favorites[index], self.favorites[other] = self.favorites[other], self.favorites[index]
        elif entry in self.favorites:
            self.favorites.remove(entry)
        else:
            self.favorites.append(entry)


def local_media(folders, limit=500):
    paths = {}
    inaccessible = []
    visited = 0
    for root in folders:
        root = Path(root)
        if not root.is_dir():
            inaccessible.append(str(root))
            continue
        for folder, directories, names in os.walk(root, onerror=lambda error: inaccessible.append(error.filename)):
            directories[:] = sorted(d for d in directories if not d.startswith("."))
            visited += 1
            for name in sorted(names):
                entry = Path(folder, name)
                if entry.suffix.lower() in MEDIA_EXTENSIONS and not entry.is_symlink():
                    paths[os.path.normcase(str(entry))] = entry
                if len(paths) >= limit:
                    break
            if len(paths) >= limit or visited >= limit*4:
                break
        if len(paths) >= limit or visited >= limit*4:
            break
    return sorted(paths.values(), key=lambda path: (path.stem.casefold(), str(path))), inaccessible


def media_command(player, file, resume, store):
    return [player, "--no-config", "--fullscreen", "--force-window=yes", "--osc=yes",
            "--osd-level=2", "--osd-duration=1800", "--no-terminal",
            "--input-conf=" + str(Path(__file__).with_name("mpv-input.conf")),
            "--save-position-on-quit=" + ("yes" if resume else "no"),
            "--resume-playback=" + ("yes" if resume else "no"),
            "--watch-later-directory=" + str(store), "--", str(file)]


def diagnostics():
    interfaces = []
    if Path("/sys/class/net").is_dir():
        for entry in sorted(Path("/sys/class/net").iterdir()):
            if entry.name == "lo":
                continue
            try:
                state = (entry / "operstate").read_text().strip()
            except OSError:
                state = "unknown"
            interfaces.append(f"{entry.name}: {state}")
    network = ", ".join(interfaces) if interfaces else "No link information available."
    return f"TV OS {VERSION}  |  {platform.machine()}\n{socket.gethostname()}\nNetwork: {network}\nMedia player: {'available' if shutil.which('mpv') else 'unavailable'}"


def audio_control(*args):
    executable = shutil.which("pactl")
    if not executable:
        raise OSError("PulseAudio controls are unavailable.")
    try:
        result = subprocess.run([executable, *args], check=True, capture_output=True, text=True,
                                timeout=2, env={**os.environ, "LC_ALL":"C"})
    except (subprocess.SubprocessError, OSError) as error:
        raise OSError("The default audio output could not be reached.") from error
    return result.stdout


def audio_state():
    volume = audio_control("get-sink-volume", "@DEFAULT_SINK@")
    muted = audio_control("get-sink-mute", "@DEFAULT_SINK@")
    levels = [int(value) for value in re.findall(r"(\d+)%", volume)]
    if not levels or muted.strip() not in ("Mute: yes", "Mute: no"):
        raise OSError("The audio output returned an unknown state.")
    return max(levels), muted.strip() == "Mute: yes"
