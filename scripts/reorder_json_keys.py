import json
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reorder_json_keys.py <source_file> <destination_file>")
        sys.exit(1)

    source_file = sys.argv[1]
    destination_file = sys.argv[2]

    with open(source_file, "r", encoding="utf-8") as f:
        source_data = json.load(f)

    with open(destination_file, "r", encoding="utf-8") as f:
        destination_data = json.load(f)

    def reorder_keys(source, destination):
        ordered_destination = {}
        for key in source:
            if key in destination:
                if isinstance(source[key], dict) and isinstance(destination[key], dict):
                    ordered_destination[key] = reorder_keys(
                        source[key], destination[key]
                    )
                else:
                    ordered_destination[key] = destination[key]
        for key in destination:
            if key not in ordered_destination:
                ordered_destination[key] = destination[key]
        return ordered_destination

    destination_data = reorder_keys(source_data, destination_data)

    with open(destination_file, "w", encoding="utf-8") as f:
        json.dump(destination_data, f, ensure_ascii=False, indent=2)
