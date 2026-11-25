# Free My TV normal-app test

## Package and compatibility

- Upstream release v1.5.0, tag commit `0e33f168b82ffb05d002b3ab9093f12048bdfc92`. The release WGT identifies package `FreeMyTVio` and app `FreeMyTVio.FreeMyTV`. Its manifest requires Tizen 2.3 or newer. Both package signature files are present. SHA-256 matches GitHub's release asset digest `2b0215ca6e0776106e71a983cf63023e726bf83c1dc337e6e0102b0b15e1cae9`. [Release](https://github.com/simbasjungles/free-my-tv/releases/tag/v1.5.0)
- The pinned Python installer's documented test list includes a 2019 UN55RU7100 on Tizen 5.0. That is an adjacent-model precedent. The release notes call out limited testing of the new channel privilege. No verified Free My TV normal-app result for the exact target firmware was located. [Pinned installer](https://github.com/simbasjungles/free-my-tv/blob/v1.5.0/tizen/install.py)
- The exact release WGT was checked for an enabled optional Home watcher. It is disabled. The release has no bundled TMDB key. The installer transfers the signed app through SDB over TCP 26101, runs the TV's developer app install command, and requests launch. It makes no system or startup changes. It uses only Python's standard library. No new certificate has been requested because the publisher supports the signed release route for this generation. If the TV rejects the publisher's signature, stop and assess Samsung TV signing with the device selected.

## Procedure

1. Turn the TV on and verify the target model with its read-only device information API. Verify the current PC Ethernet IPv4 is the Host PC IP in the TV's Apps developer screen and that Developer Mode is on. Reboot only if a Developer Mode setting is changed and the TV prompts for it.
2. In a checkout pinned to the release, place the publisher's verified `FreeMyTV-tizen.wgt` at the checkout root. Inspect `tizen/install.py` before using it. Run `python tizen/install.py TV_IP` from the PC after verifying identity. Capture its output. Look for the TV's install result. The script's final launch message alone does not confirm a visible UI.
3. Use **Samsung Home → Apps → Free My TV** to test manual launch. Verify the app name and version where available.
4. If cleanup is wanted, remove only **Free My TV** through **Apps → Settings → Free My TV → Delete**. The pinned installer also documents `--uninstall` for that one package. Deleting the app can erase its local settings.

## Test log

| Check | Result |
|---|---|
| Local prerequisite | Existing Python 3 and Samsung SDB available. No additional installer or SDK required for the publisher's Python route. |
| Published package | Downloaded from the release, checksum matched, archive integrity and manifest checked, and pinned installer inspected and syntax-checked. |
| Current device identity and developer connection | Confirmed on November 25, 2026 after an initial timeout. The API identified the expected 2019 RU-series model on MuseL, Developer Mode enabled, and Host PC IP matching the Ethernet PC. A retried direct SDB handshake reported Tizen 5.0. The API did not report a firmware version. |
| Install and manual launch | The pinned Python installer completed successfully using the verified publisher WGT and requested launch. The device package listing independently shows package FreeMyTVio. The status API reports installed version 1.5.0. It reported not running and not visible. A separate developer launch returned app_id[FreeMyTVio] launched, but three follow-up status requests still returned running=false and visible=false. The reason for the disagreement is unverified. Manual launch and visible rendering still need physical confirmation. |
| Remote, focus, Back, app launch, HDMI, rendering and settings | Untested on the target. |

If the package manager responds `download failed[116]`, record the exact error. Upstream associated that code with storage on a different TV. Do not remove other apps. A certificate or privilege error has a different diagnosis. [Upstream install failure report](https://github.com/simbasjungles/free-my-tv/issues/490)

## Connection and install notes

The first SDB attempt after the TV became reachable reset the connection. A standalone retry worked. The installed Windows sdb executable failed to start with Illegal System DLL Relocation. The upstream Python installer establishes its own SDB connection and succeeded without that executable. No separate signing, firmware, Home integration, or startup step was used.

## Physical test after install

1. Open Free My TV from Apps. Note time to first usable screen and any blank screen, rendering issue or freeze.
2. Move in all four directions, hold Right briefly, open an in-app settings panel, and press Return to close it. Press Return from the main view and note the Samsung screen you land on.
3. Reopen Free My TV. Open one installed app from its library. Return via Samsung Apps. If an attached HDMI input is listed, select it and confirm the active source changes.
4. Change one reversible in-app preference, exit, reopen and check whether it was retained. Keep the Home feature and Autorun settings untouched.

After that passes, collect a separate standby and cold-start baseline without changing settings. Evaluate Samsung-supported Home shortcut placement and startup options separately. Upstream reports that Autorun Last App does not reopen Free My TV on some 2019/2020 sets. [Upstream standby report](https://github.com/simbasjungles/free-my-tv/issues/356)


## Separate TV-side startup experiment

The owner confirmed the installed v1.5.0 application works. Details of the individual remote and HDMI checks were not provided.

For TV-only startup, pinned the reported Web Service fork at b8847dda43702ed1376932730061d16fbbbaaf85. The opt-in build produced an unsigned v1.2.0 WGT with on-boot enabled and the original package ID. Its service logic passed a mocked on / standby / on test. This source build is older than the working v1.5.0 and was not installed.

The installed TV OS Coast profile signed an offline probe successfully. Its distributor leaf is issued by the Samsung VD Developer Public CA. The reported boot service requires a Samsung Partner distributor certificate registered to the test TV. Prepare that signing profile locally before deploying any boot service. A separate test package is preferred for the first device test so the working Free My TV package and its app data can be preserved.

Once a Partner profile is available, verify the signature level, install the separate test package, record one short standby/wake and one cold boot with the PC inactive, and check that choosing another app does not cause a relaunch. No watcher was started on the PC. No installed app or TV setting was changed during preparation.

[Reported fork instructions](https://github.com/MKsys1337/free-my-tv/blob/b8847dda43702ed1376932730061d16fbbbaaf85/tizen/AUTOSTART.md) · [Samsung Partner test certificates](https://developer.samsung.com/smarttv/develop/faq/privileges.html)
