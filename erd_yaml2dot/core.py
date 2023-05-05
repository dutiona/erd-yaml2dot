import yaml
import sys
import re
from graphviz import Digraph
from erd_yaml2dot.validate import validate_erd_schema
from pprint import pprint


def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)
  error = True


def load_yaml_file(file_path):
  with open(file_path, 'r') as file:
    data = yaml.safe_load(file)
  return data


def merge_dict(input, override):
  ret = input.copy()
  for k, v in override.items():
    ret[k] = v
  return ret


def expand_style_yaml_data(yaml_data):

  yaml_proper = {}
  yaml_proper['name'] = yaml_data['name']
  yaml_proper['style'] = {}

  styles_to_expand = {}
  for style_name, style_content in yaml_data.items():
    if style_name.startswith("."):
      styles_to_expand[style_name] = style_content

  # unpack style for entity and relationships
  for rule_name, rule_content in yaml_data['style'].items():
    if rule_name in ['entity', 'relationship'] and 'extends' in rule_content:
      style_to_override = rule_content.pop('extends')
      rule_content = merge_dict(styles_to_expand[style_to_override], rule_content)
      yaml_proper['style'][rule_name] = rule_content

    # for nested title, fields, note
    for nested_rule_name, nested_rule_content in rule_content.items():
      if nested_rule_name in ['title', 'field', 'note'] and 'extends' in nested_rule_content:
        style_to_override = nested_rule_content.pop('extends')
        nested_rule_content = merge_dict(styles_to_expand[style_to_override], nested_rule_content)
        rule_content[nested_rule_name] = nested_rule_content
    yaml_proper['style'][rule_name] = rule_content

  print("\nYAML PROPER\n")
  pprint(yaml_proper)
  print("\nEND YAML PROPER\n")

  return yaml_proper


def load_style(file_path):
  return expand_style_yaml_data(load_yaml_file(file_path))


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
  valid, validation_errors = validate_erd_schema(yaml_data)
  if not valid:
    eprint("\n".join(validation_errors))
    return None
  else:
    # TODO: handle style
    return convert_yaml_to_dot(path_to_yaml_file)
