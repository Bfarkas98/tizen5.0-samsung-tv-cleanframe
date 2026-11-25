"""Build and verify the release widget, then test the downloadable-widget route."""

import hashlib
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile

BUILDER = Path(__file__).resolve().parents[1] / "samsung/cleanframe/build-cleanframe-local.py"
WIDGET = "http://www.w3.org/ns/widgets"
TIZEN = "http://tizen.org/ns/widgets"
VERSION = "0.7.7"
PUBLIC_PACKAGE = "CfRelease7"
TEST_PACKAGE = "CfBuildTst"


def build(source, directory, package, *, from_release=False):
    manifest = directory.with_suffix(".xml")
    manifest.write_text(
        f'<widget xmlns="{WIDGET}" xmlns:tizen="{TIZEN}">'
        f'<tizen:application id="{package}.CleanFrame" package="{package}"/>'
        '</widget>',
        encoding="utf-8",
    )
    command = [sys.executable, "-B", str(BUILDER), str(source), str(manifest), "--output", str(directory)]
    if from_release:
        command.append("--from-release")
    subprocess.run(command, check=True)
    return directory / "CleanFrame-local-unsigned.wgt"


def inspect(widget, package):
    with ZipFile(widget) as archive:
        assert archive.testzip() is None, "Invalid ZIP contents"
        names = archive.namelist()
        assert len(names) == len(set(names)), "Duplicate ZIP entries"
        assert {"index.html", "config.xml", "device.js", "main.js", "style.css", "weather.js",
                "LICENSE", "THIRD_PARTY_NOTICES.md"} <= set(names), "Missing app files or notices"
        assert not any(
            "signature" in Path(name).name.lower()
            or name.startswith("assets/private-fonts/")
            or Path(name).suffix.lower() in {".p12", ".pfx", ".key", ".pem"}
            or Path(name).name in {"profiles.xml", "device-profile.xml"}
            for name in names
        ), "Unexpected private or signing data"
        assert b'CleanFramePrivateFontIDs = ["geist", "newsreader"]' in archive.read("assets/font-catalog.js")
        manifest = ET.fromstring(archive.read("config.xml"))
        app = manifest.find(f"{{{TIZEN}}}application")
        assert manifest.get("id") == f"urn:cleanframe:local:{package}"
        assert manifest.get("version") == VERSION
        assert app.get("required_version") == "5.0"
        assert app.get("package") == package and app.get("id") == f"{package}.CleanFrame"
        assert f"'{package}.CleanFrame'".encode() in archive.read("device.js")
        assert b"var d = new Date(), h = d.getHours(), m = d.getMinutes();" in archive.read("main.js")
        assert b"d.getHours() % 12" not in archive.read("main.js")


def main(source, output):
    with TemporaryDirectory() as temporary:
        temp = Path(temporary)
        public = build(source, temp / "public", PUBLIC_PACKAGE)
        inspect(public, PUBLIC_PACKAGE)
        rebuilt = build(public, temp / "reidentified", TEST_PACKAGE, from_release=True)
        inspect(rebuilt, TEST_PACKAGE)
        direct = build(source, temp / "direct", TEST_PACKAGE)
        assert rebuilt.read_bytes() == direct.read_bytes(), "Release route differs from direct source build"
        data = public.read_bytes()
    output.mkdir(parents=True, exist_ok=True)
    name = f"CleanFrame-{VERSION}-unsigned.wgt"
    (output / name).write_bytes(data)
    (output / "SHA256SUMS.txt").write_bytes(f"{hashlib.sha256(data).hexdigest()}  {name}\n".encode("ascii"))
    print(f"Verified {name} and the release identity workflow.")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
