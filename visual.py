import argparse
import json
from math import ceil
import os
from pathlib import Path
import re
import shutil
import subprocess
from tv_core import MEDIA_EXTENSIONS, Preferences, audio_control, audio_state, diagnostics, local_media, media_command
import tkinter as tk
from struct import pack
import zlib
from tkinter import filedialog
from tempfile import NamedTemporaryFile

BG = "#10111a"
PANEL = "#191b28"
TEXT = "#f4f7ff"
MUTED = "#b5b6c8"
LINE = "#343647"
APP_DIR = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "tv-os/apps"
BUILTINS = (
    ("media", "Media", "Play local video and music"),
    ("search", "Search", "Find apps and indexed media"),
    ("favorites", "Favorites", "Pin apps and change their order"),
    ("settings", "Settings", "Appearance, playback and device status"),
    ("library", "Library", "Import apps from a file"),
    ("system", "System", "Device and connection details"),
    ("controls", "Controls", "Remote and keyboard guide"),
)


def read_app(path):
    with path.open("rb") as stream:
        raw = stream.read(65537)
    if len(raw) > 65536:
        raise ValueError("An app file can be at most 64 KiB.")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("An app file must contain an object.")
    identifier = data.get("id")
    if not isinstance(identifier, str) or not re.fullmatch(r"[a-z][a-z0-9-]{1,47}", identifier):
        raise ValueError("Use a lowercase app ID containing letters, numbers, or hyphens.")
    if identifier in {app[0] for app in BUILTINS}:
        raise ValueError("This ID is reserved for a built-in app.")
    name, summary, pages = (data.get(k) for k in ("name", "summary", "pages"))
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 32:
        raise ValueError("Use an app name between 1 and 32 characters.")
    if not isinstance(summary, str) or not 1 <= len(summary.strip()) <= 80:
        raise ValueError("Use a summary between 1 and 80 characters.")
    if not isinstance(pages, list) or not 1 <= len(pages) <= 20:
        raise ValueError("An app needs between 1 and 20 pages.")
    for page in pages:
        if not isinstance(page, dict):
            raise ValueError("Each page needs a title and text.")
        for key, limit in (("title", 48), ("text", 450)):
            value = page.get(key)
            if not isinstance(value, str) or not 1 <= len(value.strip()) <= limit:
                raise ValueError(f"Each page needs {key} between 1 and {limit} characters.")
    return data


def import_app(path, directory):
    data = read_app(path)
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / (data["id"] + ".json")
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False)
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return data


