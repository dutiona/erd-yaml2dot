import yaml
from erd_yaml2dot.validate import validate_schema
import importlib.resources


def load_test_file():
  with importlib.resources.open_text('tests.resources', 'test_diagram.yaml') as file:
    return yaml.safe_load(file)


def test_validate_schema():

  yaml_data = load_test_file()
  valid, errors = validate_schema(yaml_data)
  if not valid:
    print("\n")
    print(errors)

  assert valid
  assert len(errors) == 0
