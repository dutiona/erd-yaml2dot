import argparse
import sys
import yaml
import re
import graphviz


def format_for_dot(rel_name, rel_dict, html=True, with_pk=False):
  if html:
    label = "    <table border='0' cellborder='0' cellspacing='0'>\n"
    label += "      <tr><td bgcolor='darkgrey'><b><u>{}</u></b></td></tr>\n".format(
        rel_name)
    for field in rel_dict['fields']:
      if with_pk and 'primary key' in rel_dict and field in rel_dict['primary key']:
        label += "      <tr><td align='left'><b>{}</b></td></tr>\n".format(
            field)
      else:
        label += "      <tr><td align='left'>{}<br/></td></tr>\n".format(
            field)
    label += "    </table>"

    return '"{}" [label=<\n{}\n  >];'.format(rel_name, label)

  else:
    max_size = max([len(field) for field in rel_dict['fields']])
    dashes = '-' * (max_size + 2)
    label = '{}\\n{}\\n'.format(entity_name, dashes)
    for field in rel_dict['fields']:
      if with_pk and 'primary key' in rel_dict and field in rel_dict['primary key']:
        label += '*{}*\\n'.format(field)
      else:
        label += '{}\\n'.format(field)
    # trim last \n
    label = rchop(label, '\\n')

    return '"{}" [label="{}"];'.format(rel_name, label)


def format_card(min, max):
  return "{}..{}".format(min, max)


def write_er_data_to_graphviz(out_stream, er_data, html=True, title_top=False):
  # TODO: handle notes

  out_stream.write(
      "digraph ER {\n"
      "  layout=neato;\n"
      "  rankdir=TB;\n"
      "  overlap=false;\n"
      "  // Properties for entities\n"
      "  node [shape=box, fontname=\"Courier\", fontsize=12, style=filled, fillcolor=\"lightgrey\"];\n"
      "  edge [fontname=\"Courier\", fontsize=10];\n")

  # Title Top
  if title_top:
    out_stream.write(
        '  label = "\\n\\n{}";\n  fontsize=16;\n'.format(er_data['title']))
  # Entities
  out_stream.write("\n  // ENTITIES\n\n")
  for entity_name, entity_content in er_data['entities'].items():
    formatted_entity = format_for_dot(
        entity_name, entity_content, html=html, with_pk=True)
    out_stream.write(
        "  // Entity {}\n  {}\n".format(entity_name, formatted_entity))

  # Relationships
  out_stream.write("\n // RELATIONSHIPS\n\n")
  out_stream.write("node [shape=diamond,style=filled,color=grey];\n")

  # Add the shape of the relationships
  for relationship_name, relationship_content in er_data['relationships'].items():
    if not "fields" in relationship_content:
      if not html:
        out_stream.write('"{}";\n'.format(relationship_name))
      else:
        out_stream.write('"{}" [label=< <table border=\'0\' cellborder=\'0\' cellspacing=\'0\'>'
                         '<tr><td bgcolor=\'darkgrey\'><b><u>'
                         '{}</u></b></td></tr></table> >];\n'.format(relationship_name,
                                                                     relationship_name))
    else:
      formatted_relationship = format_for_dot(
          relationship_name, relationship_content, html=html, with_pk=False)
      out_stream.write("{}\n".format(formatted_relationship))

  # Add the links between the relationships
  out_stream.write("\n  // RELATIONSHIPS LINKS\n\n")
  for relationship_name, relationship_content in er_data['relationships'].items():
    lhs_card = relationship_content['lhs-card']
    out_stream.write('  "{}" -> "{}" [label="{}", arrowhead=none];\n'.format(
        relationship_content['lhs'], relationship_name, format_card(lhs_card['min'], lhs_card['max'])))
    rhs_card = relationship_content['rhs-card']
    out_stream.write('  "{}" -> "{}" [label="{}", arrowhead=none];\n\n'.format(
        relationship_content['rhs'], relationship_name, format_card(rhs_card['min'], rhs_card['max'])))

  # Title
  if not title_top:
    out_stream.write(
        '  label = "\\n\\n{}";\n  fontsize=16;\n'.format(er_data['title']))
  out_stream.write("}\n")


def main():
  import platform
  if platform.system() == "Windows":
    import os
    os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'

  parser = argparse.ArgumentParser(
      description="Transform a well-formed yaml file describing entities and relationships into a proper ER diagram with graphviz."
  )
  parser.add_argument("input",
                      type=argparse.FileType('r'),
                      help="The input yaml file containing the ER data.",
                      default=sys.stdin)
  parser.add_argument("output",
                      type=argparse.FileType('w'),
                      help="The resulting graphviz files to write.",
                      default=sys.stdout)
  args = parser.parse_args()

  er_data = parse_er_yaml_data(args.input)

  write_er_data_to_graphviz(args.output, er_data)
  # Write png, svg and pdf file
  dot_string = args.output.close()
  with open(args.output.name, "r") as dot_file:
    graph = graphviz.Source(dot_file.read(), filename=args.output.name)
    graph.render(format='png')
    graph.render(format='svg')
    graph.render(format='pdf')


if __name__ == '__main__':
  main()
