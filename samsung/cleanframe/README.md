# Build the local CleanFrame adaptation

Use CleanFrame commit [845f332d083502fab39be49869052966103b564a](https://github.com/nthnclrk/CleanFrame/tree/845f332d083502fab39be49869052966103b564a). The adaptation changes the package identity and local clock format. Its separately signed startup app opens CleanFrame from a Tizen Web Service. No native Home integration is part of the build.

1. Export the public-font widget in the pinned CleanFrame checkout with `python -B scripts/export-public.py`.
2. Generate a TV web project in Samsung's SDK. Keep its `config.xml` to reuse the same app ID for future builds.
3. From this archive's root, run:

   ```text
   python -B samsung/cleanframe/build-cleanframe-local.py <upstream-public-unsigned.wgt> <sdk-project-config.xml>
   ```

4. The script writes both unsigned WGT files into `dist/`. Sign them separately with Samsung's SDK using your local device-bound profile. The on-boot service uses a Partner distributor certificate. Install the CleanFrame widget first, then CleanFrame Startup, using the SDK. The TV needs no PC connection at runtime.

See the [TV verification record](../../docs/CLEANFRAME-TV.md) for the exact scope of device checks. The upstream launcher and bundled assets are governed by their own notices. The startup service was adapted from the MIT-licensed Free My TV implementation, with its notice bundled in the helper.
