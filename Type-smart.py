#!/usr/bin/env python3
import time
import random
import os
import json

# Path to store progress
PROGRESS_FILE = os.path.expanduser("~/.typing_progress.json")

# Sample practice text
SENTENCES = [
    "The quick brown fox jumps over the lazy dog",
    "Practice makes perfect",
    "Python programming is fun",
    "Consistency is the key to improvement",
    "Typing fast requires accuracy"
]

# Load previous progress
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        progress = json.load(f)
else:
    progress = {"total_words": 0, "total_time": 0, "sessions": 0}

def save_progress():
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

def typing_session():
    sentence = random.choice(SENTENCES)
    print("\nType this sentence:")
    print(f"> {sentence}\n")

    start = time.time()
    typed = input("> ")
    end = time.time()

    elapsed = end - start
    words_typed = len(typed.split())
    accuracy = sum(1 for a, b in zip(typed, sentence) if a == b) / max(len(sentence),1) * 100

    print(f"\nTime: {elapsed:.2f}s")
    print(f"Words typed: {words_typed}")
    print(f"Accuracy: {accuracy:.2f}%")
    if elapsed > 0:
        print(f"WPM: {words_typed / (elapsed / 60):.2f}")

    # Update progress
    progress["total_words"] += words_typed
    progress["total_time"] += elapsed
    progress["sessions"] += 1
    save_progress()

def show_stats():
    print("\n--- Typing Progress ---")
    sessions = progress.get("sessions",1)
    total_words = progress.get("total_words",0)
    total_time = progress.get("total_time",1)
    print(f"Sessions: {sessions}")
    print(f"Total words typed: {total_words}")
    print(f"Total time spent: {total_time:.2f} seconds")
    print(f"Average WPM: {total_words / (total_time / 60):.2f}")

def main():
    while True:
        print("\n--- Ultra Light Typing Practice ---")
        print("1. Practice typing")
        print("2. Show progress")
        print("3. Exit")
        choice = input("> ")

        if choice == "1":
            typing_session()
        elif choice == "2":
            show_stats()
        elif choice == "3":
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
