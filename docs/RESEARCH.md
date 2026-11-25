# Samsung TV project research

The test target is a 2019 RU-series Samsung. Keep exact device identifiers in local notes. Samsung Device Manager reported TV 5.0. Samsung documents Chromium M63 for 2019 TV Web apps. Source for the new on-device launcher uses plain JavaScript and Flexbox and targets TV 5.0 in the manifest. Desktop Chromium tests exercise the behavior. They do not establish the old TV engine or hardware behavior.

| Reference | What its project demonstrates | What it changed here |
| --- | --- | --- |
| [custom-tv](https://github.com/berteotti/custom-tv) | Full-screen landscape, one app row and remote navigation in a normal Tizen Web app | Original full-bleed wallpaper, a restrained app shelf, and visible remote focus. Weather was omitted to keep this version usable offline. |
| [CleanFrame](https://github.com/nthnclrk/CleanFrame) and [compatibility record](https://github.com/nthnclrk/CleanFrame/blob/main/docs/compatibility.md) | A Web launcher with a 2019 Tizen 5.0 owner report for running and opening apps on a different model | Implement a native Web-app-sized test on the 2019 Samsung and verify its actual app list before promising compatibility. |
| [Apps2Samsung](https://github.com/Apps2Samsung/Apps2Samsung) | A desktop installer and catalog for Tizen applications | Keep installation as a PC-side workflow. The native launcher discovers apps already installed on the TV. The Debian build has its own local app import. |
| [Quiet Tizen](https://github.com/jss8649/quiet-tizen) | An on-device launcher and controls for a 2025 U8000F on Tizen 9 | Its platform differs from the target TV. Keep the 2019 build on Samsung's public Web API and use the newer project only as a design reference. |
| [abhaymundhara/samsung-tizen-launcher](https://github.com/abhaymundhara/samsung-tizen-launcher) | Photographic backdrops, remote focus, configurable docks and scoped visual tests | Keep a clearly defined focused tile and test across a full TV viewport and a smaller 16:9 viewport. |
| [ToMeXaS/tv-launcher](https://github.com/ToMeXaS/tv-launcher) | A documented Left/Right/OK flow, local pictures, and readable clock overlays | Add local time to the native launcher and keep directional selection consistent across both prototypes. |

There are two build targets. `TV-OS-Visual-amd64.iso` is the standalone Debian system for a PC or VM. `tizen/` is the Web app source for Samsung's existing Tizen OS. None of the reviewed projects established a replacement boot image for the target model. A signed package and real TV test are required for the native branch.

Samsung documentation: [2019 Web engine](https://developer.samsung.com/smarttv/develop/specifications/web-engine-specifications.html), [Application API](https://developer.samsung.com/smarttv/develop/api-references/tizen-web-device-api-references/application-api.html), [Remote keys](https://developer.samsung.com/smarttv/develop/guides/user-interaction/remote-control.html), [Certificate setup](https://developer.samsung.com/smarttv/develop/tools/additional-tools/vscode/creating-certificates.html).
