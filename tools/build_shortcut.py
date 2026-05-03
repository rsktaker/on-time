#!/usr/bin/env python3
"""
Generate OnTime.shortcut as an unsigned XML plist.

Status: best-effort. The Shortcuts plist format is under-documented; some
action identifiers and parameter shapes are inferred from public reverse-
engineering. After import in Shortcuts.app, scan for "Unknown Action"
placeholders and replace them in-place — UUIDs, variable references,
conditional groupings, and the repeat structure are wired up correctly,
so only the per-action params should need any touch-up.

Run:
    python3 tools/build_shortcut.py
Outputs:
    OnTime.shortcut (XML plist) at the repo root.
"""
from __future__ import annotations

import os
import plistlib
import uuid
from typing import Any


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def U() -> str:
    return str(uuid.uuid4()).upper()


def ref_output(action_uuid: str, output_name: str = "Result") -> dict[str, Any]:
    """Magic-variable reference to a previous action's output."""
    return {
        "Value": {
            "OutputUUID": action_uuid,
            "OutputName": output_name,
            "Type": "ActionOutput",
        },
        "WFSerializationType": "WFTextTokenAttachment",
    }


def ref_named(name: str) -> dict[str, Any]:
    """Reference to a named variable (set via Set Variable)."""
    return {
        "Value": {"VariableName": name, "Type": "Variable"},
        "WFSerializationType": "WFTextTokenAttachment",
    }


def ref_repeat_item(repeat_uuid: str) -> dict[str, Any]:
    """The implicit Repeat Item variable inside a Repeat with Each."""
    return ref_output(repeat_uuid, "Repeat Item")


def ref_extension_input() -> dict[str, Any]:
    """The Shortcut Input variable."""
    return {
        "Value": {"Type": "ExtensionInput"},
        "WFSerializationType": "WFTextTokenAttachment",
    }


def with_property(att: dict[str, Any], prop: str,
                  coercion: str = "WFCalendarEventContentItem") -> dict[str, Any]:
    """Add a property aggrandizement: e.g. an event variable's .Calendar / .Title."""
    out = {"Value": {**att["Value"]}, "WFSerializationType": att["WFSerializationType"]}
    out["Value"]["Aggrandizements"] = [{
        "CoercionItemClass": coercion,
        "PropertyName": prop,
        "Type": "WFPropertyVariableAggrandizement",
    }]
    return out


def text_string(s: str) -> dict[str, Any]:
    return {"Value": {"string": s}, "WFSerializationType": "WFTextTokenString"}


# --------------------------------------------------------------------------
# Action emitter
# --------------------------------------------------------------------------

actions: list[dict[str, Any]] = []


def emit(identifier: str, params: dict[str, Any] | None = None,
         output_name: str | None = None) -> str:
    p = dict(params or {})
    uid = U()
    p["UUID"] = uid
    if output_name:
        p["CustomOutputName"] = output_name
    actions.append({
        "WFWorkflowActionIdentifier": identifier,
        "WFWorkflowActionParameters": p,
    })
    return uid


# --------------------------------------------------------------------------
# Recipe (matches Shortcut/BUILD.md, with all literals routed through
# Number/List actions before Set Variable, per Shortcuts' actual semantics)
# --------------------------------------------------------------------------

# Defaults
default_buffer = emit(
    "is.workflow.actions.number",
    {"WFNumberActionNumber": 2},
    output_name="Default Buffer",
)
default_excluded = emit(
    "is.workflow.actions.list",
    {"WFItems": [{"WFItemType": 0, "WFValue": text_string("Know, Don't Go")}]},
    output_name="Default Excluded",
)

# Get input dictionary (empty if no input)
input_dict = emit(
    "is.workflow.actions.detect.dictionary",
    {"WFInput": ref_extension_input()},
    output_name="Input Dict",
)

