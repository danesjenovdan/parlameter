import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = set()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(f"Duplicate key {key!r} found in YAML.")
            mapping.add(key)
        return super().construct_mapping(node, deep)


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

YAML_TEST_DUPLICATES1_INPUT = """
one: 1
one: 1
two: 2
"""

YAML_TEST_DUPLICATES1_ERROR = "Duplicate key 'one' found in YAML."

YAML_TEST_DUPLICATES2_INPUT = """
one: 1
two: 2
three: 3
two: 2
"""

YAML_TEST_DUPLICATES2_ERROR = "Duplicate key 'two' found in YAML."

YAML_TEST_DUPLICATES3_INPUT = """
nested:
  level1:
    level2:
      key1: value1
      key2: value2
nested:
  level1:
    level2:
      key1: value1
      key2: value2
"""

YAML_TEST_DUPLICATES3_ERROR = "Duplicate key 'nested' found in YAML."


def get_yaml_keys_impl(input):
    data = yaml.load(input, Loader=UniqueKeyLoader)

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


def _test_yaml_duplicates(input_data, expected_error):
    try:
        get_yaml_keys_impl(input_data)
        assert False, f"Expected error: {expected_error}"
    except ValueError as e:
        assert str(e) == expected_error, f"Unexpected error message: {e}"


if __name__ == "__main__":
    print("Testing YAML key extraction...")
    keys = get_yaml_keys_impl(YAML_TEST_INPUT)
    assert keys == YAML_TEST_KEYS, "Keys do not match expected keys!"
    print("All keys match expected keys.")

    print("Testing YAML key extraction with duplicates...")
    _test_yaml_duplicates(YAML_TEST_DUPLICATES1_INPUT, YAML_TEST_DUPLICATES1_ERROR)
    _test_yaml_duplicates(YAML_TEST_DUPLICATES2_INPUT, YAML_TEST_DUPLICATES2_ERROR)
    _test_yaml_duplicates(YAML_TEST_DUPLICATES3_INPUT, YAML_TEST_DUPLICATES3_ERROR)
    print("All duplicate key tests passed.")
