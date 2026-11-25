# CleanFrame for Samsung Tizen 5.0

An independent adaptation of **[CleanFrame by Nathan Clark (nthnclrk)](https://github.com/nthnclrk/CleanFrame)**, the original launcher for Samsung The Frame. This project adapts the interface for an older Samsung TV and runs as a sideloaded Tizen web application alongside Samsung Smart Hub. The original project, design, and assets are credited to their respective authors.

[Install on your TV](samsung/cleanframe/README.md) · [Give this guide to an AI agent](AGENTS.md) · [Compatibility and test results](docs/CLEANFRAME-TV.md)

![CleanFrame 0.7.7 home screen with the clock, weather, app dock, and HDMI shortcuts](docs/screenshots/CleanFrame-0.7.7-preview.jpg)

## What's included

- A remote-friendly app dock with a top menu and a large 24-hour clock.
- A three-day Celsius forecast on Home, a detailed forecast view, and an editable city. Weather requests go to Open-Meteo and the latest forecast is cached on the TV.
- A Home HDMI strip and dedicated HDMI manager with input status and switching on supported TVs.
- An optional TV-local startup helper for supported configurations. It needs a separate signing and testing step.

## Screenshots

These are browser captures of the 0.7.7 interface using sample weather and simulated HDMI devices. Installed apps and HDMI inputs vary by TV.

| HDMI manager | Three-day forecast |
| --- | --- |
| ![HDMI input manager](docs/screenshots/CleanFrame-0.7.7-hdmi.jpg) | ![Weather forecast and city controls](docs/screenshots/CleanFrame-0.7.7-weather.jpg) |

## Compatibility

Samsung's developer tools confirmed installation and launch on a **UE43RU7102KXXH** running **Tizen 5.0** and firmware **T-MSLDEUC-1500.9**. HDMI switching and weather have browser test coverage. On-device behavior and support across other models may vary. The startup helper was installed on the reference TV. Immediate startup placement and final-build wake behavior remain unverified. See the [test record](docs/CLEANFRAME-TV.md).

## Source and credits

The [0.7.7 patch and build script](samsung/cleanframe/) use a pinned upstream CleanFrame snapshot and only the public font assets. See [the upstream MIT license](samsung/cleanframe/LICENSE) and [third-party notices](samsung/cleanframe/THIRD_PARTY_NOTICES.md). The optional startup service adapts [Free My TV](https://github.com/simbasjungles/free-my-tv) and includes its [MIT notice](samsung/free-my-tv/startup-helper/LICENSE).

## Earlier Samsung TV OS experiments

| Stage | Archived result |
| --- | --- |
| Debian appliance | Graphical media shell, writable data image support, remote navigation, playback and opt-in key-only SSH. Source and rebuild commands are in [the appliance guide](APPLIANCE.md). |
| Coast for Tizen | Remote-focused launcher source and browser simulation in [tizen](tizen/). See [build and deployment notes](docs/DEPLOYMENT.md). |
| Free My TV | v1.5.0 ran on the physical TV. A separate Partner-signed service opened it on wake, with a reported delay of about 30 seconds from the TV picture to the launcher. Earlier Tizen acceptance did not improve the reported visible delay. See [install notes](docs/FREE-MY-TV.md) and [startup timings](docs/FREE-MY-TV-STARTUP-TEST.md). |
| CleanFrame | Local 0.7.7 was installed and launched on the Samsung TV. It includes a centered 24-hour clock, three-day weather panel, and HDMI manager and shortcuts. The separate TV-local startup helper was reinstalled. See [the CleanFrame record](docs/CLEANFRAME-TV.md). |

The earlier Debian appliance targets PCs and virtual machines. See the [appliance guide](APPLIANCE.md) or [research notes](docs/RESEARCH.md) for that work.
