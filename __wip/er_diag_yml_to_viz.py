import argparse
import sys
import yaml
import re
import graphviz

card_regex = r"(0|1),(1|\*)"
error = False


def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)
  error = True


def parse_er_yaml_data(input_stream):
  card_reg = re.compile(card_regex, re.MULTILINE | re.IGNORECASE)

  data = yaml.safe_load(input_stream)

  # TODO verify entities and fields are unique
  # TODO verify relationships are unique

  # Basic validating
  assert 'title' in data and 'entities' in data and 'relationships' in data

  title = data['title']
  entities = data['entities']
  relationships = data['relationships']

  # Validating entities
  mandatory_entity_fields = ['fields', 'primary key']
  optional_entity_fields = []
  entities_name = entities.keys()

  for entity_name, entity_content in entities.items():
    # Print ignored unknown fields
    for k in entity_content.keys():
      if not (k in mandatory_entity_fields) and not (
              k in optional_entity_fields):
        print(
            "WARNING: In entity <{}>: unknown field <{}> will be ignored!"
            .format(entity_name, k))
    # Check for mandatory fields
    for mandatory_field in mandatory_entity_fields:
      if not mandatory_field in entity_content.keys():
        eprint("ERROR: In entity <{}>: missing mandatory field <{}>!".
               format(entity_name, mandatory_field))

    # Check if fields in primary keys are valid field
    for pk_field in entity_content['primary key']:
      if not pk_field in entity_content['fields']:
        eprint(
            "ERROR: In entity <{}>: field <{}> is a primary key it does not exist!"
            .format(entity_name, pk_field))

  # Validating relationships
  mandatory_relationship_field = ['lhs', 'lhs-card', 'rhs', 'rhs-card']
  optional_relationship_fields = ['fields', 'note']

  for relationship_name, relationship_content in relationships.items():
    # Print ignored unknown fields
    for k in relationship_content.keys():
      if not (k in mandatory_relationship_field) and not (
              k in optional_relationship_fields):
        print(
            "WARNING: In relationship <{}>: unknown field <{}> will be ignored!"
            .format(relationship_name, k))

    # Check for mandatory fields
    for mandatory_field in mandatory_relationship_field:
      if not mandatory_field in relationship_content.keys():
        eprint(
            "ERROR: In relationship <{}>: missing mandatory field <{}>!"
            .format(relationship_name, mandatory_field))

    # Check for entity existence in the relationship
    if not relationship_content['lhs'] in entities_name:
      eprint("ERROR: In relationship <{}>: entity <{}> does not exist!".
             format(relationship_name, relationship_content['lhs']))
    if not relationship_content['rhs'] in entities_name:
      eprint("ERROR: In relationship <{}>: entity <{}> does not exist!".
             format(relationship_name, relationship_content['rhs']))

    # Check cardinality formatting
    if m := card_reg.match(relationship_content['lhs-card']):
      data['relationships'][relationship_name]['lhs-card'] = {
          'min': m.group(1),
          'max': m.group(2)
      }
    else:
      eprint(
          "ERROR: In relationship <{}>: cardinality <{}> for entity <{}> is wrong!"
          .format(relationship_name, relationship_content['lhs-card'],
                  relationship_content['lhs']))

    if m := card_reg.match(relationship_content['rhs-card']):
      data['relationships'][relationship_name]['rhs-card'] = {
          'min': m.group(1),
          'max': m.group(2)
      }
    else:
      eprint(
          "ERROR: In relationship <{}>: cardinality <{}> for entity <{}> is wrong!"
          .format(relationship_name, relationship_content['rhs-card'],
                  relationship_content['rhs']))

  # kill program on error
  assert error == False

  return data


def rchop(s, suffix):
  if suffix and s.endswith(suffix):
    return s[:-len(suffix)]
  return s


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
