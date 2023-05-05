import os
from erd_yaml2dot.core import load_yaml_file, render_graph, validate_and_convert_yaml_to_dot
import importlib.resources


def load_erd_test_file():
  return load_yaml_file(importlib.resources.open_text('tests.resources', 'test_diagram.yaml'))


def test_render():
  import platform
  if platform.system() == "Windows":
    import os
    os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'

  graph = validate_and_convert_yaml_to_dot(
    importlib.resources.open_text('tests.resources', 'test_diagram.yaml'),
    importlib.resources.open_text("erd_yaml2dot.resources.styles", "default.yaml"))
  render_graph(graph, basename="test")
