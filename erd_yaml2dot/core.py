import yaml
import sys
import re
from graphviz import Digraph
from erd_yaml2dot.validate import validate_schema


def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)
  error = True


def load_yaml_file(file_path):
  with open(file_path, 'r') as file:
    data = yaml.safe_load(file)
  return data


def parse_card(card_str):
  card_regex = r"(0|1),(1|\*)"
  card_reg = re.compile(card_regex, re.MULTILINE | re.IGNORECASE)
  m = card_reg.match(card_str)

  return {
    'min': m.group(1),
    'max': m.group(2)
  }


def convert_yaml_to_dot(yaml_to_convert):
  # TODO: construct Digraph with graphviz directly instead of emitting dot source code
  pass


def validate_and_convert_yaml_to_dot(path_to_yaml_file, html=True, style="default.yaml"):
  yaml_data = load_yaml_file(path_to_yaml_file)
  valid, validation_errors = validate_schema(yaml_data)
  if not valid:
    eprint("\n".join(validation_errors))
    return None
  else:
    # TODO: handle style
    return convert_yaml_to_dot(path_to_yaml_file)
