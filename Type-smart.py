#!/usr/bin/env python3
# ============================================================
#   ULTRA-LIGHT TYPING TRAINER — FULL FEATURE EDITION (v10)
# ============================================================
# Features:
# - Real-time WPM
# - Real-time accuracy %
# - Colored target text
# - Backspace handling
# - Randomized practice mode
# - Custom lessons
# - Keyboard heatmap accuracy tracking
# - Fancy UI themes
# - Progress bars
# - Sound effects
# - Typing-test mode (1 or 5 minutes)
# ============================================================

import json, os, time, sys, tty, termios, random, shutil
from datetime import datetime

PROGRESS_FILE = os.path.expanduser("~/.typing_progress_v10.json")

# ============================================================
# THEMES
# ============================================================

THEMES = {
    "light": {
        "text": "\033[37m",
        "accent": "\033[36m",
        "good": "\033[92m",
        "bad": "\033[91m",
        "hud": "\033[90m",
        "reset": "\033[0m",
    },
    "dark": {
        "text": "\033[97m",
        "accent": "\033[94m",
        "good": "\033[92m",
        "bad": "\033[91m",
        "hud": "\033[90m",
        "reset": "\033[0m",
    },
    "neon": {
        "text": "\033[96m",
        "accent": "\033[95m",
        "good": "\033[92m",
        "bad": "\033[91m",
        "hud": "\033[95m",
        "reset": "\033[0m",
    }
}

# Default theme
THEME = THEMES["neon"]

# ============================================================
# SAMPLE LEVEL DATA (you can expand these)
# ============================================================

BEGINNER_LEVEL = [
    "asdf jkl qwe rty",
    "zxcv bn m po iu",
    "qaz wsx edc rfv",
] + [f"wordset {i}" for i in range(10)]

INTERMEDIATE_LEVEL = [
    "The quick brown fox jumps over the lazy dog.",
    "Typing improves focus and muscle memory.",
] + [f"Intermediate sentence {i}" for i in range(10)]

EXPERT_LEVEL = [
    "Expert typing requires endurance, precision, and mental stamina.",
    "Long-form typing helps develop high sustained WPM.",
] + [f"Expert paragraph {i}" for i in range(10)]

LEVELS = {1: BEGINNER_LEVEL, 2: INTERMEDIATE_LEVEL, 3: EXPERT_LEVEL}

# ============================================================
# LOAD PROGRESS
# ============================================================

if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        progress = json.load(f)
else:
    progress = {
        "theme": "neon",
        "level": 1,
        "current_set": 0,
        "total_words": 0,
        "total_errors": 0,
        "total_time": 0.0,
        "heatmap": {},  # accuracy by key
        "streak": 0,
        "last_practice": "",
        "custom_lessons": []
    }

THEME = THEMES.get(progress["theme"], THEMES["neon"])

def save_progress():
    tmp = PROGRESS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(progress, f)
    os.replace(tmp, PROGRESS_FILE)

# ============================================================
# HELPERS
# ============================================================

def normalize(s):
    return " ".join(s.strip().split())

def beep_correct():
    sys.stdout.write("\a")
    sys.stdout.flush()

def beep_wrong():
    sys.stdout.write("\a\033[91m\033[1m")
    sys.stdout.flush()

