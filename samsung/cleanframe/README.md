# Build the local CleanFrame adaptation

Use CleanFrame commit [845f332d083502fab39be49869052966103b564a](https://github.com/nthnclrk/CleanFrame/tree/845f332d083502fab39be49869052966103b564a). The archived 0.7.7 patch adds the HDMI manager and shortcuts, three-day weather, and the final Dock layout. The build script sets the local package identity and 24-hour clock. Its separately signed startup app opens CleanFrame from a Tizen Web Service. No native Home integration is part of the build.

1. In a clean checkout of the pinned upstream commit, apply this archive's `samsung/cleanframe/cleanframe-0.7.7.patch`. Replace the example path with the absolute path to your archive checkout.

   ```text
   git apply --check <archive-path>/samsung/cleanframe/cleanframe-0.7.7.patch
   git apply <archive-path>/samsung/cleanframe/cleanframe-0.7.7.patch
   python -B scripts/export-public.py
   ```

   The export writes `dist/CleanFrame-public-unsigned.wgt`.
2. Generate a TV web project in Samsung's SDK. Keep its `config.xml` to reuse the same app ID for future builds.
3. From this archive's root, run:

   ```text
   python -B samsung/cleanframe/build-cleanframe-local.py <upstream-public-unsigned.wgt> <sdk-project-config.xml>
   ```

4. The script writes both unsigned WGT files into `dist/`. Sign them separately with Samsung's SDK using your local device-bound profile. The on-boot service uses a Partner distributor certificate. Install the CleanFrame widget first, then CleanFrame Startup, using the SDK. The TV needs no PC connection at runtime.

See the [TV verification record](../../docs/CLEANFRAME-TV.md) for the exact scope of device checks. The upstream launcher and bundled assets are governed by the upstream [MIT license](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md). The startup service was adapted from the MIT-licensed Free My TV implementation, with its notice bundled in the helper.
