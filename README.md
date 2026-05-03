# On Time

> Never be late again. iOS app that creates a phone alarm a few minutes before every calendar event you actually care about.

**On Time** turns your iPhone's calendar into a wall of alarms. Every morning at 12:01 AM, it deletes yesterday's alarms and sets fresh ones — one for each event today, ringing N minutes before the event starts. You pick the buffer and which calendars.

It's the fix for the gap between "calendar reminder you swipe past" and "alarm you can't ignore".

---

## Why this exists

I built the original as an iOS Shortcut for myself. It worked great for a year. People asked for it, so I rebuilt it as a real app with two real settings: **buffer minutes** and **which calendars count**. That's the whole product. No accounts, no cloud, no notifications you'll mute, no analytics.

It is intentionally minimal.

## How it works

iOS does not let third-party apps create alarms. Only the Shortcuts app can. So On Time is two pieces:

1. **The On Time app** — a one-screen settings UI: buffer slider, calendar toggles, "Run Now" button.
2. **The On Time shortcut** — a Shortcuts file you install once. It does the actual alarm-creation work. You can run it manually from the app, automatically every night, or both.

Tapping **Run Now** in the app launches the shortcut and passes your current settings to it. The nightly automation runs the shortcut with no input and uses the defaults baked into it.

## Install

### 1. Download the app
Available on the App Store soon. Until then, [build it from source](#build-from-source).

### 2. Grant calendar access
First launch will ask. Tap allow.

### 3. Install the shortcut

Two paths:

**(a) Prebuilt file (recommended).** Download [`OnTime.shortcut`](OnTime.shortcut) from this repo. Then:

- **On macOS Sequoia:** double-click the file. Shortcuts opens it for review → **Add Shortcut**.
- **On iPhone:** AirDrop the file from your Mac to your iPhone. iOS will offer to import. Requires **Settings → Shortcuts → Allow Sharing Untrusted Shortcuts** turned on (which itself requires you to have run at least one shortcut on the device — open Shortcuts.app and run any built-in once, then the toggle appears).

> The committed `OnTime.shortcut` is generated from `tools/build_shortcut.py`. The Shortcuts plist format is under-documented; if any actions import as **Unknown Action**, swap them in-place — UUIDs and variable wiring are intact.

**(b) iCloud share link** (after the shortcut is published, the in-app **Install Shortcut** button opens this directly): once Ruchir publishes via Shortcuts.app → Share → Copy iCloud Link, the URL is committed to `OnTime/Constants.swift`. Until then, use path (a).

If both paths fail, hand-build using [`Shortcut/BUILD.md`](Shortcut/BUILD.md). ~10 minutes.

### 4. Set up the daily automation
Tap **Set Up Daily Automation** inside the app — it walks you through six taps in the Shortcuts app to schedule a 12:01 AM trigger. Done once, runs forever.

### 5. Tweak settings
- **Buffer** — how many minutes before each event the alarm fires. Default 2.
- **Calendars** — toggle off the ones you never want alarms for (work-only, "maybe" calendars, family calendars you watch but don't attend).

Tap **Run Now** to apply changes immediately for today. Changes carry forward automatically tomorrow.

## Repository layout

```
on-time/
├── OnTime/                   # iOS app source (SwiftUI)
│   ├── OnTimeApp.swift       # App entry point
│   ├── Constants.swift       # Branding strings, contact info, shortcut URL
│   ├── Models/Settings.swift # OnTimeConfig (Codable)
│   ├── Services/             # CalendarService, ConfigStore, ShortcutLauncher
│   ├── Views/                # RootView, ContactView, AutomationGuideView
│   └── Assets.xcassets/      # AppIcon (1024px clock-face), AccentColor
├── OnTime.shortcut           # Prebuilt companion shortcut (XML plist, generated)
├── Shortcut/
│   └── BUILD.md              # Hand-build recipe (fallback / reference)
├── tools/
│   └── build_shortcut.py     # Generator for OnTime.shortcut
├── docs/
│   ├── setup-guide.md        # End-user setup walkthrough
│   └── app-store-submission.md
├── project.yml               # XcodeGen spec
└── README.md
```

## Build from source

Requires macOS with Xcode 15+ and an Apple Developer account (free tier is fine for sideloading to your own device).

```bash
brew install xcodegen
git clone https://github.com/rsktaker/on-time.git
cd on-time
xcodegen generate
open OnTime.xcodeproj
```

In Xcode:
1. Pick a simulator or your connected iPhone.
2. Set your team under **Signing & Capabilities** (free Apple ID is fine for personal device installs).
3. Press **⌘R**.

## Privacy

On Time runs entirely on-device.

- It reads your calendars only to display them in the toggle list and to read event titles when the shortcut runs.
- No event data, settings, or analytics are sent anywhere. There is no server.
- The shortcut only reads today's calendar events and writes to the iOS Clock app's alarms.

## Contact

Questions, feedback, bugs, ideas:

- **Email:** ruchirkavulli@gmail.com
- **Phone:** (408) 465-6442
- **GitHub Issues:** https://github.com/rsktaker/on-time/issues

This is a one-person side project. Replies might be slow but they will come.

## License

[MIT](LICENSE) — do whatever you want with it.
