import argparse
import sys
import importlib
from erd_yaml2dot.core import validate_and_convert_yaml_to_dot, render_graph


def main():
  # import platform
  # if platform.system() == "Windows":
  #   import os
  #   os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'

  parser = argparse.ArgumentParser(
      description="Transform a well-formed yaml file describing entities and relationships into a proper ER diagram with graphviz."
  )
  parser.add_argument("input",
                      type=argparse.FileType('r'),
                      help="The input yaml file containing the ER data.",
                      default=sys.stdin)
  parser.add_argument("name",
                      help="The resulting graphviz file basename.")
  parser.add_argument("-s", "--style", type=argparse.FileType('r'), help="The style sheet to use to render the graph.",
                      default=importlib.resources.open_text("erd_yaml2dot.resources.styles", "default.yaml"))
  parser.add_argument("-l", "--layout", help="The layout to use to render the graph.", default="dot")
  parser.add_argument("-r", "--render",
                      help="The rendered files that will be generated (svg,pdf,png,...).",
                      default=("svg", "pdf", "png"))
  parser.add_argument("-x", "--graphviz-bin-dir",
                      help="Path to graphviz binary's directory."
                           "Will be injected in the PATH. Mostly useful for windows.",
                      default=None)
  args = parser.parse_args()
  
  if not args.graphviz_bin_dir is None:
    import os
    os.environ["PATH"] += os.pathsep + args.graphviz_bin_dir

  graph = validate_and_convert_yaml_to_dot(args.input, args.style, layout=args.layout)
  render_graph(graph, basename=args.name, format=args.render)


if __name__ == '__main__':
  main()
