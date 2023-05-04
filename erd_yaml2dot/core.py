import yaml
from graphviz import Digraph


def load_yaml_file(file_path):
  with open(file_path, 'r') as file:
    data = yaml.safe_load(file)
  return data


def generate_dot_diagram(yaml_data):
  dot = Digraph()

  for node, properties in yaml_data['nodes'].items():
    dot.node(node, **properties)

  for edge in yaml_data['edges']:
    dot.edge(edge['from'], edge['to'], **edge.get('properties', {}))

  return dot
