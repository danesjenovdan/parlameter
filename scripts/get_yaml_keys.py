import yaml


YAML_TEST_INPUT = """
one: 1
two: 2
three: 3
items:
  - name: item1
    value: 10
  - name: item2
    value: 20
  - name: item3
    value: 30
nested:
  level1:
    level2:
      key1: value1
      key2: value2
nested2:
  level1empty:
  level1null: null
list:
  - name: item4
    value: 40
    nested:
      key3: value3
      key4: value4
  - name: item5
    value: 40
    nested:
      key3: value5
      key4: value6
empty:
"""

YAML_TEST_KEYS = [
    "one",
    "two",
    "three",
    "items.0.name",
    "items.0.value",
    "items.1.name",
    "items.1.value",
    "items.2.name",
    "items.2.value",
    "nested.level1.level2.key1",
    "nested.level1.level2.key2",
    "nested2.level1empty",
    "nested2.level1null",
    "list.0.name",
    "list.0.value",
    "list.0.nested.key3",
    "list.0.nested.key4",
    "list.1.name",
    "list.1.value",
    "list.1.nested.key3",
    "list.1.nested.key4",
    "empty",
]


def get_yaml_keys_impl(input):
    data = yaml.safe_load(input)

    keys = []

    def get_nested_keys(data, parent_key=""):
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}.{key}" if parent_key else key
                get_nested_keys(value, new_key)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_key = f"{parent_key}.{index}" if parent_key else str(index)
                get_nested_keys(item, new_key)
        else:
            keys.append(parent_key)

    get_nested_keys(data)

    return keys


def get_yaml_keys(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        return get_yaml_keys_impl(file.read())


if __name__ == "__main__":
    print("Testing YAML key extraction...")
    keys = get_yaml_keys_impl(YAML_TEST_INPUT)
    assert keys == YAML_TEST_KEYS, "Keys do not match expected keys."
    print("All keys match expected keys.")
