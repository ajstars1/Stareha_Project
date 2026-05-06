# Interface: Desktop UI

**Status:** Concept  
**Stage:** 6

---

## What It Is

The desktop UI is a system tray application and companion panel that makes Stareha feel present — not just a CLI command you have to remember to run.

---

## Why It Matters

Stage 6 transforms Stareha from a tool into a companion. When users can see Stareha in their taskbar, it becomes ambient and approachable.

---

## Components

### System Tray Icon

- Shows Stareha status (learning active / paused / has suggestions)
- Badge count for memory inbox items
- Right-click menu for quick actions

### Suggestions Panel

A lightweight floating panel that appears when Stareha has something useful:
- Session summary after session ends
- "I prepared tomorrow's plan" notification
- Memory inbox notification

Closes when dismissed. Does not interrupt.

### Memory Inbox UI

A simple window listing pending memory candidates with approve/reject/edit buttons.

### Daily Briefing Window

Opens automatically on login (if enabled) or on first terminal open.

Shows:
- Yesterday's summary
- Today's learning plan or work brief
- Quick actions (start session, view exercises, open inbox)

---

## Technology

Linux-first: Electron or Tauri (leaning Tauri for smaller footprint).

GTK integration via tray library.

The UI is thin — it talks to the daemon via local HTTP. All logic stays in the daemon.

---

## Screen Layouts

### Tray Menu (right-click)
```
Stareha ●
─────────────────
📥 Inbox: 3 pending
📋 Today's plan ready
─────────────────
Open panel
Pause learning
Settings
─────────────────
Quit
```

### Companion Panel
```
┌─────────────────────────────────┐
│ Stareha                    [─][×]│
├─────────────────────────────────┤
│ Good morning, Ayush.            │
│                                 │
│ Yesterday:                      │
│ • Worked on agent-os (3h 20m)  │
│ • CSS Flexbox (95min)           │
│                                 │
│ Today's plan:                   │
│ [📝 Flexbox Quiz (5 questions)] │
│ [🔨 Pricing card exercise]     │
│ [💻 Open agent-os]             │
│                                 │
│ Memory Inbox: 3 new             │
│ [Review]                        │
└─────────────────────────────────┘
```

---

## Related Files
- [Interfaces Overview](README.md)
- [CLI Interface](cli.md)
- [Roadmap](../../product/roadmap.md) — Stage 6