class TV:
    menu_screens = {"media","library","favorites","manage","pin","settings","audio","folders","reset","search","results"}
    def __init__(self, root, kiosk=False, directory=APP_DIR):
        self.root, self.directory = root, directory
        self.canvas = tk.Canvas(root, bg=BG, highlightthickness=0, takefocus=True)
        self.canvas.pack(fill="both", expand=True)
        self.selected, self.current, self.page = 0, None, 0
        self.prefs = Preferences(directory.parent/"preferences.json")
        self.message = self.prefs.warning
        self.menu_index = 0
        self.query = ""
        self.pin_id = None
        self.history = []
        self.player = None
        self.audio = None
        self.audio_problem = ""
        self.apps = []
        self.refresh_media()
        self.hitboxes, self.hero_button = [], None
        self.wallpaper = None
        image_path = Path(__file__).resolve().parent / "assets" / "coast-at-dusk.png"
        if image_path.is_file():
            self.wallpaper = tk.PhotoImage(data=image_path.read_bytes(), format="png")
        self.wallpaper_view = None
        self.backdrop = None
        self.backdrop_size = None
        root.title("TV OS")
        if kiosk:
            root.attributes("-fullscreen", True)
            root.bind("<Map>", lambda event: root.after(150, self.canvas.focus_force) if event.widget is root else None)
        else:
            root.geometry("1100x660")
            root.minsize(680, 400)
        self.canvas.bind("<Configure>", lambda _: self.draw())
        root.bind("<Key>", self.key)
        root.bind("<Button-1>", self.click)
        self.canvas.focus_set()
        self.refresh()

    def refresh(self):
        self.apps = []
        for path in sorted(self.directory.glob("*.json")):
            try:
                self.apps.append(read_app(path))
            except (OSError, ValueError, UnicodeError, RecursionError):
                continue
        self.tiles = (*BUILTINS, *((a["id"], a["name"], a["summary"]) for a in self.apps))
        self.selected = min(self.selected, len(self.tiles) - 1)
        self.draw()

    def draw(self):
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if min(w, h) < 10:
            return
        s = min(w / 1280, h / 760)
        left, right = 60*s, w-60*s
        footer = h-55*s
        self.hitboxes = []

        def text(x, y, value, size, color=TEXT, bold=False, width=None, anchor="nw"):
            style = ("DejaVu Sans", -max(10, round(size*s)), "bold" if bold else "normal")
            options = {"width": max(1, int(width))} if width else {}
            return c.create_text(x, y, text=value, fill=color, anchor=anchor, font=style, **options)

        def panel(x0, y0, x1, y1, fill, outline="", weight=1):
            c.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline, width=max(1, weight*s))

        c.create_rectangle(0, 0, w, h, fill=BG, outline="")
        if self.wallpaper and self.prefs.wallpaper:
            if self.backdrop_size != (w, h):
                zoom = ceil(max(w/self.wallpaper.width(), h/self.wallpaper.height()))
                self.wallpaper_view = self.wallpaper if zoom == 1 else self.wallpaper.zoom(zoom)
                self.backdrop = self.make_scrim(w, h)
                self.backdrop_size = (w, h)
            excess = self.wallpaper_view.width()-w
            c.create_image(-excess*.58, (h-self.wallpaper_view.height())*.5, image=self.wallpaper_view, anchor="nw")
            c.create_image(0, 0, image=self.backdrop, anchor="nw")
        panel(left, 33*s, left+27*s, 40*s, "#c784ff")
        panel(left+14*s, 43*s, left+42*s, 50*s, "#7798ff")
        text(left+56*s, 27*s, "TV OS", 20, bold=True)
        c.create_line(left, 74*s, right, 74*s, fill=LINE)

        if self.current is None:
            icon, label, summary = self.tiles[self.selected]
            hero_left = left+(right-left)*.48
            title_item = text(left, 126*s, label, 52, bold=True, width=hero_left-left-24*s)
            title_bottom = c.bbox(title_item)[3]
            summary_item = text(left, title_bottom+12*s, summary, 21, MUTED, width=hero_left-left-34*s)
            button_top = min(354*s, max(250*s, c.bbox(summary_item)[3]+19*s))
            panel(left, button_top, left+142*s, button_top+47*s, TEXT)
            text(left+18*s, button_top+10*s, "OK   Open", 19, "#101018", True)
            self.hero_button = (left, button_top, left+142*s, button_top+47*s)

            row_top, row_bottom = 447*s, 625*s
            columns = min(4, len(self.tiles))
            gap = 17*s
            card_width = (right-left-(columns-1)*gap)/columns
            first = (self.selected // columns)*columns
            text(left, 405*s, "Apps", 24, bold=True)
            if len(self.tiles) > columns:
                text(right, 410*s, f"{self.selected+1} of {len(self.tiles)}", 16, MUTED, anchor="ne")
            for index, (entry, name, _) in enumerate(self.tiles[first:first+columns], first):
                x = left+(index-first)*(card_width+gap)
                active = index == self.selected
                self.draw_art(entry, x, row_top, x+card_width, row_bottom, self.colors(entry), s)
                panel(x, row_bottom-50*s, x+card_width, row_bottom, "#1b1d2b" if active else PANEL)
                text(x+14*s, row_bottom-41*s, name, 18, TEXT if active else MUTED, True, card_width-25*s)
                if active:
                    panel(x, row_top, x+card_width, row_bottom, "", "#eeeaff", 3)
                self.hitboxes.append(((x, row_top, x+card_width, row_bottom), index))
        elif self.current in self.menu_screens:
            self.hero_button = None
            title = {"library":"App library", "media":"Media", "favorites":"Favorites", "settings":"Settings", "audio":"Audio output",
                     "manage":"Manage favorites", "pin":"Favorite options", "folders":"Media folders",
                     "reset":"Reset settings?", "search":"Search", "results":"Search results"}[self.current]
            text(left, 106*s, title, 47, bold=True)
            if self.current == "search":
                text(left, 181*s, self.query or "Enter an app or media title", 23, MUTED)
                keys = self.search_keys
                width = min(103*s,(right-left-6*10*s)/7)
                for i, value in enumerate(keys):
                    x = left+(i%7)*(width+10*s)
                    y = 239*s+(i//7)*59*s
                    active = i == self.menu_index
                    panel(x,y,x+width,y+47*s,TEXT if active else PANEL)
                    text(x+10*s,y+11*s,value,17,"#131323" if active else TEXT,True)
            else:
                entries = self.menu()
                self.menu_index = min(self.menu_index, max(0,len(entries)-1))
                if self.current == "audio":
                    audio_status = self.audio_problem if self.audio is None else f"Volume {self.audio[0]}%"+("  |  Muted" if self.audio[1] else "")
                    text(left,171*s,audio_status,17,MUTED)
                if not entries and self.current != "audio":
                    text(left,190*s,"No matching apps or media." if self.current == "results" else
                         "No imported apps yet. Import one from the library.",23,MUTED)
                elif self.current == "media" and (self.media_problem or not shutil.which("mpv")):
                    text(left,171*s,self.media_problem or "The media player is unavailable.",17,MUTED)
                first = self.menu_index//6*6
                if len(entries) > 6:
                    text(right, 160*s, f"{self.menu_index+1} of {len(entries)}",16,MUTED,anchor="ne")
                for i,(label, _) in enumerate(entries[first:first+6],first):
                    y = 209*s+(i-first)*64*s
                    active = i == self.menu_index
                    panel(left,y,right,y+54*s,TEXT if active else PANEL)
                    available = max(8,int((right-left)/(12*s))-2)
                    label = label if len(label) <= available else label[:available-1]+"..."
                    text(left+17*s,y+12*s,label,21,"#151622" if active else TEXT,active)
                    self.hitboxes.append(((left,y,right,y+54*s),i))
        else:
            self.hero_button = None
            title, description = self.details()
            art_left = right-min((right-left)*.34, 410*s)
            title_item = text(left, 140*s, title, 49, bold=True, width=art_left-left-28*s)
            title_bottom = c.bbox(title_item)[3]
            text(left, title_bottom+26*s, description, 22, MUTED, width=art_left-left-34*s)
            if self.current == "library":
                text(left, footer-48*s, "Enter  Import app", 18, TEXT, True)

        c.create_line(left, footer, right, footer, fill=LINE)
        hint = "Arrow keys  Move" if self.current is None else "Esc  Back"
        if self.current is not None and self.current not in self.menu_screens | {"system", "controls"}:
            hint += "        Arrow keys  Turn page"
        text(left, footer+14*s, hint, 16, MUTED)
        if self.message:
            text(right, footer+14*s, self.message, 16, TEXT, width=(right-left)*.67, anchor="ne")

    @staticmethod
    def make_scrim(w, h):
        def chunk(kind, data):
            return pack(">I", len(data)) + kind + data + pack(">I", zlib.crc32(kind + data))

        left = [max(0, 1-x/(w*.65)) for x in range(w)]
        rows = bytearray()
        for y in range(h):
            vertical = max(0, (y/h-.35)/.65)
            base = 24+int(175*vertical**1.4)
            alpha = bytes(min(235, base+int(127*fade*(1-vertical))) for fade in left)
            row = bytearray(b"\x0a\x0c\x16\0"*w)
            row[3::4] = alpha
            rows.extend(b"\0"+row)
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", pack(">IIBBBBB",w,h,8,6,0,0,0))
        png += chunk(b"IDAT", zlib.compress(rows,3)) + chunk(b"IEND", b"")
        return tk.PhotoImage(data=png, format="png")

    @staticmethod
    def colors(icon):
        palettes = {
            "library": ((27, 14, 63), (99, 45, 171), "#c895ff"),
            "media": ((26, 16, 59), (86, 42, 143), "#d5a7ff"),
            "search": ((9, 37, 56), (21, 90, 122), "#89e6ff"),
            "favorites": ((53, 23, 39), (131, 56, 94), "#ffacc4"),
            "settings": ((21, 43, 40), (43, 94, 82), "#a2e5ba"),
            "system": ((10, 35, 53), (23, 99, 119), "#77ebd8"),
            "controls": ((54, 25, 38), (132, 56, 86), "#ffa0b1"),
        }
        return palettes.get(icon, ((19, 30, 67), (44, 69, 148), "#95baff"))

    def draw_art(self, icon, x, y, right, bottom, family, scale):
        c = self.canvas
        dark, light, accent = family
        width, height = right-x, bottom-y
        bands = 18
        for band in range(bands):
            position = band/(bands-1)
            blend = (1-position)**1.45
            color = "#%02x%02x%02x" % tuple(round(a+(b-a)*blend) for a, b in zip(dark, light))
            c.create_rectangle(x, y+height*band/bands, right, y+height*(band+1)/bands+1,
                               fill=color, outline="")
        middle_x = x+width*.53
        middle_y = y+height*.37
        radius = min(width*.45, height*.28)
        for index in range(7):
            ratio = .49+index*.079
            rx, ry = radius*ratio, radius*ratio*.71
            delta = radius*(index-3)*.071
            c.create_oval(middle_x-rx+delta, middle_y-ry-delta*.45,
                          middle_x+rx+delta, middle_y+ry-delta*.45,
                          outline=accent, width=max(1, round(scale)))
        icon_scale = min(radius/33, .90*scale)
        pad = 27*icon_scale
        c.create_oval(middle_x-pad, middle_y-pad, middle_x+pad, middle_y+pad,
                      fill="#171523", outline=accent, width=max(1, round(2*scale)))
        self.draw_icon(icon, middle_x-19.5*icon_scale, middle_y-19.5*icon_scale, icon_scale)

    def draw_icon(self, icon, x, y, scale):
        def points(*coords):
            return tuple((x if i % 2 == 0 else y) + v * scale for i, v in enumerate(coords))

        c = self.canvas
        width = max(2, int(3 * scale))
        if icon == "library":
            c.create_rectangle(*points(0, 12, 39, 38), outline=TEXT, width=width)
            c.create_line(*points(8, 5, 32, 5), fill=TEXT, width=width)
            c.create_line(*points(19, 18, 19, 31, 13, 25, 19, 31, 25, 25), fill=TEXT, width=width)
        elif icon == "media":
            c.create_polygon(*points(12, 7, 32, 19, 12, 32), fill=TEXT, outline="")
        elif icon == "search":
            c.create_oval(*points(4, 4, 27, 27), outline=TEXT, width=width)
            c.create_line(*points(24, 24, 35, 35), fill=TEXT, width=width)
        elif icon == "favorites":
            c.create_polygon(*points(7, 4, 32, 4, 32, 34, 19, 25, 7, 34),
                             fill="", outline=TEXT, width=width)
        elif icon == "settings":
            for y_offset, slider in ((9, 13), (19, 27), (29, 18)):
                c.create_line(*points(4, y_offset, 35, y_offset), fill=TEXT, width=width)
                c.create_line(*points(slider, y_offset-4, slider, y_offset+4), fill=TEXT, width=width+1)
        elif icon == "system":
            c.create_oval(*points(0, 0, 39, 39), outline=TEXT, width=width)
            c.create_line(*points(19, 8, 19, 24, 28, 24), fill=TEXT, width=width)
        elif icon == "controls":
            c.create_line(*points(19, 0, 19, 38), fill=TEXT, width=width)
            c.create_line(*points(0, 19, 38, 19), fill=TEXT, width=width)
            c.create_oval(*points(13, 13, 25, 25), outline=TEXT, width=width)
        else:
            c.create_polygon(*points(19, 0, 39, 19, 19, 39, 0, 19), outline=TEXT, fill="", width=width)

    def save(self, message="Saved."):
        try:
            self.prefs.save()
            self.message = message
        except OSError as error:
            self.message = f"Could not save settings. {error}"

    def catalog(self):
        return {entry[0]: entry[1] for entry in self.tiles if entry[0] not in self.menu_screens or entry[0] == "media"}

    def open_view(self, view):
        if self.current is not None:
            self.history.append((self.current, self.menu_index, self.page))
        self.current, self.menu_index, self.page = view, 0, 0

    def back(self):
        if self.history:
            self.current, self.menu_index, self.page = self.history.pop()
        else:
            self.current = None
        self.message = ""

    def refresh_media(self):
        self.media, missing = local_media(self.prefs.folders)
        self.media_problem = f"{len(missing)} media folder(s) unavailable." if missing else ""

    def choose_folder(self):
        folder = filedialog.askdirectory(parent=self.root, title="Add media folder")
        if folder:
            if folder not in self.prefs.folders:
                self.prefs.folders.append(folder)
                self.save("Media folder added.")
            self.refresh_media()
        self.canvas.focus_set()

    def choose_file(self):
        path = filedialog.askopenfilename(parent=self.root, title="Play media",
            filetypes=[("Supported media", " ".join("*"+ext for ext in sorted(MEDIA_EXTENSIONS)))])
        if path:
            self.play(Path(path))
        self.canvas.focus_set()

    def play(self, path):
        if self.player is not None:
            return
        executable = shutil.which("mpv")
        if not executable:
            self.message = "mpv is unavailable on this device."
            return
        if not path.is_file() or path.suffix.lower() not in MEDIA_EXTENSIONS:
            self.message = "Media is missing or the format is unavailable."
            return
        try:
            watch = self.directory.parent/"watch-later"
            watch.mkdir(parents=True, exist_ok=True)
            self.player = subprocess.Popen(media_command(executable, path, self.prefs.resume, watch),
                                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
        except OSError as error:
            self.message = f"Could not start playback. {error}"
            return
        self.message = f"Opening {path.name}..."
        self.root.after(300, self.check_player)

    def check_player(self):
        result = self.player.poll()
        if result is None:
            self.root.after(300, self.check_player)
            return
        self.player = None
        if result == 10:
            self.current, self.history = None, []
        self.message = "Playback ended." if result in (0, 10) else f"Playback failed (mpv exit {result})."
        self.canvas.focus_force()
        self.draw()

    def toggle_option(self, option):
        setattr(self.prefs, option, not getattr(self.prefs, option))
        self.save()

    def reset_settings(self):
        self.prefs.reset()
        self.refresh_media()
        self.save("Launcher settings restored. Imported apps were kept.")
        self.current, self.menu_index = "settings", 0
        if self.history and self.history[-1][0] == "settings":
            self.history.pop()

    def change_favorite(self, entry, shift=0):
        self.prefs.favorite(entry, shift)
        self.save()

    def menu(self):
        current = self.current
        catalog = self.catalog()
        if current == "library":
            return [("Import an app file", self.choose_app)] + [
                (name, lambda entry=entry: self.open_view(entry)) for entry, name in catalog.items()]
        if current == "media":
            actions = [("Open a media file", self.choose_file), ("Add a media folder", self.choose_folder),
                       ("Rescan media folders", self.refresh_media)]
            return actions + [(path.name, lambda path=path: self.play(path)) for path in self.media]
        if current == "favorites":
            return [("Manage favorites", lambda: self.open_view("manage"))] + [
                (catalog[entry], lambda entry=entry: self.open_view(entry)) for entry in self.prefs.favorites
                if entry in catalog]
        if current == "manage":
            ordered = list(dict.fromkeys(self.prefs.favorites+list(catalog)))
            return [(("Pinned  " if entry in self.prefs.favorites else "Pin  ")+catalog[entry],
                     lambda entry=entry: self.pin_menu(entry)) for entry in ordered if entry in catalog]
        if current == "pin":
            entry = self.pin_id
            pinned = entry in self.prefs.favorites
            actions = [("Remove pin" if pinned else "Pin app", lambda: self.change_favorite(entry))]
            if pinned:
                index = self.prefs.favorites.index(entry)
                if index:
                    actions.append(("Move earlier", lambda: self.change_favorite(entry, -1)))
                if index + 1 < len(self.prefs.favorites):
                    actions.append(("Move later", lambda: self.change_favorite(entry, 1)))
            return actions
        if current == "settings":
            return [
                ("Wallpaper  " + ("On" if self.prefs.wallpaper else "Off"), lambda: self.toggle_option("wallpaper")),
                ("Resume playback  " + ("On" if self.prefs.resume else "Off"), lambda: self.toggle_option("resume")),
                ("Audio output", self.open_audio),
                ("Media folders", lambda: self.open_view("folders")),
                ("Device status", lambda: self.open_view("system")),
                ("Reset launcher settings...", lambda: self.open_view("reset")),
            ]
        if current == "audio":
            if self.audio is None:
                return [("Retry audio output", self.refresh_audio)]
            return [(("Unmute" if self.audio[1] else "Mute"), self.toggle_mute),
                    ("Volume up", lambda: self.adjust_volume(5)),
                    ("Volume down", lambda: self.adjust_volume(-5))]
        if current == "folders":
            return [("Add folder", self.choose_folder)] + [
                ("Remove: "+folder, lambda folder=folder: self.remove_folder(folder))
                for folder in self.prefs.folders]
        if current == "reset":
            return [("Cancel", self.back), ("Reset launcher settings", self.reset_settings)]
        if current == "results":
            needle = self.query.casefold().strip()
            apps = [(name, lambda entry=entry: self.open_view(entry)) for entry, name in catalog.items()
                    if needle and needle in name.casefold()]
            media = [(path.name, lambda path=path: self.play(path)) for path in self.media
                     if needle and needle in path.name.casefold()]
            return apps + media
        return []

    def refresh_audio(self):
        try:
            self.audio = audio_state()
            self.audio_problem = ""
        except OSError as error:
            self.audio = None
            self.audio_problem = str(error)

    def open_audio(self):
        self.refresh_audio()
        self.open_view("audio")

    def set_audio(self, *command):
        try:
            audio_control(*command)
        except OSError as error:
            self.message = str(error)
        self.refresh_audio()

    def toggle_mute(self):
        self.set_audio("set-sink-mute", "@DEFAULT_SINK@", "toggle")

    def adjust_volume(self, amount):
        volume = max(0, min(100,self.audio[0]+amount))
        self.set_audio("set-sink-volume", "@DEFAULT_SINK@", f"{volume}%")

    def pin_menu(self, entry):
        self.pin_id = entry
        self.open_view("pin")

    def remove_folder(self, folder):
        self.prefs.folders.remove(folder)
        self.refresh_media()
        self.save("Folder removed from the library.")

    def search_key(self, key):
        keys = self.search_keys
        if key in ("Left", "Right", "Up", "Down"):
            self.menu_index = (self.menu_index + {"Left": -1, "Right": 1, "Up": -7, "Down": 7}[key]) % len(keys)
        elif key in ("Return", "KP_Enter", "space"):
            value = keys[self.menu_index]
            if value == "Results":
                self.open_view("results")
            elif value == "Delete":
                self.query = self.query[:-1]
            elif len(self.query) < 80:
                self.query += " " if value == "Space" else value.lower()

    @property
    def search_keys(self):
        return (*"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", "Space", "Delete", "Results")

    def details(self):
        if self.current == "library":
            return "App library", "Press OK to import a .json app from a file. Installed apps appear on Home. A file with an existing app ID updates that app."
        if self.current == "system":
            mode = "The live image uses temporary storage."
            if Path("/run/live").exists():
                mountinfo = Path("/proc/self/mountinfo").read_text()
                if any(line.split()[4] == "/home" for line in mountinfo.splitlines()):
                    mode = "Home has a separate mount. See build documentation for persistence setup."
            else:
                mode = "Settings and imports are stored in your user data folder."
            return "System", diagnostics()+"\n\n"+mode
        if self.current == "controls":
            return "Controls", "Arrows   Move focus or turn pages\nEnter / OK   Open or confirm\nEscape   Back\nHome   Return to the shelf\nDuring playback, Enter pauses and Left / Right seek."
        app = next(a for a in self.apps if a["id"] == self.current)
        page = app["pages"][self.page]
        return page["title"], f"{page['text']}\n\nPage {self.page+1} of {len(app['pages'])}"

    def key(self, event):
        key = event.keysym
        self.message = ""
        if key == "Home":
            self.current, self.history = None, []
        elif key in ("Escape", "BackSpace") and self.current is not None:
            self.back()
        elif self.current == "search":
            character = getattr(event, "char", "")
            if len(character) == 1 and character.isalnum() and len(self.query) < 80:
                self.query += character.lower()
            else:
                self.search_key(key)
        elif self.current in self.menu_screens:
            entries = self.menu()
            if entries:
                if key in ("Left", "Right", "Up", "Down"):
                    self.menu_index = (self.menu_index + (-1 if key in ("Up", "Left") else 1)) % len(entries)
                elif key in ("Return", "KP_Enter", "space"):
                    entries[min(self.menu_index,len(entries)-1)][1]()
        elif key in ("Return", "KP_Enter", "space") and self.current is None:
            self.open_view(self.tiles[self.selected][0])
        elif key in ("Left", "Right", "Up", "Down"):
            change = -1 if key in ("Left", "Up") else 1
            if self.current is None:
                self.selected = (self.selected + change) % len(self.tiles)
            else:
                app = next((a for a in self.apps if a["id"] == self.current), None)
                if app:
                    self.page = (self.page + change) % len(app["pages"])
        self.draw()
        return "break"

    def click(self, event):
        if event.widget is not self.canvas:
            return
        if self.hero_button is not None:
            left, top, right, bottom = self.hero_button
            if left <= event.x <= right and top <= event.y <= bottom:
                self.key(type("Click", (), {"keysym": "Return"})())
                return
        for (left, top, right, bottom), index in self.hitboxes:
            if left <= event.x <= right and top <= event.y <= bottom:
                if self.current in self.menu_screens:
                    self.menu_index = index
                else:
                    self.selected = index
                self.key(type("Click", (), {"keysym": "Return"})())
                break

    def choose_app(self):
        bundled = Path("/opt/tv-os/examples")
        initial = bundled if bundled.is_dir() else Path(__file__).resolve().parent / "examples"
        filename = filedialog.askopenfilename(parent=self.root, title="Import TV app", initialdir=initial,
                                              filetypes=[("TV app", "*.json")])
        if filename:
            try:
                app = import_app(Path(filename), self.directory)
                self.refresh()
                self.selected = next(i for i, tile in enumerate(self.tiles) if tile[0] == app["id"])
                self.message = f"Installed {app['name']}."
            except (OSError, ValueError, UnicodeError, RecursionError) as error:
                self.message = f"Import failed. {error}"
        self.canvas.focus_set()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kiosk", action="store_true")
    args = parser.parse_args()
    window = tk.Tk()
    TV(window, args.kiosk)
    window.mainloop()
