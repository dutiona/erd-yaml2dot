import yaml
import jsonschema
from jsonschema import validate
import importlib.resources


def load_schema():
  with importlib.resources.open_text('erd_yaml2dot.resources', 'erd_schema.yaml') as file:
    return yaml.safe_load(file)


def load_test_file():
  with importlib.resources.open_text('tests.resources', 'test_diagram.yaml') as file:
    return yaml.safe_load(file)


def validate_schema():

  yaml_data = load_test_file()
  schema_data = load_schema()

  try:
    validate(instance=yaml_data, schema=schema_data)
    return True
  except jsonschema.exceptions.ValidationError as e:
    print(e)
    return False


def test_schema():
  ret = validate_schema()
  print(ret)
  assert ret
