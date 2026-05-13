---
title: "Singleton Pattern"
description: "Ensure a class has only one instance and provide a global point of access to it — with thread-safe implementations in Python, Java, and TypeScript."
date: 2026-05-13
author: "Community"
pattern_type: "Creational"
difficulty: "Beginner"
languages: ["Python", "Java", "TypeScript"]
also_known_as: "Single Instance"
review_status: "approved"
tags: ["creational", "oop", "concurrency"]
---

## Intent

Ensure a class has **only one instance** and provide a **global point of access** to it. Useful when exactly one object is needed to coordinate actions across a system.

## Problem

You need to control access to a shared resource — a configuration registry, a connection pool, or a logger — and guarantee that only one instance ever exists, regardless of how many times client code requests it.

## Solution

Make the constructor private and expose a static method that returns the single stored instance, creating it on first call.

---

## Structure

```
Client ──► Singleton
              ├── -instance: Singleton   (static)
              ├── -Singleton()           (private constructor)
              └── +getInstance(): Singleton (static)
```

---

## Implementation

### Python — thread-safe with a lock

```python
from threading import Lock


class Singleton:
    _instance = None
    _lock: Lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def some_business_logic(self):
        ...


# Usage
s1 = Singleton()
s2 = Singleton()
assert s1 is s2  # True
```

### Java — double-checked locking

```java
public class Singleton {
    private static volatile Singleton instance;

    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

### TypeScript

```typescript
class Singleton {
  private static instance: Singleton;

  private constructor() {}

  static getInstance(): Singleton {
    if (!Singleton.instance) {
      Singleton.instance = new Singleton();
    }
    return Singleton.instance;
  }

  doSomething(): void {
    console.log("Singleton working");
  }
}

const s1 = Singleton.getInstance();
const s2 = Singleton.getInstance();
console.log(s1 === s2); // true
```

---

## When to Use

- A single shared instance must control access to a shared resource (DB pool, file system, config).
- You need stricter control over global variables.

## When to Avoid

| Situation | Better Alternative |
|---|---|
| Unit-testing in isolation | Dependency injection |
| Multiple independent configs | Regular classes with DI |
| Multi-process environments | External state store (Redis, etc.) |

---

## Real-World Examples

- **Logger** — one log writer for the entire application.
- **Configuration** — one parsed config object loaded at startup.
- **Thread pool** — shared executor across all workers.

---

## Pros & Cons

**Pros**
- Guaranteed single instance.
- Global access point.
- Instance created only when first needed (lazy init).

**Cons**
- Violates Single Responsibility Principle (controls both lifecycle and behavior).
- Difficult to unit-test without dependency injection.
- Requires special treatment in multithreaded environments.

---

## Related Patterns

- **Abstract Factory**, **Builder**, **Prototype** — can all be implemented as Singletons.
- **Facade** — often uses a Singleton facade object.
- **State** — objects representing states are often Singletons.
