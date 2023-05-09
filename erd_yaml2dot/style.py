import re
from erd_yaml2dot.utility import load_yaml_file, eprint  # , save_yaml_file
from erd_yaml2dot.validate import validate_style_schema
from pprint import pprint


regex = r"(\.[a-zA-Z0-9_-]+)((?:/(?:[a-zA-Z0-9_-]+))+)?"
style_path_reg = re.compile(regex, re.MULTILINE | re.IGNORECASE)


class ValidationError(Exception):
  def __init__(self, validation_errors: list[str]):
    super().__init__("Validation failed.")
    self.validation_errors = validation_errors

  def __str__(self):
    error_messages = "\n".join([str(err) for err in self.validation_errors])
    return f"Validation errors:\n{error_messages}"


def merge_dict_recur(input, override):
  ret = input.copy()
  for k, v in override.items():
    if k in input and isinstance(input[k], dict) and isinstance(v, dict):
      v = merge_dict_recur(input[k], v)
    ret[k] = v
  return ret


def unstack_accessor_recur(accessor_current, base_path, remaining_path):
  if len(remaining_path) == 0:
    return accessor_current
  else:
    path_token = remaining_path[0]
    remaining_path = remaining_path[1:]

    def acc(dict_):
      curr = accessor_current(dict_)
      # print("In dict<{}>\n Taking key <{}>\n".format(curr, path_token))
      try:
        return curr[path_token]
      except KeyError as kerr:
        eprint("Error: Invalid style-path to expand! In <{}>, key <{}> does not exist!\n{}"
               .format(base_path, path_token, kerr))
        raise kerr
    # print("Remaining Path <{}>\n".format(remaining_path))
    return unstack_accessor_recur(acc, base_path, remaining_path)


def parse_expand_pattern(expand_pattern, parent):
  if style_path_reg == "parent":
    return lambda x: parent
  m = style_path_reg.match(expand_pattern)
  path = [m.group(1)]
  path_in_style = m.group(2)
  if path_in_style is not None:
    path += path_in_style.split("/")[1:]
  return unstack_accessor_recur(lambda x: x, path, path)


class Style:
  def __init__(self, file_stream, validate=True):
    style_yaml_data = self._load(file_stream)
    self._validate(style_yaml_data)

    self._parse(style_yaml_data)

  def _load(self, fp):
    yaml_data = load_yaml_file(fp)
    # pprint(yaml_data)
    expanded_yaml_data = self._expand_style_yaml_data(yaml_data)
    # pprint(expanded_yaml_data)
    return expanded_yaml_data

  def _expand_style_yaml_data(self, yaml_data):

    styles_to_expand = {}
    for style_name, style_content in yaml_data.items():
      if style_name.startswith("."):
        styles_to_expand[style_name] = style_content
    for style_name, style_content in styles_to_expand.items():
      if 'extends' in style_content:
        base_dict_to_override = parse_expand_pattern(style_content.pop('extends'), parent={})(styles_to_expand)
        styles_to_expand[style_name] = style_content
        if not base_dict_to_override is None:
          styles_to_expand[style_name] = merge_dict_recur(input=base_dict_to_override, override=style_content)
        else:
          styles_to_expand[style_name] = base_dict_to_override

    # unpack style for entity and relationships
    cur_style = yaml_data['style-sheet']
    for rule_name, rule_content in cur_style.items():
      if rule_name in ['entity', 'relationship'] and 'extends' in rule_content:
        base_dict_to_override = parse_expand_pattern(rule_content.pop('extends'), parent={})(styles_to_expand)
        if not base_dict_to_override is None:
          rule_content = merge_dict_recur(input=base_dict_to_override, override=rule_content)
        else:
          rule_content = base_dict_to_override

      # for nested title, fields, note, primary-key and cluster
      cur_parent = rule_content
      for nested_rule_name, nested_rule_content in rule_content.items():
        if nested_rule_name in ['title', 'field', 'note', 'primary-key', 'cluster'] and 'extends' in nested_rule_content:
          base_dict_to_override = parse_expand_pattern(
            nested_rule_content.pop('extends'), parent=cur_parent)(styles_to_expand)
          if not base_dict_to_override is None:
            nested_rule_content = merge_dict_recur(input=base_dict_to_override, override=nested_rule_content)
          else:
            nested_rule_content = base_dict_to_override

        rule_content[nested_rule_name] = nested_rule_content

      cur_style[rule_name] = rule_content

    yaml_data = {
      **styles_to_expand,
      "style-sheet": cur_style,
      "name": yaml_data["name"]
    }

    return yaml_data

  def _validate(self, data):
    valid, validation_errors = validate_style_schema(data)
    if not valid:
      raise ValidationError(validation_errors)

  def _parse(self, data):
    return data

  def get(self, entry=None, nested_entry=None, field=None):
    assert not entry is None
    assert not field is None

    if not nested_entry is None:
      return self.data[entry][nested_entry][field]
    else:
      return self.data[entry][field]


# def test():
#
#  import importlib.resources
#
#  def load_and_validate_style_test_file():
#    return Style(
#      importlib.resources.open_text('erd_yaml2dot.resources.styles', 'default.yaml'),
#      # open("./erd_yaml2dot/resources/styles/default.yaml", "r"),
#      validate=True)
#
#  try:
#    style = load_and_validate_style_test_file()
#  except ValidationError as err:
#    print(err)
#    raise err
#
#
# if __name__ == "__main__":
#  test()
