import json
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python copy_i18n_keys_from.py <source_file> <destination_file>")
        sys.exit(1)

    source_file = sys.argv[1]
    destination_file = sys.argv[2]

    with open(source_file, "r", encoding="utf-8") as f:
        source_data = json.load(f)

    with open(destination_file, "r", encoding="utf-8") as f:
        destination_data = json.load(f)

    def copy_missing_keys(source, destination):
        for key, value in source.items():
            if key not in destination:
                destination[key] = value
            elif isinstance(value, dict) and isinstance(destination.get(key), dict):
                copy_missing_keys(value, destination[key])

    copy_missing_keys(source_data, destination_data)

    with open(destination_file, "w", encoding="utf-8") as f:
        json.dump(destination_data, f, ensure_ascii=False, indent=2)
