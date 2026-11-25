# Samsung TV OS project archive

**Project status: complete as an archive.** This repository records an x86-64 TV appliance and the signed Tizen apps tested on a physical Samsung UE43RU7102KXXH running Tizen 5.0. The appliance runs on a PC or VM over HDMI. The on-device work ran as applications on Samsung's stock Tizen.

| Stage | Archived result |
| --- | --- |
| Debian appliance | Graphical media shell, writable data image support, remote navigation, playback and opt-in key-only SSH. Source and rebuild commands are in [the appliance guide](APPLIANCE.md). |
| Coast for Tizen | Remote-focused launcher source and browser simulation in [tizen](tizen/). See [build and deployment notes](docs/DEPLOYMENT.md). |
| Free My TV | v1.5.0 ran on the physical TV. A separate Partner-signed service opened it on wake, with a reported delay of about 30 seconds from the TV picture to the launcher. Earlier Tizen acceptance did not improve the reported visible delay. See [install notes](docs/FREE-MY-TV.md) and [startup timings](docs/FREE-MY-TV-STARTUP-TEST.md). |
| CleanFrame | CleanFrame 0.7.0 was installed and launched through the SDK. A local 0.7.1 update with a 24-hour clock was installed and relaunched. The TV-local CleanFrame Startup service was installed. Visual clock confirmation and automatic CleanFrame wake remained unverified. See [the CleanFrame record](docs/CLEANFRAME-TV.md). |

The TV refused both Free My TV removals through the developer connection. The old timing tester was updated to remove its startup service. The two old app entries were still listed at handoff. First-screen placement was not achieved.

## Rebuild and review

- [CleanFrame adaptation and build instructions](samsung/cleanframe/README.md)
- [Free My TV startup helper source](samsung/free-my-tv/startup-helper/)
- [Build log](docs/BUILD-LOG.md) and [research notes](docs/RESEARCH.md)
- [CleanFrame preview](docs/screenshots/CleanFrame-browser-preview.jpg), [Debian appliance](docs/screenshots/TV-OS-Appliance.png), and [Coast preview](docs/screenshots/TV-OS-Coast-1.1-browser-test.png)

Rebuild the ISO, persistence image and signed Tizen widgets locally. The archive uses placeholders for network addresses and excludes credentials, device IDs, signed packages and persistent user data. The upstream apps are pinned by source commit or release in the notes. Their own license and asset terms apply.
