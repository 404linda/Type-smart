
#!/usr/bin/env python3
import json, os, time, sys, tty, termios
from datetime import datetime

PROGRESS_FILE = os.path.expanduser("~/.typing_progress_v8_fullcurriculum.json")

# --------------------------
# LEVELS & SETS
# --------------------------

# Level 1 – Beginner (40 sets × 12 words/strings each)
BEGINNER_LEVEL = [
    "asdf jkl qwe rty", "zxcv bn m po iu", "qaz wsx edc rfv", "tgb yhn ujm ik,", "ol. p;/ as df",
    "gh jk lq we rt yu", "zx cv bn mk lo pi", "uy tr ew as df gh", "jk lq we rt yu io", "pa sd fg hj kl",
] + [f"wordset {i}" for i in range(30)]  # filler to reach 40 sets

# Level 2 – Intermediate (30 sets × 3–5 sentences each)
INTERMEDIATE_LEVEL = [
    "The cat sat on the mat.", "I like to read books.", "Typing helps improve focus.",
    "Python is fun to learn.", "Practice daily to increase speed.", "Accuracy is more important than speed.",
] + [f"This is intermediate sentence {i}." for i in range(24)]  # filler to reach 30 sets

# Level 3 – Expert (70 sets × 3–5 paragraphs each)
EXPERT_LEVEL = [
    "Typing fast requires accuracy and consistency.",
    "Practice daily to improve speed and minimize errors.",
    "Accuracy beats speed in the beginning stages.",
    "This paragraph contains multiple sentences to improve fluid typing.",
    "The goal is to type long passages with minimal mistakes.",
] + [f"Expert paragraph {i}: This passage is designed to challenge your typing speed and accuracy." for i in range(65)]  # filler to reach 70 sets

LEVELS = {1: BEGINNER_LEVEL, 2: INTERMEDIATE_LEVEL, 3: EXPERT_LEVEL}

# --------------------------
# LOAD OR INITIALIZE PROGRESS
# --------------------------
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        progress = json.load(f)
else:
    progress = {
        "level": 1,
        "current_set": 0,
        "total_words": 0,
        "total_errors": 0,
        "total_time": 0.0,
        "streak": 0,
        "last_practice": ""
    }

def save_progress():
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

# --------------------------
# LIVE TYPING FUNCTION
# --------------------------
def live_typing_prompt(target):
    print("\nType this:\n> ", flush=True)
    typed = ""
    start = time.time()
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch in ("\r", "\n"):
                print("")
                break
            elif ord(ch) == 127:  # Backspace
                if typed:
                    typed = typed[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            else:
                typed += ch
                if len(typed) <= len(target) and ch == target[len(typed)-1]:
                    sys.stdout.write(f"\033[92m{ch}\033[0m")
                else:
                    sys.stdout.write(f"\033[91m{ch}\033[0m")
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    elapsed = time.time() - start
    return typed, elapsed

# --------------------------
# PRACTICE FUNCTION
# --------------------------
def practice_level(level_number, daily=False):
    level_sets = LEVELS[level_number]
    set_idx = progress["current_set"]

    while set_idx < len(level_sets):
        item = level_sets[set_idx]
        typed, elapsed = live_typing_prompt(item)

        if typed.strip() == item.strip():
            print("✅ Correct!")
            progress["total_words"] += len(item.split())
            progress["total_time"] += elapsed
            set_idx += 1
            progress["current_set"] = set_idx
            save_progress()
        else:
            print("❌ Incorrect. Try again.")
            progress["total_errors"] += 1
            save_progress()
            continue  # retry same set

        if not daily and set_idx < len(level_sets):
            print(f"\n--- Moving to set {set_idx + 1} ---")

    print(f"\n🎉 You completed Level {level_number}!")
    if level_number < max(LEVELS.keys()):
        progress["level"] = level_number + 1
        progress["current_set"] = 0
        save_progress()

# --------------------------
# DAILY PRACTICE FUNCTION
# --------------------------
def daily_practice():
    today = datetime.today().strftime("%Y-%m-%d")
    if progress["last_practice"] != today:
        progress["streak"] += 1
        progress["last_practice"] = today
        save_progress()
    print(f"\n--- Daily Practice (Day {progress['streak']}) ---")
    practice_level(progress["level"], daily=True)
    print(f"\n✅ Daily practice completed! Streak: {progress['streak']} days")

# --------------------------
# STATS FUNCTION
# --------------------------
def show_stats():
    total_time = progress['total_time'] if progress['total_time'] > 0 else 1
    avg_wpm = progress['total_words'] / (total_time / 60)
    print("\n--- Typing Progress ---")
    print(f"Level: {progress['level']}")
    print(f"Set: {progress['current_set'] + 1}")
    print(f"Total words typed: {progress['total_words']}")
    print(f"Total errors: {progress['total_errors']}")
    print(f"Total time spent: {progress['total_time']:.2f} seconds")
    print(f"Average WPM: {avg_wpm:.2f}")
    print(f"Current streak: {progress['streak']} days")
    print(f"Last practice: {progress['last_practice']}")

# --------------------------
# MAIN MENU
# --------------------------
def main():
    while True:
        print("\n--- Ultra-Light Typing Trainer v8 Full Curriculum ---")
        print("1. Practice current level")
        print("2. Daily practice")
        print("3. Show progress & streak")
        print("4. Exit")
        choice = input("> ")

        if choice == "1":
            practice_level(progress["level"])
        elif choice == "2":
            daily_practice()
        elif choice == "3":
            show_stats()
        elif choice == "4":
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