def progress_bar(current, total, width=30):
    filled = int((current / total) * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"

# ============================================================
# KEYBOARD HEATMAP UPDATE
# ============================================================

def update_heatmap(key, correct):
    hm = progress["heatmap"]
    if key not in hm:
        hm[key] = {"correct": 0, "wrong": 0}
    if correct:
        hm[key]["correct"] += 1
    else:
        hm[key]["wrong"] += 1
    save_progress()

# ============================================================
# REAL-TIME TYPING ENGINE
# ============================================================

def live_typing_prompt(target):
    global THEME
    print(f"\n{THEME['accent']}Type this:{THEME['reset']}")
    print(f"{THEME['accent']}> {target}{THEME['reset']}\n")

    typed = ""
    start = time.time()
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)

            # ENTER ends typing
            if ch in ("\r", "\n"):
                print("")
                break

            # BACKSPACE
            elif ch in ("\x7f", "\x08"):
                if typed:
                    typed = typed[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue

            typed += ch

            # WPM & accuracy
            elapsed = max(0.001, time.time() - start)
            wpm = (len(typed.split()) / elapsed) * 60
            correct_chars = sum(
                typed[i] == target[i] if i < len(target) else False
                for i in range(len(typed))
            )
            acc = (correct_chars / len(typed)) * 100 if typed else 100

            # color feedback
            correct_char = len(typed) <= len(target) and ch == target[len(typed)-1]
            update_heatmap(ch, correct_char)

            if correct_char:
                sys.stdout.write(f"{THEME['good']}{ch}{THEME['reset']}")
                beep_correct()
            else:
                sys.stdout.write(f"{THEME['bad']}{ch}{THEME['reset']}")
                beep_wrong()

            sys.stdout.flush()

            sys.stdout.write(
                f"\r{THEME['hud']}WPM: {wpm:.1f} | Accuracy: {acc:.1f}%{THEME['reset']}"
            )
            sys.stdout.flush()

        print("\n")

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    elapsed = time.time() - start
    return typed, elapsed

# ============================================================
# TYPING TEST MODE
# ============================================================

def typing_test(minutes):
    print(f"\n{THEME['accent']}--- {minutes}-Minute Typing Test ---{THEME['reset']}\n")
    deadline = time.time() + minutes * 60
    total_typed = ""

    while time.time() < deadline:
        sample = random.choice(LEVELS[3])
        typed, _ = live_typing_prompt(sample)
        total_typed += " " + typed

    words = len(total_typed.split())
    wpm = words / minutes

    print(f"\n{THEME['accent']}Test Complete!{THEME['reset']}")
    print(f"WPM: {wpm:.1f}\n")

# ============================================================
# PRACTICE LEVEL
# ============================================================

def practice_level(level_number, daily=False, random_mode=False):
    level_sets = LEVELS[level_number]

    # random mode
    if random_mode:
        sets = random.sample(level_sets, len(level_sets))
        set_idx = 0
    else:
        sets = level_sets
        set_idx = progress["current_set"]

    while set_idx < len(sets):
        item = sets[set_idx]
        typed, elapsed = live_typing_prompt(item)

        if normalize(typed) == normalize(item):
            print(f"{THEME['good']}Correct!{THEME['reset']}\n")

            progress["total_words"] += len(item.split())
            progress["total_time"] += elapsed

            if not random_mode:
                progress["current_set"] += 1

            set_idx += 1
            save_progress()
        else:
            print(f"{THEME['bad']}Incorrect. Try again.{THEME['reset']}\n")
            progress["total_errors"] += 1
            save_progress()
            continue

        bar = progress_bar(set_idx, len(sets))
        print(f"Progress: {bar} {set_idx}/{len(sets)}\n")

    print(f"\n{THEME['good']}🎉 Level {level_number} completed!{THEME['reset']}\n")

    if level_number < 3:
        progress["level"] += 1
        progress["current_set"] = 0
    save_progress()

# ============================================================
# CUSTOM LESSONS
# ============================================================

def add_custom_lesson():
    text = input("Enter text for your custom lesson:\n> ").strip()
    progress["custom_lessons"].append(text)
    save_progress()
    print("Custom lesson added!\n")

def practice_custom_lessons():
    if not progress["custom_lessons"]:
        print("No custom lessons yet!\n")
        return
    for lesson in progress["custom_lessons"]:
        live_typing_prompt(lesson)

# ============================================================
# DAILY PRACTICE
# ============================================================

def daily_practice():
    today = datetime.today().strftime("%Y-%m-%d")
    if progress["last_practice"] != today:
        progress["streak"] += 1
        progress["last_practice"] = today
        save_progress()

    print(f"\n{THEME['accent']}--- Daily Practice (Day {progress['streak']}) ---{THEME['reset']}\n")
    practice_level(progress["level"], daily=True)
    print(f"{THEME['good']}Daily practice done! Streak: {progress['streak']} days{THEME['reset']}\n")

# ============================================================
# STATS
# ============================================================

def show_stats():
    total_time = progress["total_time"] or 1
    avg_wpm = (progress["total_words"] / (total_time / 60)) if progress["total_words"] else 0

    print("\n--- Stats ---")
    print(f"Theme: {progress['theme']}")
    print(f"Level: {progress['level']}")
    print(f"Set: {progress['current_set'] + 1}")
    print(f"Total Words: {progress['total_words']}")
    print(f"Errors: {progress['total_errors']}")
    print(f"Avg WPM: {avg_wpm:.1f}")
    print(f"Streak: {progress['streak']} days")
    print(f"Last Practice: {progress['last_practice']}\n")

    print("--- Heatmap (Accuracy by Key) ---")
    for key, data in progress["heatmap"].items():
        total = data["correct"] + data["wrong"]
        acc = (data["correct"] / total) * 100 if total else 100
        print(f"{repr(key)}: {acc:.1f}% accuracy")

# ============================================================
# THEME SWITCHER
# ============================================================

def change_theme():
    print("Themes:")
    for name in THEMES:
        print(" -", name)
    choice = input("Choose theme: ").strip().lower()
    if choice in THEMES:
        progress["theme"] = choice
        global THEME
        THEME = THEMES[choice]
        save_progress()
        print("Theme changed!\n")
    else:
        print("Invalid theme.\n")

# ============================================================
# MAIN MENU
# ============================================================

def main():
    while True:
        print(f"\n{THEME['accent']}=== Typing Trainer v10 ==={THEME['reset']}")
        print("1. Practice level")
        print("2. Daily practice")
        print("3. Practice (randomized)")
        print("4. Add custom lesson")
        print("5. Practice custom lessons")
        print("6. Typing test (1 min)")
        print("7. Typing test (5 min)")
        print("8. Show stats")
        print("9. Change theme")
        print("0. Exit")

        choice = input("> ").strip()

        if choice == "1":
            practice_level(progress["level"])
        elif choice == "2":
            daily_practice()
        elif choice == "3":
            practice_level(progress["level"], random_mode=True)
        elif choice == "4":
            add_custom_lesson()
        elif choice == "5":
            practice_custom_lessons()
        elif choice == "6":
            typing_test(1)
        elif choice == "7":
            typing_test(5)
        elif choice == "8":
            show_stats()
        elif choice == "9":
            change_theme()
        elif choice == "0":
            break
        else:
            print("Invalid choice!\n")

if __name__ == "__main__":
    main()
