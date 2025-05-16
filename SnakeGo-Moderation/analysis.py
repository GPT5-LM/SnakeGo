import json
import re
from collections import Counter

def analyze_finetune_data(filename="dataset.json"):
    """
    Analyzes RWKV finetune data to count flagged status and language distribution.

    Args:
        filename (str): The path to the JSON data file.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found. Please ensure '{filename}' exists.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON file '{filename}'. Please check the file format.")
        return

    total_entries = len(data)
    if total_entries == 0:
        print("No data entries found in the file.")
        return

    flagged_counts = Counter()
    language_counts = Counter()

    # Simple language detection: check for character ranges specific to each language
    # This is a heuristic and might not be accurate for mixed or complex cases
    korean_pattern = re.compile(r'[\uAC00-\uD7A3]') # Hangul
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]') # Hiragana, Katakana, Common Kanji

    print(f"Found {total_entries} data entries.")

    for i, entry in enumerate(data):
        text = entry.get("text")
        if not text:
            print(f"Warning: Entry {i+1} is missing the 'text' field. Skipping.")
            continue

        # Attempt to split User and Assistant parts
        parts = text.split("\n\nAssistant: ", 1)
        if len(parts) < 2:
            print(f"Warning: Entry {i+1} 'text' field format is unexpected. Skipping Assistant JSON parsing: {text[:50]}...")
            user_text = text.replace("User: ", "").strip() # Try to extract User part for language detection
            assistant_json_string = None
        else:
            user_text = parts[0].replace("User: ", "").strip()
            assistant_json_string = parts[1].strip()

        # Parse Assistant JSON and count flagged status
        if assistant_json_string:
            try:
                assistant_data = json.loads(assistant_json_string)
                is_flagged = assistant_data.get("flagged")
                if is_flagged is not None:
                    flagged_counts[is_flagged] += 1
                else:
                    print(f"Warning: Entry {i+1} Assistant JSON is missing the 'flagged' field: {assistant_json_string[:50]}...")
            except json.JSONDecodeError:
                print(f"Error: Entry {i+1} could not parse Assistant JSON string: {assistant_json_string[:50]}...")
                # Entries with unparseable Assistant JSON are not counted in flagged stats

        # Detect and count language based on User text
        if korean_pattern.search(user_text):
            language_counts['Korean'] += 1
        elif japanese_pattern.search(user_text):
            language_counts['Japanese'] += 1
        else:
            # If no Korean or Japanese characters found, assume English
            language_counts['English'] += 1

    # Calculate flagged percentages
    total_flagged_processed = sum(flagged_counts.values())
    if total_flagged_processed > 0:
        flagged_true_count = flagged_counts.get(True, 0)
        flagged_false_count = flagged_counts.get(False, 0)
        flagged_true_percent = (flagged_true_count / total_flagged_processed) * 100
        flagged_false_percent = (flagged_false_count / total_flagged_processed) * 100
    else:
        flagged_true_percent = 0
        flagged_false_percent = 0


    # Calculate language percentages
    total_languages_processed = sum(language_counts.values())
    language_percentages = {}
    if total_languages_processed > 0:
        for lang, count in language_counts.items():
            language_percentages[lang] = (count / total_languages_processed) * 100
    else:
        pass # language_percentages remains empty

    # Print results
    print("\n--- Analysis Results ---")

    print("\nFlagged Status Statistics:")
    print(f"  Flagged (True): {flagged_counts.get(True, 0)} entries ({flagged_true_percent:.2f}%)")
    print(f"  Not Flagged (False): {flagged_counts.get(False, 0)} entries ({flagged_false_percent:.2f}%)")
    if total_entries != total_flagged_processed:
         print(f"  (Note: {total_entries - total_flagged_processed} entries were not included in Flagged statistics due to Assistant JSON parsing/format issues)")


    print("\nLanguage Distribution Statistics:")
    if total_languages_processed > 0:
        for lang, count in language_counts.items():
            print(f"  {lang}: {count} entries ({language_percentages[lang]:.2f}%)")
    else:
         print("  No language data processed.")

    if total_entries != total_languages_processed:
         print(f"  (Note: {total_entries - total_languages_processed} entries were not included in language statistics due to 'text' field format issues)")


# Run the analysis
if __name__ == "__main__":
    analyze_finetune_data()
