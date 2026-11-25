# Graphical build and test log

- The original console build could start on a blank display. The console launcher was corrected to render through curses and passed a later QEMU boot test.
- WSL registration is scoped to the interactive Windows account. The automation account could not see it, so the graphical build was attempted through an isolated QEMU Debian guest.
- The first guest serial attempt dropped characters. The second accepted typed characters but did not submit carriage returns. The controller was changed to throttle each character and submit line feeds.
- The first app importer needed separate Windows and Linux rename paths because Windows cannot replace an open temporary file. It now closes the temporary file before performing the same atomic replacement on both platforms.
- Windows Tk tests passed for rendering, navigation, manual sample import, page navigation, library reload, updates, invalid package rejection, and selection across multiple tile pages.
- Samsung SDB listed the expected test TV as connected over the local developer transport.

- The first graphical ISO built and booted. Its title screen appeared, but keyboard navigation did not respond. Several symbols also appeared as question marks in the Linux session.
- The launcher now uses a managed fullscreen window, requests keyboard focus after mapping, and draws its icons from shapes. The session explicitly sets a UTF-8 locale. Windows smoke tests passed again after these changes.
- The initial graphical ISO passed the VM SSH test. SSH was off by default, key authentication opened a shell as the live user, and root login was rejected.
- Hardware acceleration through WHPX succeeded and replaced the slower software-emulated build attempt.

- The first repack attempt expected an MD5 manifest. The image contains a SHA-256 manifest. I updated the actual SquashFS entry and replayed both boot configurations when repacking.
- The first vector-icon pass assigned the library icon to all tiles. Icon selection now uses the tile ID. The final QEMU screenshot shows four distinct icons, including the imported Field Guide.
- The final image booted via BIOS and UEFI in QEMU. The BIOS test opened System, imported Field Guide with the real file chooser, opened both pages, and returned to Home.
- The UEFI check used separate read-only firmware and writable variable flash devices after the single-file BIOS invocation failed.
- Delivered image SHA-256 is F95614F7D197CD069140577BFED36DBD4DA952E8611BEBA61330ECFA10F1FD72.
- The live image is an x86-64 VM or PC build. Native Samsung boot and physical remote input were outside this validation.

## Landscape redesign and Samsung app

- Reviewed custom-tv, Apps2Samsung, Quiet Tizen, CleanFrame, and other topic projects. Model-specific evidence and design choices are in RESEARCH.md.
- Tk could not open the artwork by path in the Windows sandbox. Loading the validated PNG bytes through Python fixed the preview and the smoke test.
- The first VM screenshot showed blocky wallpaper from Tk's combined zoom and subsample operation. The revised renderer crops the original pixels when the image covers the screen and uses integer scaling for larger screens.
- Chromium tests passed for the new Tizen app's preview, directional focus, paging, mocked app discovery and launch, error handling, and Back.
- The installed Tizen SDK built and packed a test WGT. It used fallback certificates, including a mobile author certificate. A Samsung TV signing profile for the physical device was unavailable, so the test WGT was kept in scratch and was not sent to the Samsung.

- The revised landscape image booted through BIOS and UEFI in QEMU. BIOS screenshots verified manual Field Guide import, opening page two, and returning to Home. UEFI screenshots verified that the revised home screen appeared.
- Delivered landscape ISO SHA-256 is C0B42EDD4E85465EB231C9EE577F47E4F5A18C6AE5372FE4CB854EBC8973568F.

## Appliance 0.2

- Inspected the previous tree and verified the Coast ISO hash against the earlier build log. The console and Coast images were retained. The primary target is the x86-64 live appliance. The Samsung TV app is secondary.
- Windows Tk tests passed for app import, favorites ordering and reload, missing apps, indexed search, focus restoration, reset, malformed settings, canceled file selection, unsupported playback and failed player launch. The Tk UI was also exercised at a requested 1920 by 1080 window size.
- The released ISO reached the graphical shell through standard QEMU BIOS and UEFI boot. The deployment run was a remaster of the verified Debian image with updated packages and source. The full live-build recipe was updated and syntax-checked, but a separate full rebuild was not used to produce this release.
- The diagnostic QEMU test used a separate copy of the data image, with /home mounted from the labeled ext4 disk. The actual shell wrote the wallpaper preference and a second boot read the same setting. The delivered data image is clean.
- Initial media smoke checks hit three test-harness issues. The live guest lacks wget, a QMP key alias was incorrect, and QEMU's WAV backend left the RIFF lengths unset on exit. The test used Python file transfer, the Enter key, and checked the captured PCM payload directly.
- Initial video output worked but the guest PulseAudio sink was muted. The shell now reports the real default sink state and provides working mute and volume actions. The final test used those controls, played a locally generated VP8/Opus clip, sought and returned to Home, then confirmed the player process exited. QEMU captured 716060 non-silent PCM samples. No physical HDMI audio or hardware acceleration was tested.
- The target Samsung returned the expected identity and Developer Mode enabled through its public API. SDB independently listed the same model. No WGT was deployed or system settings changed on the TV. The current PC had no Samsung TV signing profile at the SDK's default path.
- Appliance ISO SHA-256 is FF7374B69BEFF611D3A07C80983A3D51C506A20A28660C7631A8F8F35DA0D6F7.
- Clean data image SHA-256 is EAB2C927D28687B149D47E2CBF67679800D1B6CF410C44DE060A0E5775F04748.

## Samsung Coast 1.1 deployment milestone

- Reconnected SDB and verified the device's model and Developer Mode through its public API. Preserved both 0.2 artifacts and matched their previous SHA-256 values.
- Verified the installed Tizen VS Code extension and Certificate Manager UI. The manager displayed no profiles and VS Code showed No Active Certificate. Opened the Samsung certificate creation wizard and requested only the local signing step.
- Built the new launcher in a scratch staging directory using `tz build --proj-dir <staging-folder>`. Validated all eight built assets and packaged them as explicitly unsigned WGT content. Did not use the generic SDK fallback certificate.
- Ran the automated desktop Chromium test against SDK-built files at 1920x1080. It covered empty runtime state, navigation, paging, mocked discovery and launch errors, focus, favorite order and persistence across browser reload, removed apps, search, settings reset and malformed stored data. A first run after adding Enter debounce exposed the test pressing OK faster than the guard. Added realistic key spacing to the test and reran it successfully.
- Samsung installation, launch, physical remote, suspend/resume, cold restart, and Tizen on-device persistence remain blocked by signing. The browser screenshots contain injected test data. No WGT was installed and no TV settings were changed.
