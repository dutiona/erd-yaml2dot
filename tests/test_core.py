import os
import yaml
from erd_yaml2dot.core import load_yaml_file, generate_dot_diagram


def test_load_yaml_file():
  test_file = 'test.yaml'
  test_data = {
      'nodes': {
          'A': {'label': 'Node A'},
          'B': {'label': 'Node B'},
      },
      'edges': [
          {'from': 'A', 'to': 'B'}
      ]
  }

  with open(test_file, 'w') as file:
    yaml.dump(test_data, file)

  loaded_data = load_yaml_file(test_file)
  os.remove(test_file)
  assert loaded_data == test_data


def test_generate_dot_diagram():
  yaml_data = {
      'nodes': {
          'A': {'label': 'Node A'},
          'B': {'label': 'Node B'},
      },
      'edges': [
          {'from': 'A', 'to': 'B'}
      ]
  }

  dot_diagram = generate_dot_diagram(yaml_data)
  assert 'Node A' in str(dot_diagram)
  assert 'Node B' in str(dot_diagram)
  assert 'A -> B' in str(dot_diagram)
