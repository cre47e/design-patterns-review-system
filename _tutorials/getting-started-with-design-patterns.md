---
title: "Getting Started with Design Patterns"
description: "A practical introduction to the three categories of GoF patterns — with a simple project that evolves through each one."
date: 2026-05-13
author: "Community"
level: "Beginner"
reading_time: 12
review_status: "approved"
prerequisites: ["Basic OOP knowledge", "Any one of: Python, Java, or TypeScript"]
tags: ["design-patterns", "oop", "beginner"]
---

## What You Will Build

By the end of this tutorial you will have a small **notification system** that evolves through three design patterns. Starting with a naive implementation, you will refactor it step by step to understand *why* each pattern exists, not just how it looks.

---

## Before You Start

Design patterns are solutions to recurring design problems. They are not libraries to install — they are ways of arranging code. You will recognise good candidates for patterns when you feel:

- **Pain from duplication** — I'm copying this logic everywhere.
- **Fear of change** — touching this one class breaks everything else.
- **Confusion about ownership** — where should this behaviour live?

---

## Part 1 — The Naive Notification System

Start with the simplest thing that works:

```python
class NotificationService:
    def send(self, user_email: str, message: str, channel: str) -> None:
        if channel == "email":
            print(f"Email → {user_email}: {message}")
        elif channel == "sms":
            print(f"SMS → {user_email}: {message}")
        elif channel == "push":
            print(f"Push → {user_email}: {message}")
        else:
            raise ValueError(f"Unknown channel: {channel}")
```

This works for a demo. It breaks the moment a product manager asks for Slack notifications, because you have to open `NotificationService` and add another branch.

> **The force this violates:** the Open/Closed Principle — the class is not open for extension without modifying it.

---

## Part 2 — Creational Pattern: Factory Method

**Goal:** decouple the *creation* of a sender from the code that *uses* it.

```python
from abc import ABC, abstractmethod


class Sender(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> None: ...


class EmailSender(Sender):
    def send(self, recipient: str, message: str) -> None:
        print(f"Email → {recipient}: {message}")


class SmsSender(Sender):
    def send(self, recipient: str, message: str) -> None:
        print(f"SMS → {recipient}: {message}")


class SlackSender(Sender):
    def send(self, recipient: str, message: str) -> None:
        print(f"Slack → {recipient}: {message}")


def sender_factory(channel: str) -> Sender:
    senders = {
        "email": EmailSender,
        "sms":   SmsSender,
        "slack": SlackSender,
    }
    cls = senders.get(channel)
    if cls is None:
        raise ValueError(f"Unknown channel: {channel}")
    return cls()


class NotificationService:
    def send(self, recipient: str, message: str, channel: str) -> None:
        sender = sender_factory(channel)
        sender.send(recipient, message)
```

Now adding Slack required writing a new class and one line in the factory dict — `NotificationService` never changed.

**What you just applied:** Factory Method — centralise construction so the client code depends on an interface, not a concrete class.

---

## Part 3 — Structural Pattern: Decorator

**Goal:** add logging and retry behaviour *without* subclassing every sender.

```python
import time


class LoggingSender(Sender):
    def __init__(self, wrapped: Sender) -> None:
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        print(f"[LOG] Sending via {type(self._wrapped).__name__}")
        self._wrapped.send(recipient, message)
        print(f"[LOG] Sent successfully")


class RetrySender(Sender):
    def __init__(self, wrapped: Sender, max_attempts: int = 3) -> None:
        self._wrapped = wrapped
        self._max_attempts = max_attempts

    def send(self, recipient: str, message: str) -> None:
        for attempt in range(1, self._max_attempts + 1):
            try:
                self._wrapped.send(recipient, message)
                return
            except Exception as e:
                print(f"[RETRY] Attempt {attempt} failed: {e}")
                if attempt < self._max_attempts:
                    time.sleep(0.5)
                else:
                    raise
```

Now compose them:

```python
sender = RetrySender(LoggingSender(EmailSender()))
sender.send("user@example.com", "Hello!")
```

Each wrapper adds one responsibility. You can mix and match without a class explosion.

**What you just applied:** Decorator — wrap an object to add behaviour, preserving the interface.

---

## Part 4 — Behavioural Pattern: Observer

**Goal:** let other parts of the system react to a sent notification (analytics, audit log) without `NotificationService` knowing about them.

```python
from typing import Protocol


class NotificationObserver(Protocol):
    def on_sent(self, recipient: str, channel: str) -> None: ...


class AnalyticsTracker:
    def on_sent(self, recipient: str, channel: str) -> None:
        print(f"[ANALYTICS] Tracked {channel} send to {recipient}")


class AuditLogger:
    def on_sent(self, recipient: str, channel: str) -> None:
        print(f"[AUDIT] {channel} message sent to {recipient}")


class NotificationService:
    def __init__(self) -> None:
        self._observers: list[NotificationObserver] = []

    def subscribe(self, observer: NotificationObserver) -> None:
        self._observers.append(observer)

    def send(self, recipient: str, message: str, channel: str) -> None:
        sender = sender_factory(channel)
        sender.send(recipient, message)
        for obs in self._observers:
            obs.on_sent(recipient, channel)


# Wire it up
service = NotificationService()
service.subscribe(AnalyticsTracker())
service.subscribe(AuditLogger())
service.send("user@example.com", "Welcome!", "email")
```

Adding a new reaction — say, a rate limiter — means writing one class and one `subscribe()` call. The service never changes.

**What you just applied:** Observer — notify dependents automatically when state changes, keeping the subject decoupled from its observers.

---

## What You Learned

| Pattern | Category | Force Resolved |
|---|---|---|
| Factory Method | Creational | Decouple construction from use |
| Decorator | Structural | Add responsibilities without subclassing |
| Observer | Behavioural | Notify dependents without tight coupling |

The three categories map neatly to the three phases of an object's life: how it's **created**, how it's **composed**, and how it **communicates**.

---

## Next Steps

- Read [Why Design Patterns Still Matter in 2026]({{ '/blog/why-design-patterns-still-matter/' | relative_url }}) for the bigger picture.
- Browse [Design Patterns]({{ '/patterns/' | relative_url }}) for deeper dives into individual patterns.
- Submit your own pattern or article by following the [Contributing Guide](https://github.com/{{ site.github_username | default: 'your-username' }}/{{ site.github_repo | default: 'DesignPatternsReviewSystem' }}/blob/main/CONTRIBUTING.md).
