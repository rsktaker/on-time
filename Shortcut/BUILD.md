# Building the On Time shortcut

The iOS app has a settings UI but it cannot create alarms — that capability
is locked to the Shortcuts app. This file is the recipe to build the
companion shortcut **once** on your iPhone, share it via iCloud, and paste
the share URL into `OnTime/Constants.swift` (`shortcutInstallURL`) and the
README.

> **Time to build:** ~10 minutes on iPhone.
> **Tested with:** Shortcuts app on iOS 17 / 18.
> **On macOS Shortcuts:** the same actions and settings exist. Translate "tap" → "click", "long-press" → "right-click", and "tap **(i)** at the bottom" → "click the **info** icon in the toolbar → **Details**".

---

## What it does

1. Reads optional input — a JSON dictionary `{"bufferMinutes": 2, "excludedCalendarTitles": ["Know, Don't Go"]}` — passed by the On Time app's "Run Now" button. If empty (e.g. fired by the daily automation), falls back to the defaults baked into step 3.
2. Deletes every existing alarm.
3. Finds all of today's calendar events that are not all-day and whose calendar isn't in the excluded list.
4. For each event, subtracts `bufferMinutes` from the start time and creates an alarm with the event's title.

That's it — same shape as the original handcrafted shortcut, but parameterized.

---

## Recipe

Open the Shortcuts app → tap **+** → name the shortcut **`On Time`** (this exact name; the app launches it by name). Then add the following actions in order. Action names match the Shortcuts UI verbatim.

### 1 · Read input (with defaults)

| # | Action | Configuration |
| - | ------ | ------------- |
| 1 | **Get Dictionary from Input** | Use **Shortcut Input** as the source. (When run with no input, this returns an empty dictionary — that's fine.) |
| 2 | **Set Variable** | Name: `Config`. Value: `Dictionary` (output of step 1). |
| 3 | **Text** | Type the JSON of your fallback defaults, e.g. `{"bufferMinutes":2,"excludedCalendarTitles":["Know, Don't Go"]}`. |
| 4 | **Get Dictionary from Input** | Source: the **Text** from step 3. |
| 5 | **Set Variable** | Name: `Defaults`. Value: `Dictionary` (output of step 4). |

### 2 · Resolve buffer minutes

| # | Action | Configuration |
| - | ------ | ------------- |
| 6 | **Get Dictionary Value** | Get value for **bufferMinutes** in `Config`. |
| 7 | **If** | If **Dictionary Value** **has any value** |
| 8 |   **Set Variable** | Name: `Buffer`. Value: **Dictionary Value** (from step 6). |
| 9 | **Otherwise** | |
| 10 |   **Get Dictionary Value** | Get value for **bufferMinutes** in `Defaults`. |
| 11 |   **Set Variable** | Name: `Buffer`. Value: **Dictionary Value** (from step 10). |
| 12 | **End If** | |

### 3 · Resolve excluded calendars (list of strings)

| # | Action | Configuration |
| - | ------ | ------------- |
| 13 | **Get Dictionary Value** | Get value for **excludedCalendarTitles** in `Config`. |
| 14 | **If** | If **Dictionary Value** **has any value** |
| 15 |   **Set Variable** | Name: `Excluded`. Value: **Dictionary Value**. |
| 16 | **Otherwise** | |
| 17 |   **Get Dictionary Value** | Get value for **excludedCalendarTitles** in `Defaults`. |
| 18 |   **Set Variable** | Name: `Excluded`. Value: **Dictionary Value**. |
| 19 | **End If** | |

### 4 · Wipe existing alarms

| # | Action | Configuration |
| - | ------ | ------------- |
| 20 | **Find All Alarms** | No filter. |
| 21 | **Repeat with Each** | Source: **Alarms** (output of step 20). |
| 22 |   **Delete Alarm** | Alarm: **Repeat Item**. *(Tap "Show More" → turn off "Confirm Before Deleting".)* |
| 23 | **End Repeat** | |

### 5 · Pull today's events (skip excluded calendars + all-day)

| # | Action | Configuration |
| - | ------ | ------------- |
| 24 | **Find All Calendar Events where** | Filter 1: **Start Date** is **today**. Filter 2: **Is Not All Day**. (Match **All** of the following.) Sort by: None. Limit: off. |
| 25 | **Repeat with Each** | Source: **Calendar Events** (output of step 24). |
| 26 |   **Set Variable** | Name: `Skip`. Value: **0** (text). |
| 27 |   **Repeat with Each** | Source: variable `Excluded`. |
| 28 |     **If** | If **Repeat Item** (inner) **is** **Repeat Item** *(outer — tap "Repeat Item" and choose the calendar event's **Calendar** property)*. |
| 29 |       **Set Variable** | Name: `Skip`. Value: **1**. |
| 30 |     **End If** | |
| 31 |   **End Repeat** | |
| 32 |   **If** | If `Skip` **is** **0**. |
| 33 |     **Adjust Date** | Date: outer **Repeat Item**. Subtract `Buffer` **Minutes**. Output is **Adjusted Date**. |
| 34 |     **Create Alarm** | Alarm time: **Adjusted Date**. Label: outer **Repeat Item**'s **Title**. *(Tap "Show More" if you want to set sound or repeating off.)* |
| 35 |   **End If** | |
| 36 | **End Repeat** | |

> **Step 28 tip:** Inside a nested Repeat, Shortcuts shows the chips as **Repeat Item 1** and **Repeat Item 2**. Which number maps to outer vs. inner is wording-ambiguous in Apple's own docs — tap each chip to see which loop it came from. You want the comparison to be: *(inner) Repeat Item* (a calendar **name** from `Excluded`) **is** *(outer) Repeat Item → Calendar* (the event's calendar name). If you get them swapped, the test still type-checks string-vs-string but won't actually filter; verify with one test run.

---

## Final settings on the shortcut

Open the shortcut's settings panel — on iPhone tap the **(i)** at the bottom; on Mac click the **info** icon in the toolbar → **Details** — and:

- **Show in Share Sheet:** off
- **Show on Apple Watch:** off (unless you want it)
- **Pin in Menu Bar / Add to Home Screen:** optional
- **Receives:** **Text** from **Run Shortcut**, with **No Input** behaviour set to **Continue** (so the daily automation works when no input is supplied)

---

## Test it

1. Tap **▶** at the top — it should run with the baked-in defaults. Open the iOS Clock → Alarms tab. You should see one alarm per non-excluded event today.
2. From the On Time app, tap **Run Now**. The same alarms should regenerate, this time using the buffer/calendar settings from the app.

---

## Share it

1. In the Shortcuts app, long-press **On Time** → **Share** → **Copy iCloud Link**.
2. Paste the URL into:
   - `OnTime/Constants.swift` → `shortcutInstallURL`
   - `README.md` → "Install the shortcut" section.
3. Commit + push. The "Install Shortcut" button in the app will now open the shareable link.

---

## Set up the daily 12:01 AM automation

In **Shortcuts → Automation → +**:

1. **Time of Day** → 12:01 AM, **Daily**.
2. Turn **off** "Run After Confirmation".
3. **Next** → choose **On Time** → **Done**.

That's it. Alarms refresh every night at 12:01 AM with whatever defaults the shortcut has baked in. To override for a single day, open the On Time app and tap **Run Now** — the input from the app overrides defaults for that run only.
