import yaml


def eprint(*args, **kwargs):
  import sys
  print(*args, file=sys.stderr, **kwargs)


def load_yaml_file(file_stream):
  return yaml.safe_load(file_stream)


def save_yaml_file(yaml_data, file_stream):
  file_stream.write(yaml.dump(yaml_data))