# bufferMinutes: input value → Buffer, else default
in_buffer = emit(
    "is.workflow.actions.getvalueforkey",
    {
        "WFDictionaryKey": "bufferMinutes",
        "WFInput": ref_output(input_dict, "Dictionary"),
        "WFGetDictionaryValueType": "Value",
    },
    output_name="Input Buffer",
)
buf_grp = U()
emit("is.workflow.actions.conditional", {
    "GroupingIdentifier": buf_grp,
    "WFControlFlowMode": 0,
    "WFCondition": 100,  # has any value
    "WFInput": {"Variable": ref_output(in_buffer, "Dictionary Value")},
})
emit("is.workflow.actions.setvariable", {
    "WFVariableName": "Buffer",
    "WFInput": ref_output(in_buffer, "Dictionary Value"),
})
emit("is.workflow.actions.conditional", {
    "GroupingIdentifier": buf_grp,
    "WFControlFlowMode": 1,
})
emit("is.workflow.actions.setvariable", {
    "WFVariableName": "Buffer",
    "WFInput": ref_output(default_buffer, "Number"),
})
emit("is.workflow.actions.conditional", {
    "GroupingIdentifier": buf_grp,
    "WFControlFlowMode": 2,
})

# excludedCalendarTitles: input value → Excluded, else default list
in_excl = emit(
    "is.workflow.actions.getvalueforkey",
    {
        "WFDictionaryKey": "excludedCalendarTitles",
        "WFInput": ref_output(input_dict, "Dictionary"),
        "WFGetDictionaryValueType": "Value",
    },
    output_name="Input Excluded",
)
excl_grp = U()
emit("is.workflow.actions.conditional", {
    "GroupingIdentifier": excl_grp,
    "WFControlFlowMode": 0,
    "WFCondition": 100,
    "WFInput": {"Variable": ref_output(in_excl, "Dictionary Value")},
})
emit("is.workflow.actions.setvariable", {
    "WFVariableName": "Excluded",
    "WFInput": ref_output(in_excl, "Dictionary Value"),
})
emit("is.workflow.actions.conditional", {
    "GroupingIdentifier": excl_grp,
    "WFControlFlowMode": 1,
})
emit("is.workflow.actions.setvariable", {
    "WFVariableName": "Excluded",
    "WFInput": ref_output(default_excluded, "List"),
})
emit("is.workflow.actions.conditional", {
    "GroupingIdentifier": excl_grp,
    "WFControlFlowMode": 2,
})

# Wipe alarms
all_alarms = emit(
    "is.workflow.actions.alarm.find",
    {"WFContentItemFilter": {
        "Value": {"WFActionParameterFilterPrefix": 1},
        "WFSerializationType": "WFContentPredicateTableTemplate",
    }},
    output_name="All Alarms",
)
del_repeat_grp = U()
del_repeat = emit("is.workflow.actions.repeat.each", {
    "GroupingIdentifier": del_repeat_grp,
    "WFControlFlowMode": 0,
    "WFInput": ref_output(all_alarms, "Alarms"),
})
emit("is.workflow.actions.alarm.delete", {
    "WFInput": ref_repeat_item(del_repeat),
})
emit("is.workflow.actions.repeat.each", {
    "GroupingIdentifier": del_repeat_grp,
    "WFControlFlowMode": 2,
})

# Today's events, skip all-day
events = emit(
    "is.workflow.actions.calendar.findevents",
    {"WFContentItemFilter": {
        "Value": {
            "WFActionParameterFilterPrefix": 1,
            "WFContentPredicateBoundedDate": False,
            "WFActionParameterFilterTemplates": [
                {
                    "Property": "Start Date",
                    "Operator": 8,  # "is today" — verify in Shortcuts.app
                    "Removable": True,
                    "Unit": "days",
                    "Values": {"Magnitude": 0, "Unit": "days"},
                },
                {
                    "Property": "Is All Day",
                    "Operator": 4,
                    "Removable": True,
                    "Values": {"Bool": False},
                },
            ],
        },
        "WFSerializationType": "WFContentPredicateTableTemplate",
    }},
    output_name="Today's Events",
)

# For each event: filter excluded calendars (nested loop), then create alarm
event_repeat_grp = U()
event_repeat = emit("is.workflow.actions.repeat.each", {
    "GroupingIdentifier": event_repeat_grp,
    "WFControlFlowMode": 0,
    "WFInput": ref_output(events, "Calendar Events"),
})

