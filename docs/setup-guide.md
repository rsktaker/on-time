# Setup guide

A step-by-step from a fresh phone to the first alarm firing.

## What you need

- An iPhone running **iOS 17 or newer**.
- The Shortcuts app (preinstalled on iOS).
- The Calendar app set up with at least one calendar that has events today.

## 1. Install the On Time app

Once it's on the App Store, search "On Time alarm" and install. Until then, see the README's [Build from source](../README.md#build-from-source) section.

## 2. First launch

- Tap **Allow** on the calendar permission prompt. If you tap Don't Allow by accident, fix it from **Settings → On Time → Calendars → Full Access**.
- You'll land on the main settings screen.

## 3. Install the shortcut

Tap **Install Shortcut** inside the app. Safari (or the Shortcuts app) opens the iCloud share link. Tap **Add Shortcut**. Done.

## 4. Set up the nightly automation (one time, ~30 seconds)

In the app, tap **Set Up Daily Automation** and follow the on-screen list:

1. Open Shortcuts.
2. Tap **Automation** (bottom tab).
3. Tap the **+** in the top right.
4. Tap **Time of Day** → set **12:01 AM**, repeat **Daily**.
5. Turn off **Run After Confirmation** (otherwise iOS pings you for a tap each night).
6. Tap **Next** → choose **On Time** → **Done**.

Once configured, you don't need to think about the automation again.

## 5. Pick your buffer

Back in the On Time app, the buffer is how many minutes before each event your alarm rings. Defaults to 2. Try 5 if you tend to need more lead time.

## 6. Pick your calendars

Toggle off any calendars you never want alarms from. Common candidates:

- "Holidays" or "Birthdays" subscriptions
- "FYI" / "Maybe" / "Know, Don't Go" type calendars
- Work calendars during your time off

Toggling is reversible — flip it back any time.

## 7. Tap "Run Now"

This deletes any existing alarms and creates fresh ones for today using the settings you just chose. Open the iOS Clock app → Alarms tab to confirm. You should see one entry per non-excluded event today, each labeled with the event title.

## Daily life

- Calendar events change all day. The 12:01 AM automation rebuilds the next day's wall of alarms from scratch.
- If you add an event for *today* after the nightly run, just open On Time and tap **Run Now**.
- If you change buffer or calendar toggles, tap **Run Now** to apply immediately. The new defaults will also take effect on the next nightly automation run only after you also update the shortcut's baked-in defaults — see the [shortcut build doc](../Shortcut/BUILD.md) for the two text fields to edit.

## Troubleshooting

**"Run Now" opens the Shortcuts app but nothing happens.**
The shortcut name in Shortcuts must match exactly: **On Time** (case sensitive). Rename it if needed.

**No alarms get created.**
Check Shortcuts → On Time → ▶ — when you run it directly, errors appear inline. Most common: the shortcut hasn't been granted permission to "Find Calendar Events" or "Create Alarm". Tap the offending action; iOS will prompt for permission.

**The nightly run doesn't fire.**
- Make sure the personal automation is enabled (Shortcuts → Automation).
- Make sure **Run After Confirmation** is off.
- iOS sometimes shows a banner asking you to confirm the first nightly run — confirm once and it stops asking.

**An excluded calendar still triggers alarms.**
The exclusion match is case-sensitive on calendar **title** (not the calendar's source/account). Verify the exact title under iOS Calendar → Calendars list.
