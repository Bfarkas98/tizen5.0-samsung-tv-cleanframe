"""Run with python tests/smoke_visual.py on a Tk-capable development host."""
import json
from pathlib import Path
import sys
import tempfile
import tkinter as tk
from types import SimpleNamespace
from unittest.mock import patch

project = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project))
from tv_core import Preferences, local_media, media_command
from visual import TV, import_app

with tempfile.TemporaryDirectory() as directory:
    base = Path(directory)
    sample = project/"examples/field-guide.json"
    root = tk.Tk()
    root.attributes("-alpha", 0.0)
    try:
        tv = TV(root, directory=base/"apps")
        root.update()

        def press(key, char=""):
            tv.key(SimpleNamespace(keysym=key, char=char))
            root.update()

        def home(view):
            press("Home")
            for _ in tv.tiles:
                if tv.tiles[tv.selected][0] == view:
                    break
                press("Right")
            assert tv.tiles[tv.selected][0] == view
            press("Return")

        home("library")
        with patch("tkinter.filedialog.askopenfilename", return_value=str(sample)):
            press("Return")
        assert "Installed Field Guide" in tv.message
        press("Escape")
        press("Return")
        assert tv.details()[0] == "Field Guide"
        press("Right")
        assert tv.details()[0] == "Install your own"
        press("Escape")
        assert tv.current is None and tv.tiles[tv.selected][0] == "field-guide"

        home("favorites")
        press("Return")
        names = [name for name, _ in tv.menu()]
        selected = names.index("Pin  Field Guide")
        for _ in range(selected):
            press("Down")
        press("Return")
        press("Return")
        assert Preferences(base/"preferences.json").favorites == ["field-guide"]
        press("Escape")
        assert tv.current == "manage" and tv.menu_index == selected
        tv.change_favorite("system")
        tv.change_favorite("system", -1)
        assert Preferences(base/"preferences.json").favorites == ["system", "field-guide"]
        (base/"apps/field-guide.json").unlink()
        tv.refresh()
        home("favorites")
        assert [name for name,_ in tv.menu()] == ["Manage favorites", "System"]

        media = base/"media"
        media.mkdir()
        (media/"Coast recording.mp4").touch()
        (media/"Ignored.txt").touch()
        home("media")
        press("Down")
        with patch("tkinter.filedialog.askdirectory", return_value=str(media)):
            press("Return")
        assert [x.name for x in tv.media] == ["Coast recording.mp4"]
        home("search")
        for char in "coast":
            press(char, char)
        tv.menu_index = len(tv.search_keys)-1
        press("Return")
        assert [name for name,_ in tv.menu()] == ["Coast recording.mp4"]
        press("Escape")
        assert tv.current == "search" and tv.query == "coast"
        press("Home")
        assert tv.current is None

        home("settings")
        press("Return")
        assert Preferences(base/"preferences.json").wallpaper is False
        for _ in range(5):
            press("Down")
        press("Return")
        assert tv.current == "reset"
        press("Down")
        press("Return")
        assert Preferences(base/"preferences.json").wallpaper is True
        (base/"preferences.json").write_text("invalid", encoding="utf-8")
        assert Preferences(base/"preferences.json").warning
        assert local_media([base/"missing"])[1] == [str(base/"missing")]
        assert "--resume-playback=no" in media_command("mpv", media/"Coast recording.mp4", False, base)
        with patch("visual.shutil.which", return_value=None):
            tv.play(media/"Coast recording.mp4")
        assert "unavailable" in tv.message
        with patch("visual.shutil.which", return_value="mpv"), patch("visual.subprocess.Popen", side_effect=OSError("missing executable")):
            tv.play(media/"Coast recording.mp4")
        assert "Could not start playback" in tv.message
        home("media")
        with patch("tkinter.filedialog.askopenfilename", return_value=""):
            press("Return")
        assert tv.current == "media" and tv.menu_index == 0
        root.geometry("1920x1080")
        root.update()
        home("library")
        assert tv.canvas.winfo_width() >= 1000 and tv.hitboxes

        import_app(sample, base/"apps")
        invalid = base/"bad.json"
        for payload in ({"id":"../escape"}, {"id":"media"}, [], {"id":"field-guide"}, {"id":"x"*65540}):
            invalid.write_text(json.dumps(payload), encoding="utf-8")
            try:
                import_app(invalid, base/"apps")
            except ValueError:
                pass
            else:
                raise AssertionError(payload)
        for _ in tv.tiles:
            press("Home")
            press("Right")
            assert any(i == tv.selected for _, i in tv.hitboxes)
        print("PASS: app import, pages, Back restoration, favorites and ordering, missing apps, media scan, search, reset, invalid storage and imports.")
    finally:
        root.destroy()
