"""Build the independent CleanFrame widget."""

import argparse
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

WIDGET = "http://www.w3.org/ns/widgets"
TIZEN = "http://tizen.org/ns/widgets"
NS = {"w": WIDGET, "t": TIZEN}
VERSION = "0.7.7"
ET.register_namespace("", WIDGET)
ET.register_namespace("tizen", TIZEN)


def write_widget(files, output, update):
    manifest = ET.fromstring(files["config.xml"])
    update(manifest, files)
    files["config.xml"] = ET.tostring(manifest, encoding="utf-8", xml_declaration=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as widget:
        for name, data in sorted(files.items()):
            widget.writestr(ZipInfo(name), data, compress_type=ZIP_DEFLATED)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream_widget", type=Path, help="CleanFrame unsigned input WGT")
    parser.add_argument("identity_manifest", type=Path, help="config.xml from a Samsung SDK web project")
    parser.add_argument("--from-release", action="store_true", help="Set a new identity on a prebuilt release widget")
    parser.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args()
    template = ET.parse(args.identity_manifest)
    identity = template.find("t:application", NS).attrib
    package_id = identity["package"]
    app_id = identity["id"]
    if not re.fullmatch(r"[A-Za-z0-9]{10}", package_id) or not re.fullmatch(
        re.escape(package_id) + r"\.[A-Za-z0-9_]+", app_id
    ):
        parser.error("The manifest must provide a Samsung TV package ID and matching application ID.")
    output = args.output / "CleanFrame-local-unsigned.wgt"
    if args.upstream_widget.resolve() == output.resolve():
        parser.error("Use a separate output path for the unsigned widget.")

    def cleanframe(manifest, files):
        application = manifest.find("t:application", NS)
        previous_id = application.attrib["id"] if args.from_release else "nClrkHome1.FrameHome"
        if args.from_release and (
            manifest.get("version") != VERSION
            or manifest.get("id") != f"urn:cleanframe:local:{application.attrib['package']}"
        ):
            raise ValueError(f"Expected the unsigned CleanFrame {VERSION} adaptation.")
        manifest.set("id", f"urn:cleanframe:local:{package_id}")
        manifest.set("version", VERSION)
        application.attrib.update(id=app_id, package=package_id)
        old = f"'{previous_id}'".encode()
        if files["device.js"].count(old) != 1:
            raise ValueError("CleanFrame's fallback app ID changed upstream.")
        files["device.js"] = files["device.js"].replace(old, f"'{app_id}'".encode())
        if args.from_release:
            return
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

    with ZipFile(args.upstream_widget) as original:
        public = {name: original.read(name) for name in original.namelist()}
    if {"author-signature.xml", "signature1.xml"} & public.keys():
        parser.error("Use an unsigned widget as input.")
    args.output.mkdir(parents=True, exist_ok=True)
    write_widget(public, output, cleanframe)
    print(f"CleanFrame: {package_id} / {app_id}")


if __name__ == "__main__":
    main()
