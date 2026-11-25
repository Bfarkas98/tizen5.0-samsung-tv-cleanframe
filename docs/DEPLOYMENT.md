# Deployment decision and verification

## What was already present

The console ISO is a preserved fallback. The graphical Debian ISO runs LightDM, Openbox, and the Python/Tk shell. The existing library imported JSON documents and displayed their pages. The Tizen source is a separate HTML/CSS/JavaScript app built by the Samsung SDK. Desktop browser fixtures simulated Samsung applications, so they provide no device evidence. The two targets share original artwork and interaction conventions.

## Deployment decision

| Route | Requirements and startup | Input, software and control | Evidence and recovery |
|---|---|---|---|
| Samsung firmware replacement | Needs a verified boot and recovery path for the exact model and firmware family | Hardware drivers and boot support would need independent verification | The manufacturer publishes firmware updates for the 2019 model. No reproducible third-party boot image has been verified for the target. This release provides no Samsung flash image. [Samsung support](https://www.samsung.com/uk/support/) |
| Tizen app | Existing TV OS, Developer Mode allowed for the host PC, device reachable over SDB, current Samsung TV SDK, Samsung account and a TV distributor profile that includes the device DUID. Launch manually from Apps after installing a signed WGT. | Public application enumeration and launch API with `application.info`; directional, Enter and Back events; refresh on visibility change. Startup and Samsung Home assignment are outside the supported workflow here. | SDK and browser tests passed. The TV responded over its public identity API and SDB listed the expected model. Device listing, launching, physical keys and return behavior inside the app still need a signed installation. Uninstall the development app using the SDK if it misbehaves. [Samsung certificate guide](https://developer.samsung.com/smarttv/develop/tools/additional-tools/vscode/creating-certificates.html) |
| **Standalone x86-64 appliance** | Primary target. A PC or VM with BIOS or UEFI, an Xorg-compatible GPU, keyboard or HID remote, and audio output usable by Linux. The live ISO boots into the TV shell after selecting the live entry. HDMI can carry picture and audio from compatible external hardware to the TV. | Local media through mpv, launcher modules, imported JSON apps, persistent data volume, and link diagnostics. The Samsung remains the display and input selector. CEC requires a supported adapter and an input bridge, neither of which is bundled or verified. | QEMU tests are recorded in BUILD-LOG.md. Reboot without the data disk to recover defaults without changing saved data. The live system mounts only the explicitly labeled persistence volume for this purpose and does not install to disk. [Debian Live persistence](https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-run-time-behaviours.en.html) ? [libCEC hardware](https://github.com/pulse-eight/libcec) |

## Hardware checklist

1. Confirm the physical display accepts HDMI from the intended PC and that the requested resolution, the keyboard or HID remote, and the Linux audio output work.
2. For a signed Tizen test, open the Tizen extension's Device Manager and reconnect to the confirmed TV from the authorized PC. Create a **Samsung TV** certificate profile with the TV selected. Complete Samsung account sign-in locally if prompted.
3. Sign and deploy the `tizen/` project using that profile. On the TV, open the app, test direction, OK and Back, launch a visible app, return, and confirm selection and listing still work. Verify each newly tested milestone in the build log. [Samsung TV SDK connection](https://developer.samsung.com/smarttv/develop/tools/additional-tools/vscode/connecting-to-tv-device.html)

## Capability status

| Capability | Status |
|---|---|
| Standalone app lookup and JSON import | Implemented. Tk tests cover imports, missing entries, and focus restoration. |
| Media source and search | Implemented. Tk tests cover folder indexing, filtering and Back. Playback is through the actual player on Linux. |
| Settings, favorites and reordering | Implemented. Tk tests verify order across reload, missing entries, reset and recovery from malformed preference data. |
| Samsung-native launcher | SDK build and browser simulation verified. Device signing, installation and on-device behavior pending. |
| Streaming DRM, HDMI-CEC and native firmware boot | No verification for this project. |

## Samsung deployment milestone

The Samsung branch is the primary target for this milestone. The box/VM remains a separate supported appliance build. Both 0.2 artifact hashes were rechecked, and neither appliance artifact was rebuilt or modified. The delivered appliance is a tested remaster. Its full live-build recipe was syntax-checked and has yet to produce a separately tested full build.

Coast 1.1 shares the wallpaper, focus treatment and visual conventions with the appliance. Its shell uses HTML, CSS and ES5 JavaScript for the 2019 TV engine. It has Home, Library, Search and Settings, with local preferences and a public Tizen platform adapter. The SDK and modern Chromium verification are recorded in BUILD-LOG.md. Simulated app records live only in the test script. A desktop preview without injected test data has an empty library.

### Install and open Coast

1. In the installed VS Code Tizen sidebar, open **Baseline Tools ? Device Manager**. Verify the connected model is the intended TV, then open **Baseline Tools ? Certificate Manager ? Create a new Certificate**.
2. Enter a profile name, choose **SAMSUNG**, and proceed through **Author** and **Distributor**. Use the **Public** privilege level and include the device DUID in the distributor certificate. Complete Samsung sign-in locally if prompted. Success means the profile appears in Certificate Manager and can be selected in **Active Targets**. Keep passwords, DUID, and signing keys local.
3. Select the `tizen` project, the connected TV and the Samsung profile. Use **Build Project** and **Run Project** in the Tizen sidebar. Verify the package is signed by the selected Samsung profile and never substitute the SDK's mobile fallback. This milestone uses the same app ID as Coast 1.0. If the TV reports an existing build with an incompatible signer, stop and inspect upgrade options before removing it. Removing the app may erase its favorites and preferences. [Samsung signing guide](https://developer.samsung.com/smarttv/develop/tools/additional-tools/vscode/creating-certificates.html)
4. Once installed, open **Apps ? TV OS Coast**. Samsung documents **Add to Home** for apps when the option is shown. Confirm that Coast exposes this action on the target TV. Samsung documents **Autorun Last App** for some models and apps, so treat Coast autorun as unverified. Coast does not register or intercept the Samsung Home key. [Samsung app placement](https://www.samsung.com/uk/support/tv-audio-video/how-do-i-manage-apps-on-my-smart-tv/) ? [Samsung autorun settings](https://www.samsung.com/ae/support/tv-audio-video/use-autorun-start-screen-options-on-your-samsung-tv/)

### Physical remote and lifecycle checklist

1. Open Coast from Apps. Use Left/Right to move across sections and Down to enter a shelf. Hold Right in Library. Confirm paging keeps the focused app visible and holding OK does not repeatedly launch it.
2. Open Settings. Toggle wallpaper and return. Open Reset preferences and cancel using Back. Confirm the prompt closes and does not reset the setting. Use the directional on-screen keyboard in Search to find a real installed app.
3. In Library, open a real app's actions and pin it. Pin a second app, move it earlier, then return to Home and confirm order. Choose **Open app** on a real installed entry. Reopen Coast from Apps or its Home shortcut and check focus and favorites. If launch fails, record the label and error shown without uninstalling anything.
4. In Coast, Back exits an action screen, then returns to Coast Home from a secondary section. Back on Coast Home requests app exit. Check the physical Samsung Home button, standby/resume, and a cold restart independently. Reopen Coast after each one and record whether the app remained installed and settings survived. Do not change TV-global settings just to make this test pass.

The device reports Developer Mode enabled and responds to SDB. The installed VS Code extension is 10.4.12, Certificate Manager 10.1.5, the Tizen CLI 10.3.9 and SDB 4.2.36. The device manager previously reported TV 5.0. Samsung documents Chromium M63 for 2019 TV 5.0 models. Coast uses the public `application.info` privilege for enumeration. The API may return an empty list or refuse operations for individual apps. Use Samsung Apps for software not exposed to Coast. [Samsung engine support](https://developer.samsung.com/smarttv/develop/specifications/web-engine-specifications.html) ? [Public app API](https://developer.samsung.com/smarttv/develop/api-references/tizen-web-device-api-references/application-api.html)

Coast launches installed media apps through the same public API. Each app handles its own playback and media keys. Coast does not claim global playback control, has no local-file browser, and does not port the appliance's mpv backend. Samsung documents AVPlay for compatible sources. Player integration should be verified after Coast is installed on the TV. [Samsung AVPlay guide](https://developer.samsung.com/smarttv/develop/guides/multimedia/media-playback/using-avplay.html)
