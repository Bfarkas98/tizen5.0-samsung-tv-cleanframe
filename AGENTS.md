# Install this CleanFrame build with an AI agent

Give the agent this file or point it at the repository and use this prompt:

> Help me install the custom CleanFrame 0.7.7 Tizen app in this repository on my Samsung TV. Follow AGENTS.md and the linked installation guide. Reuse my local Samsung SDK setup if possible. Start with manual launch and guide me through the steps that require my TV remote or Samsung sign-in.

## Agent instructions

1. Read the [installation guide](samsung/cleanframe/README.md) and [TV test record](docs/CLEANFRAME-TV.md). The reference install is a Samsung UE43RU7102KXXH, Tizen 5.0, firmware T-MSLDEUC-1500.9. Treat other devices as unverified and record the actual model and firmware.
2. Inspect the PC for Git, Python 3, Samsung's TV SDK, Device Manager and Certificate Manager. Reuse existing tools. Confirm the target with the owner if multiple TVs are connected. Guide the owner through Developer Mode, entering the PC address and Samsung sign-in when needed. Let them enter signing passwords directly in their local tools.
3. Use the pinned upstream [CleanFrame](https://github.com/nthnclrk/CleanFrame) commit and the repository's patch. Apply it in a separate checkout. Export the public-font widget and use a Samsung SDK-generated `config.xml` for the target identity. For an update, preserve the original application ID and author certificate.
4. Build and sign locally with the correct Samsung TV certificate. Confirm the target in Device Manager or `sdb devices` before installing. Install the launcher. Use normal SDK procedures and keep this task within app installation. Leave any existing Home assignment, firmware, and system apps alone.
5. Have the owner launch the app manually and report on navigation, Back/Return, apps, live weather and a connected HDMI source. Record separately what the SDK confirmed and what the owner saw. If a step fails, capture the exact sanitized error and diagnose it before retrying.
6. Keep certificates, passwords, signing profiles, DUIDs, local addresses, signed widgets, and private SDK data out of Git and shared logs. Report the app version, model, tested behavior, and any blocker. Show how to remove the app in Samsung Apps settings.
