# Install CleanFrame 0.7.7 on a Samsung TV

This adaptation of [Nathan Clark's CleanFrame](https://github.com/nthnclrk/CleanFrame) installs as a Tizen web app.

## 1. Prepare the TV and PC

- Check your model and firmware in the TV's About or Support screen. The reference TV is a UE43RU7102KXXH running Tizen 5.0 with firmware T-MSLDEUC-1500.9. See the [device test record](../../docs/CLEANFRAME-TV.md).
- Install Git, Python 3, and the Samsung TV development tools for VS Code, including Device Manager and Certificate Manager. Keep the TV and PC on the same local network. [Samsung VS Code SDK guide](https://developer.samsung.com/smarttv/develop/tools/additional-tools/vscode-extension-new.html)
- On the TV, open **Apps**, enter **12345** using the remote or its virtual keypad, enable **Developer Mode**, and enter the PC's local IPv4 address. Restart the TV and connect to its current address in **Device Manager**. Confirm that the model shown in Device Manager is the one you intend to use. [Samsung device connection guide](https://developer.samsung.com/smarttv/develop/tools/additional-tools/vscode/connecting-to-tv-device.html)
- Create a Samsung TV certificate profile. Include this TV's DUID in its distributor certificate and complete Samsung sign-in in Certificate Manager. Authorize the TV for app installation if Device Manager requires it. The launcher uses public privileges. Keep your author key for future updates and store all signing material outside the repository. [Samsung certificate guide](https://developer.samsung.com/smarttv/develop/tools/additional-tools/vscode/creating-certificates.html)

## 2. Build the unsigned widget

Clone or download this repository. In VS Code, create a Samsung TV **web** project in a separate local folder. Its `config.xml` provides the generated package and application IDs. If updating an existing install, use its original manifest and author key to retain that identity.

Open PowerShell at this repository's root, then run the following. Replace the example SDK manifest path.

```powershell
$repo = (Get-Location).Path
$upstream = Join-Path (Split-Path $repo -Parent) 'CleanFrame-upstream-0.7.7'
$identity = 'C:\path\to\your\SDK-web-project\config.xml'
$patch = Join-Path $repo 'samsung/cleanframe/cleanframe-0.7.7.patch'

git clone --config core.autocrlf=false https://github.com/nthnclrk/CleanFrame.git $upstream
git -C $upstream checkout --detach 845f332d083502fab39be49869052966103b564a
git -C $upstream apply --check $patch
git -C $upstream apply $patch

Push-Location $upstream
try { python -B scripts/export-public.py } finally { Pop-Location }

python -B samsung/cleanframe/build-cleanframe-local.py (Join-Path $upstream 'dist/CleanFrame-public-unsigned.wgt') $identity
```

Use a fresh checkout if the target folder already contains another version or local edits. Stop on errors before continuing. The export uses public fonts. The final script prints the local application and package IDs and writes the unsigned launcher widget into the repository's ignored `dist/` directory.

## 3. Sign, install, and test the launcher

Use the SDK's `tz` and `sdb` tools. Replace the example executable paths, profile XML path, and profile name with the values from your own SDK setup. Use the exact serial listed by `sdb devices` for the TV you connected in Device Manager.

```powershell
$tz = 'C:\path\to\sdk\tz.exe'
$sdb = 'C:\path\to\sdk\sdb.exe'
$profiles = 'C:\path\to\your\profiles.xml'
$profile = 'My Samsung TV profile'
$unsigned = Join-Path $repo 'dist/CleanFrame-local-unsigned.wgt'
$signed = Join-Path $repo 'dist/CleanFrame-local.wgt'

& $tz pack --type wgt --base-pkg $unsigned --out-path $signed --profiles-path $profiles --sign-profile $profile
& $sdb devices
$serial = '<TV serial listed by sdb devices>'
& $tz install --serial $serial --package-path $signed
```

Check that signing and install succeeded, then open **CleanFrame** from the TV's **Apps** screen. Test arrow keys, OK, Back/Return, app launches, live weather, and a connected HDMI input. Weather uses an editable city and sends forecast and city-search requests to Open-Meteo. The app can show its cached forecast when offline.

If the SDK reports an install or signature failure, save the exact error, then verify the selected TV, distributor DUID, device authorization, and signing profile before rebuilding. Keep credentials, DUIDs, local IPs, and signed widgets out of bug reports. If needed, remove the launcher through **Samsung Apps → Settings**. [Samsung install troubleshooting](https://developer.samsung.com/smarttv/develop/tools/additional-tools/vscode/connecting-to-tv-device.html)

## Credits

- [Original CleanFrame project and source](https://github.com/nthnclrk/CleanFrame)
- [CleanFrame MIT license](LICENSE) and [third-party asset notices](THIRD_PARTY_NOTICES.md)
