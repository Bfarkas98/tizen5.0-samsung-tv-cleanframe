# Free My TV startup test

On November 25, 2026, the Samsung UE43RU7102KXXH responded over SDB and reported Tizen 5.0. Developer Mode was enabled and the configured Host PC IP matched the connection.

The startup helper has its own Tizen package, `FMyTVBoot1`, and opens the working Free My TV v1.5.0 app at `FreeMyTVio.FreeMyTV`. Its web service uses the TV's loopback API to detect power state and is configured to start at boot. The foreground helper has a manual launch button for diagnosis. The service comes from the [pinned Free My TV startup fork](https://github.com/MKsys1337/free-my-tv/blob/b8847dda43702ed1376932730061d16fbbbaaf85/tizen/AUTOSTART.md).

## Build and validation

Source is in `work/free-my-tv-startup-test`. Its contents were zipped at the root of an unsigned WGT and signed with Samsung's `tz pack --type wgt --base-pkg <unsigned-wgt> --out-path <signed-wgt> --profiles-path <profiles.xml> --sign-profile "TV OS Partner"`. The signed file is `work/FreeMyTV-startup-test.wgt`. Local ZIP and JavaScript checks passed. A mocked sequence confirmed one launch request at startup, one on standby-to-on and no repeats while the TV stays on. The WGT's signature contains a Samsung VD Author certificate and a Samsung VD Developer Partner distributor certificate.

## Target TV result

Run `python -B work/install-free-my-tv-startup-test.py TV_IP` from the session workspace. The installer checks the artifact SHA-256, TV identity, Tizen version and Developer Mode before staging and installing only the helper.

The first install reached the TV and failed during certificate validation. The TV reported `install failed[118, -12], reason: Check certificate error : :Invalid format of certificate in signature.:<-2>`. Free My TV v1.5.0 was left in place. Check the TV's internet connection and clock, then check Samsung's device authorization and the distributor profile's device binding if the error persists. An online retry resolved this error on a different TV. [Certificate rejection report](https://github.com/Apps2Samsung/Apps2Samsung/issues/907)

After Device Manager reported successful certificate authorization, Samsung's SDK connected and the install reached a different error, `Invalid signature ... <-4>`. Repeating with the exact package ID gave the same error. Both RSA signatures and all package file digests verified locally. The distributor certificate and its device-profile XML agree with one another, but the connected TV returned a different DUID through SDB. No DUID was saved to these notes. The package listing confirmed the original app was installed and the startup helper was absent. Renew the Samsung Partner distributor certificate for the connected TV's DUID, authorize it using Device Manager, then re-sign and verify the helper before retrying. A plain app signed with the current profile was prepared for diagnosis and was left off the TV after the DUID mismatch was confirmed.

The owner created and authorized `TV OS Partner TV`. Re-signing the unsigned helper with that profile produced `work/FreeMyTV-startup-test-corrected.wgt` (SHA-256 `ad1f6f0d0845b2978825f4b1011aafb317291503b02c4707c4057de2457d9853`). Verified that the Samsung Partner distributor signature contains the current TV's DUID and that the manifest names `FMyTVBoot1`. Using Samsung SDB at the verified serial `TV_IP:26101`, pushed that WGT into `/home/owner/share/tmp/sdk_tools/` and ran `0 vd_appinstall FMyTVBoot1 /home/owner/share/tmp/sdk_tools/FreeMyTV-startup-test-corrected.wgt`. The TV reported `install completed`. The SDB app listing confirmed both `FMyTVBoot1` and `FreeMyTVio`. Do not use the earlier installer script's pinned build for this profile.

The new profile uses the author key in the old `TV OS Partner` directory and the distributor key in `TV OS Partner TV`. Preserve both keys for future signed updates. `TV OS Coast` is independent of the startup helper and retains the author key for Coast builds.

The owner confirmed that Free My TV opened automatically on the target TV. The exact launch delay, power-off duration, and PC state were not reported. A separate cold boot with the PC off and repeatability checks are pending.

## Faster wake check

