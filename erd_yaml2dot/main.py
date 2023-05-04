import argparse
from erd_yaml2dot.core import load_yaml_file  # , generate_dot_diagram


def main():
  parser = argparse.ArgumentParser(
      description='Generate DOT diagrams from YAML files using Python and Graphviz')
  parser.add_argument('input_yaml', help='Path to the input YAML file')
  parser.add_argument('-o', '--output', default='output.gv',
                      help='Path to the output DOT file (default: output.gv)')
  args = parser.parse_args()

  yaml_data = load_yaml_file(args.input_yaml)
  # dot_diagram = generate_dot_diagram(yaml_data)
  # dot_diagram.render(args.output, view=True)


if __name__ == '__main__':
  main()
