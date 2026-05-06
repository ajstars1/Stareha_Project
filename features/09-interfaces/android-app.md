# Interface: Android App

**Status:** Concept  
**Stage:** 9

---

## What It Is

The Stareha Android app brings the companion to mobile — enabling cross-device continuity, voice notes, learning reminders, and mobile memory access.

---

## Why It Matters (Stage 9)

By Stage 9, the user has built up significant workflow memory on their desktop. The Android app lets that memory follow them:
- Review learning briefings on the go
- Add voice notes that get imported
- Get reminded about learning goals
- Search memories from their phone

---

## Features

| Feature | What it does |
|---------|-------------|
| Share to Stareha | Share links, text, screenshots to add context |
| Voice notes | Record quick notes that are transcribed and added to memory |
| Learning reminders | Notifications for practice/review sessions |
| Mobile memory search | Search approved memories |
| Manual screenshot memory | User screenshots → added to context with annotation |
| Daily briefing | Morning briefing delivered as notification |

---

## NOT Included (Privacy)

The Android app will NOT:
- Read notification content
- Track app usage on phone
- Access contacts, messages, or calls
- Run any background surveillance

It is a companion input surface, not a surveillance tool.

---

## Sync Architecture

All sync happens through encrypted cloud memory (Stage 8 prerequisite):
- Only summaries and approved memories sync
- Raw events stay on the originating device
- End-to-end encrypted
- User can export/delete sync data at any time

---

## Related Files
- [Interfaces Overview](README.md)
- [Roadmap](../../product/roadmap.md) — Stage 9 (Android) and Stage 8 (Cloud Memory)
