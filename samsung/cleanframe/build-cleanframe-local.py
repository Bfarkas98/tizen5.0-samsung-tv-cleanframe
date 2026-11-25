"""Build the independent CleanFrame widget and its separate TV-local startup app."""

import argparse
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

SOURCE_DIR = Path(__file__).resolve().parent
WIDGET = "http://www.w3.org/ns/widgets"
TIZEN = "http://tizen.org/ns/widgets"
NS = {"w": WIDGET, "t": TIZEN}
HELPER_ID = "ClnFrmBoot"
ET.register_namespace("", WIDGET)
ET.register_namespace("tizen", TIZEN)


def write_widget(files, output, update):
    manifest = ET.fromstring(files["config.xml"])
    update(manifest, files)
    files["config.xml"] = ET.tostring(manifest, encoding="utf-8", xml_declaration=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as widget:
        for name, data in files.items():
            widget.writestr(name, data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream_widget", type=Path, help="CleanFrame public-font unsigned WGT")
    parser.add_argument("identity_manifest", type=Path, help="config.xml from a Samsung SDK web project")
    parser.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    template = ET.parse(args.identity_manifest)
    identity = template.find("t:application", NS).attrib
    package_id = identity["package"]
    app_id = identity["id"]

    def cleanframe(manifest, files):
        manifest.set("id", f"urn:cleanframe:local:{package_id}")
        manifest.set("version", "0.7.1")
        manifest.find("t:application", NS).attrib.update(id=app_id, package=package_id)
        old = b"'nClrkHome1.FrameHome'"
        if files["device.js"].count(old) != 1:
            raise ValueError("CleanFrame's fallback app ID changed upstream.")
        files["device.js"] = files["device.js"].replace(old, f"'{app_id}'".encode())
        old_clock = (
            b"    var d = new Date(), h = d.getHours() % 12 || 12, m = d.getMinutes();\n"
            b"    return h + ':' + (m < 10 ? '0' : '') + m;"
        )
        new_clock = (
            b"    var d = new Date(), h = d.getHours(), m = d.getMinutes();\n"
            b"    return (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m;"
        )
        main = files["main.js"].replace(b"\r\n", b"\n")
        if main.count(old_clock) != 1:
            raise ValueError("CleanFrame's clock function changed upstream.")
        files["main.js"] = main.replace(old_clock, new_clock)

    def startup(manifest, files):
        manifest.set("id", "urn:cleanframe:startup")
        manifest.set("version", "1.0.0")
        manifest.find("t:application", NS).attrib.update(
            id=f"{HELPER_ID}.Helper", package=HELPER_ID
        )
        manifest.find("w:name", NS).text = "CleanFrame Startup"
        manifest.find("w:description", NS).text = "Opens CleanFrame when the TV turns on."
        service = manifest.find("t:service", NS)
        service.set("id", f"{HELPER_ID}.Autostart")
        service.find("t:name", NS).text = "CleanFrame Autostart"
        service.find("t:description", NS).text = "Opens CleanFrame on boot and wake."
        script = (SOURCE_DIR / "cleanframe-autostart.js").read_text(encoding="utf-8")
        files["autostart.js"] = script.replace("__CLEANFRAME_APP_ID__", app_id).encode()
        files["index.html"] = (
            "<!doctype html><html lang='en'><meta charset='utf-8'><title>CleanFrame Startup</title>"
            "<body style='background:#142137;color:white;padding:8%;font:32px sans-serif'>"
            "<h1>CleanFrame Startup</h1><button id='launch' autofocus>Open CleanFrame</button>"
            "<p id='status' role='status'></p><script src='helper.js'></script></body></html>"
        ).encode()
        files["helper.js"] = (
            "var launch = document.getElementById('launch');\n"
            "var statusText = document.getElementById('status');\n"
            + 'launch.onclick = function () { tizen.application.launch("'
            + app_id
            + '", function () {}, function () { statusText.textContent = "Could not open CleanFrame."; }); };\n'
            + "document.addEventListener('keydown', function (event) {"
            + " if (event.keyCode === 10009) tizen.application.getCurrentApplication().exit(); });\n"
        ).encode()

    with ZipFile(args.upstream_widget) as original:
        public = {name: original.read(name) for name in original.namelist()}
    write_widget(public, args.output / "CleanFrame-local-unsigned.wgt", cleanframe)
    helper = SOURCE_DIR.parent / "free-my-tv" / "startup-helper"
    helper_files = {name: (helper / name).read_bytes() for name in ("config.xml", "icon.png", "LICENSE")}
    write_widget(helper_files, args.output / "CleanFrame-startup-unsigned.wgt", startup)
    print(f"CleanFrame: {package_id} / {app_id}")
    print(f"CleanFrame Startup: {HELPER_ID} / {HELPER_ID}.Helper")


if __name__ == "__main__":
    main()
