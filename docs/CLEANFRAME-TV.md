# CleanFrame on Samsung UE43RU7102KXXH

CleanFrame 0.7.7 was installed and launched on November 25, 2026 on Tizen 5.0, firmware T-MSLDEUC-1500.9. The owner approved the final layout. See the [rebuild guide](../samsung/cleanframe/README.md) for the pinned upstream commit, source patch, build and signing steps.

## Update history

Local CleanFrame 0.7.1 changes the launcher clock to 24-hour `HH:mm` in both layouts. The upstream widget has no clock-format setting. Midnight, morning, noon, evening and end-of-day formatting passed locally. Samsung reported the in-place update and a manual launch successful. The actual TV display was not observed.

Local CleanFrame 0.7.2 adds a Home HDMI control in Dock and List, reusing the Samsung input chooser, active/connected status and TV viewer handoff. Weather shows current Celsius conditions on Home and a three-day forecast. The city is editable in Weather, with Budapest as the default. Requests go directly to Open-Meteo from the TV. The most recent forecast can be shown from the local cache. Art Mode remains under Settings → Samsung. The 24-hour clock remains in the build.

Keyboard navigation, the HDMI handoff with mocked Tizen APIs, city search and persistence, and offline cache passed in the browser. A live API test from the PC passed. The TV confirmed installation and accepted the launch. Actual HDMI switching and weather requests from the TV itself still need on-screen verification.

Local CleanFrame 0.7.3 matches the supplied Home reference using the existing photo and glass assets. Dock shows six full app tiles when available, Home weather has forecast icons, and Dock adds an HDMI strip below the apps. Down enters the strip, Left/Right selects, OK switches, and Up or Back returns to apps. The active indicator refreshes on return and the last successfully selected port is remembered locally. The HDMI manager remains available in Dock and List and includes a refresh action.

Browser tests verified the layout, keyboard traversal, exact port routing with mocked Tizen APIs, return refresh, saved input across reloads, and weather behavior. The TV confirmed installation and accepted the app launch. Visible TV rendering and actual input switching still need physical verification. The browser preview uses sample weather and simulated HDMI ports.

Local CleanFrame 0.7.4 replaces the small Home forecast icons with larger columns for Today and the following two days. Today shows the current temperature and later columns show daily forecast highs. The tests checked the day labels, readings, conditions, image size, and cached data on Home. The TV confirmed installation and launch. The preview uses sample weather and HDMI ports.

Local CleanFrame 0.7.5 gives the city and three Home forecast columns a translucent shaded background. Light mode uses a pale panel. The browser flow passed and the TV confirmed the signed update and launch.

Local CleanFrame 0.7.7 follows the user's Paint reference. The Dock menu is centered along the top, the large 24-hour clock is centered underneath it, and the weather panel is lower on the left. The forecast stacks today, tomorrow and the following day. Browser checks verified placement and that a 70-character city name wraps inside the panel without overlapping the Dock. The TV confirmed the signed update and launch.