zero_uid = emit("is.workflow.actions.number",
                {"WFNumberActionNumber": 0}, output_name="Zero")
emit("is.workflow.actions.setvariable", {
    "WFVariableName": "Skip",
    "WFInput": ref_output(zero_uid, "Number"),
})

excl_loop_grp = U()
excl_loop = emit("is.workflow.actions.repeat.each", {
    "GroupingIdentifier": excl_loop_grp,
    "WFControlFlowMode": 0,
    "WFInput": ref_named("Excluded"),
})

cal_match_grp = U()
emit("is.workflow.actions.conditional", {
    "GroupingIdentifier": cal_match_grp,
    "WFControlFlowMode": 0,
    "WFCondition": 4,  # is (string equals)
    "WFInput": {"Variable": ref_repeat_item(excl_loop)},
    "WFConditionalActionString": with_property(
        ref_repeat_item(event_repeat), "Calendar"
    ),
})
one_uid = emit("is.workflow.actions.number",
               {"WFNumberActionNumber": 1}, output_name="One")
emit("is.workflow.actions.setvariable", {
    "WFVariableName": "Skip",
    "WFInput": ref_output(one_uid, "Number"),
})
emit("is.workflow.actions.conditional", {
    "GroupingIdentifier": cal_match_grp,
    "WFControlFlowMode": 2,
})

emit("is.workflow.actions.repeat.each", {
    "GroupingIdentifier": excl_loop_grp,
    "WFControlFlowMode": 2,
})

# If Skip == 0: subtract buffer minutes, create alarm
skip_grp = U()
emit("is.workflow.actions.conditional", {
    "GroupingIdentifier": skip_grp,
    "WFControlFlowMode": 0,
    "WFCondition": 4,
    "WFInput": {"Variable": ref_named("Skip")},
    "WFNumberValue": 0,
})

adjusted = emit("is.workflow.actions.adjustdate", {
    "WFAdjustOperation": "Subtract",
    "WFDate": ref_repeat_item(event_repeat),
    "WFDuration": {
        "Value": {"Magnitude": ref_named("Buffer"), "Unit": "min"},
        "WFSerializationType": "WFQuantityFieldValue",
    },
}, output_name="Adjusted Date")

emit("is.workflow.actions.alarm.create", {
    "WFAlarmTime": ref_output(adjusted, "Date"),
    "WFAlarmLabel": with_property(
        ref_repeat_item(event_repeat), "Name"
    ),
})

emit("is.workflow.actions.conditional", {
    "GroupingIdentifier": skip_grp,
    "WFControlFlowMode": 2,
})

emit("is.workflow.actions.repeat.each", {
    "GroupingIdentifier": event_repeat_grp,
    "WFControlFlowMode": 2,
})


# --------------------------------------------------------------------------
# Top-level shortcut
# --------------------------------------------------------------------------

shortcut: dict[str, Any] = {
    "WFWorkflowActions": actions,
    "WFWorkflowClientVersion": "2607.0.6",
    "WFWorkflowClientRelease": "2.2.2",
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowIcon": {
        "WFWorkflowIconStartColor": 463140863,
        "WFWorkflowIconGlyphNumber": 59491,
    },
    "WFWorkflowImportQuestions": [],
    "WFWorkflowTypes": [],
    "WFWorkflowInputContentItemClasses": [
        "WFTextContentItem", "WFDictionaryContentItem",
    ],
    "WFWorkflowOutputContentItemClasses": [],
    "WFWorkflowHasShortcutInputVariables": True,
    "WFWorkflowHasOutputFallback": False,
    "WFQuickActionSurfaces": [],
    "WFWorkflowNoInputBehavior": "WFWorkflowNoInputBehaviorIgnore",
}

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_path = os.path.join(repo_root, "OnTime.shortcut")
with open(out_path, "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_XML)

print(f"wrote {out_path}")
print(f"  actions: {len(actions)}")
