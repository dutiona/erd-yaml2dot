from erd_yaml2dot.core import render_graph, validate_and_convert_yaml_to_dot
import importlib.resources


def test_render():
  import platform
  if platform.system() == "Windows":
    import os
    os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'

  # graph = validate_and_convert_yaml_to_dot(
  #  importlib.resources.open_text('tests.resources', 'test_diagram.yaml'),
  #  importlib.resources.open_text("erd_yaml2dot.resources.styles", "default.yaml"))
  # render_graph(graph, basename="test")
