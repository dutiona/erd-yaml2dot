from erd_yaml2dot.validate import validate_erd_schema
from erd_yaml2dot.core import load_yaml_file
from erd_yaml2dot.style import Style, ValidationError
import importlib.resources


def load_erd_test_file():
  return load_yaml_file(importlib.resources.open_text('tests.resources', 'test_diagram.yaml'))


def load_and_validate_style_test_file():
  return Style(importlib.resources.open_text('erd_yaml2dot.resources.styles', 'default.yaml'), validate=True)


def test_validate_erd_schema():
  yaml_data = load_erd_test_file()
  valid, errors = validate_erd_schema(yaml_data)
  if not valid:
    print("\n")
    print(errors)

  assert valid
  assert len(errors) == 0


def test_validate_style_schema():
  try:
    style = load_and_validate_style_test_file()
  except ValidationError as err:
    print(err)
    raise err