Built and installed helper version 1.0.1 on the same TV. The signed WGT is `work/FreeMyTV-startup-test-1.0.1.wgt` (SHA-256 `817dc43d83b6047e0fb14ff948fa80ec8ee0e979c213322f9644e7cdb58641bd`). It uses the same author and distributor certificates as 1.0.0. The TV confirmed the update and listed both packages.

The service now checks every 250 ms during standby and while waiting for its first power state. It checks every second once the TV is on. The polling change can remove up to 750 ms of idle wait during a normal wake with responsive loopback requests. Tizen service startup and app rendering time are separate. A mocked test checked the new intervals, overlapping requests, one launch per wake, and shutdown with a request in flight. A new end-to-end wake time has not been measured on the TV.

## Timing the remaining delay

The owner reported that the TV picture appears about 30 seconds before Free My TV. Installed helper 1.0.2 from `work/FreeMyTV-startup-test-1.0.2.wgt`. The launch behavior of 1.0.1 is retained. The service now records its start time, reported power-state changes, and when Tizen receives and accepts or rejects the launch request. The helper's **Last startup timing** screen reads the latest events via a trusted Tizen MessagePort. The events stay in the service's memory.

Mocked standby-to-wake, launch, timing exchange and listener cleanup passed. The TV confirmed the update and listed both packages. A real wake timing report is pending. For the test, note when the TV picture first appears, wait for Free My TV, then open **Free My TV Startup Test** from Samsung Apps and capture the timing lines. [Samsung MessagePort API](https://developer.samsung.com/smarttv/develop/api-references/tizen-web-device-api-references/messageport-api.html)

The owner's timing photo showed service start at 19:35:27.320, the first `on` report at 19:35:42.907, a launch request at 19:35:42.953, and Tizen acceptance at 19:35:45.907. The measured power-state wait was 15.587 seconds, followed by a 46 ms dispatch interval and 2.954 seconds for Tizen to accept the request. The photo did not measure when the TV picture appeared or when Free My TV became visible.

Helper 1.0.3 now tries one launch 500 ms after the boot service starts if it has yet to receive a usable power state. An explicit standby report cancels the timer. If the early request fails or has no callback after 8 seconds, the service can try once after confirmed power-on. An accepted early request suppresses a second launch for the same observed wake. Mock tests checked success, standby, rejection, timeout, delayed callbacks and exit. The target TV confirmed the update and listed both packages. The new wake latency still needs a physical test. The signed WGT is `work/FreeMyTV-startup-test-1.0.3.wgt` (SHA-256 `a0630d05723bedb6ebb658f97d79a823cf7ea4eab3db506929d54710c7ba997d`).

The owner's 1.0.3 timing photo showed service start at 19:39:54.894, early launch request at 19:39:57.281, Tizen acceptance at 19:40:02.711 and the first `on` report at 19:40:10.931. The acceptance came 7.817 seconds after service start, compared with 18.587 seconds in the previous test, a 10.770-second improvement in that measured interval. Tizen accepted the early request 8.220 seconds before the status API reported power-on. No fallback launch appeared in the trace. A picture-to-app timing measurement is still pending.

The owner subsequently reported that the picture-to-app delay still felt the same, about 30 seconds. Installed helper 1.0.4 to time the first running application context for Free My TV using Samsung's documented `getAppsContext()`. It samples only during the first 45 seconds after a launch request, keeps at most one pending query, and records only whether the target app was found. The test passed with simulated missing and present context, standby cancellation, and timeout. The TV confirmed installation. The updated report is pending. A running app context does not establish the time of first visible content. [Samsung Application API](https://developer.samsung.com/smarttv/develop/api-references/tizen-web-device-api-references/application-api.html)

The Free My TV v1.5.0 startup code initializes the top area first, then waits for Samsung's installed-app and input callbacks before rendering the full launcher. If the TV reports a running context substantially before the app becomes visible, a separate instrumented app can measure first script, first foreground visibility, and the app/input callback path. Keep the publisher-signed app and its settings separate from any diagnostic build.

To roll back after a successful install, remove **Free My TV Startup Test** from Samsung Apps settings. Its package ID is `FMyTVBoot1`.
