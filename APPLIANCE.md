# TV OS

TV OS is a remote-first Debian live appliance for an x86-64 PC or VM. It starts a full-screen shell and can use a Samsung TV as its HDMI display. The separate `tizen/` application is a limited, on-device way to browse and launch installed Samsung apps. See `DEPLOYMENT.md` for the hardware decision and signing checklist.

## Run the appliance

Attach `TV-OS-Appliance-amd64.iso` as optical media and `TVOS-Data.img` as a writable second disk in an x86-64 VM. Select the live boot entry. On Windows, use `Start-TVOS.ps1 -QemuPath <path-to-qemu-system-x86_64.exe>` or put QEMU on PATH. The script starts a VM with virtual audio and networking. If WHPX is unavailable, pass `-Accelerator tcg`.

The data image stores the live user's home directory. Keep it attached across restarts to retain settings, favorites and imported apps. Booting without it uses temporary storage. The ISO is a live system with optional persistence. It does not install to an existing disk.

## Use it

- **Media** opens a local file or indexes a folder. Playback runs in fullscreen mpv. Enter or Space pauses and resumes, Left and Right seek by ten seconds, Up and Down change player volume, and Esc returns to the shell. The Home key exits playback to the shelf. If audio is muted, open Settings, then Audio output. The a and j keys cycle audio and subtitle tracks when present.
- **Search** has a directional on-screen keyboard and searches indexed filenames and available library entries.
- **Favorites** lets you pin entries and move them earlier or later. Missing entries are hidden until they become available again.
- **App library** opens built-in modules and imported JSON document apps. Import the sample at `examples/field-guide.json` to try the format.
- **Settings** controls wallpaper, playback resume, media folders and the default PulseAudio output, shows device status, and can reset launcher preferences after confirmation. The reset keeps imported apps.

Use arrows and Enter in the shell, Esc to go back, and Home to return to the shelf. For local files on removable media, mount the media in Linux before opening it in the shell. Network status reports local interface link state, and it does not test internet reachability.

## Develop and rebuild

On Windows, `python visual.py` previews the shell. The preview requires Tk and a separately available mpv executable if playback is needed. Run `python tests/smoke_visual.py` to exercise shell behavior.

On Debian 13 amd64, install `live-build` and run `sudo sh image/build-visual.sh`. To create a clean data image, install `e2fsprogs` and run `sh image/create-data-image.sh TVOS-Data.img`. The data script creates a new regular file and refuses an existing output. The Windows `Build-VisualTVOS.ps1` wrapper uses the existing `TVOS-Linux` WSL distribution. The old console launcher and ISO remain available through `launcher.py` and `image/build.sh`.

## PC connectivity

For the Samsung TV, use `Connect-Samsung.ps1 -Device TV_IP:26101` on the authorized PC. This uses the SDK's SDB connection.

For the Debian appliance, SSH is off by default. On the appliance console, run `sudo start-tv-ssh /path/to/pc-key.pub`. It starts key-only SSH on port 2222 as the live user `user`. Password and root login are disabled. From the PC, use `ssh -p 2222 user@DEVICE_IP`. In QEMU, forward an explicit loopback host port to guest port 2222 before connecting. The authorization is temporary.

## Samsung Tizen app

Open `tizen/index.html` in a browser for a labeled simulation. The source targets TV 5.0 and uses public app listing and launch APIs. The SDK build has passed. Installation on the Samsung requires a Samsung TV signing profile that includes the device. See [deployment](docs/DEPLOYMENT.md) and [research](docs/RESEARCH.md).

To run the Coast browser smoke test, make `playwright-core` available to Node and run `node tests/tizen_coast.cjs`. Set `COAST_CHROME` if Chrome is outside its default Windows install path.

The built-in ImageGen artwork is `assets/coast-at-dusk.png`. Its prompt requested a wide cinematic photograph of a rugged far-north coast at blue hour, with dark water and mountains, lavender and coral light, and a naturally dark left and lower third for interface text.
