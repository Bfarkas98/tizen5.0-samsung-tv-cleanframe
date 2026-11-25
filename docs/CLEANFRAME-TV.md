# CleanFrame on Samsung UE43RU7102KXXH

Installed on November 25, 2026 over Samsung SDB. The public-font CleanFrame 0.7.0 widget comes from upstream commit `845f332d083502fab39be49869052966103b564a`. The upstream source checkout is in `work/CleanFrame-review`. Both local packages are signed with `TV OS Partner TV`.

- CleanFrame package `8bMXxgJh3O`, foreground app `8bMXxgJh3O.CleanFrameLocal`, signed artifact `work/CleanFrame-local.wgt`.
- CleanFrame Startup package `ClnFrmBoot`, service `ClnFrmBoot.Autostart`, signed artifact `work/CleanFrame-startup.wgt`.

The launcher identity came from a Samsung SDK web project. To reproduce the unsigned builds, run `python -B scripts/export-public.py` in `work/CleanFrame-review`, then `python -B work/build-cleanframe-local.py` from the session workspace. Sign both WGT files using `tz pack --type wgt --base-pkg <unsigned> --out-path <signed> --profiles-path <profiles.xml> --sign-profile "TV OS Partner TV"`. Install each through the ordinary Tizen SDK app installer. The helper uses the TV's loopback power-state endpoint and the Tizen launch API. No PC watcher is needed.

The browser preview, manifest and synthetic adapter checks passed, as did the helper's mocked boot, deduplication and standby/wake scenarios. The TV reported both installs complete and accepted the CleanFrame foreground launch. The developer bridge rejected a direct launch of the service ID with `launch failed[400]`. Automatic wake and visible rendering still need a real TV test.

The TV returned `closed` for the developer uninstall commands targeting Free My TV and Free My TV Startup Test. Both remain listed. The TV accepted an in-place update of the old tester to version 1.0.5 with no web service or launch code. Finish removing the two old entries in **Samsung Apps → Settings**. Keep **CleanFrame Startup** installed for automatic launch. To disable the new automation, remove **CleanFrame Startup** in the same menu.

After reconnecting the SDK, both uninstall commands again returned `closed` for each old package. Fresh app listings confirmed all four package entries.

Local CleanFrame 0.7.1 changes the launcher clock to 24-hour `HH:mm` in both layouts. The upstream widget has no clock-format setting. Midnight, morning, noon, evening and end-of-day formatting passed locally. Samsung reported the in-place update and a manual launch successful. The signed update is `work/CleanFrame-local-24h.wgt`. The actual TV display was not observed.
