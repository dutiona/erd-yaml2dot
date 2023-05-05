import yaml
import sys
import re
import importlib.resources
import graphviz
from erd_yaml2dot.validate import validate_erd_schema, validate_style_schema
from erd_yaml2dot.format import format_label_entity_for_dot_html, format_label_relationship_for_dot_html, format_card
from pprint import pprint


def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)
  error = True


def load_yaml_file(file_stream):
  return yaml.safe_load(file_stream)


def merge_dict(input, override):
  ret = input.copy()
  for k, v in override.items():
    ret[k] = v
  return ret


def expand_style_yaml_data(yaml_data):

  yaml_proper = {}
  yaml_proper['name'] = yaml_data['name']
  yaml_proper['style'] = {}

  styles_to_expand = {}
  for style_name, style_content in yaml_data.items():
    if style_name.startswith("."):
      styles_to_expand[style_name] = style_content

  # unpack style for entity and relationships
  for rule_name, rule_content in yaml_data['style'].items():
    if rule_name in ['entity', 'relationship'] and 'extends' in rule_content:
      style_to_override = rule_content.pop('extends')
      rule_content = merge_dict(styles_to_expand[style_to_override], rule_content)
      yaml_proper['style'][rule_name] = rule_content

    # for nested title, fields, note
    for nested_rule_name, nested_rule_content in rule_content.items():
      if nested_rule_name in ['title', 'field', 'note', 'primary_key'] and 'extends' in nested_rule_content:
        style_to_override = nested_rule_content.pop('extends')
        nested_rule_content = merge_dict(styles_to_expand[style_to_override], nested_rule_content)
        rule_content[nested_rule_name] = nested_rule_content
    yaml_proper['style'][rule_name] = rule_content

  return yaml_proper


def load_style(file_stream):
  return expand_style_yaml_data(load_yaml_file(file_stream))


def parse_card(card_str):
  card_regex = r"(0|1),(1|\*)"
  card_reg = re.compile(card_regex, re.MULTILINE | re.IGNORECASE)
  m = card_reg.match(card_str)

  return {
    'min': m.group(1),
    'max': m.group(2)
  }


def convert_yaml_to_dot(erd_yaml_data, layout, style_yaml_data, html=True):
  graph = graphviz.Digraph(name="ER",
                           engine=layout,
                           renderer="cairo",
                           formatter="cairo",
                           encoding="utf-8")

  graph.attr(beautify="true",
             overlap="false",
             splines="true",
             rankdir="TB")

  # entities
  graph.attr('node',
             shape=style_yaml_data['entity']['shape'],
             fontname=style_yaml_data['entity']['fontname'],
             fontsize=str(style_yaml_data['entity']['fontsize']),
             fillcolor=style_yaml_data['entity']['fillcolor'],
             style=style_yaml_data['entity']['style'])

  for entity_name, entity_content in erd_yaml_data['entities'].items():
    graph.node(entity_name, label="<\n{}\n>".format(format_label_entity_for_dot_html(
      entity_name, entity_content, style_yaml_data['entity'])))

  # relationships
  graph.attr('node',
             shape=style_yaml_data['relationship']['shape'],
             fontname=style_yaml_data['relationship']['fontname'],
             fontsize=str(style_yaml_data['relationship']['fontsize']),
             fillcolor=style_yaml_data['relationship']['fillcolor'],
             style=style_yaml_data['relationship']['style'])
  graph.attr('edge',
             fontname=style_yaml_data['relationship']['fontname'],
             fontsize=str(style_yaml_data['relationship']['fontsize']),
             color=style_yaml_data['relationship']['color']
             )

  for relationship_name, relationship_content in erd_yaml_data['relationships'].items():
    graph.node(relationship_name, label="<\n{}\n>".format(format_label_relationship_for_dot_html(
      relationship_name, relationship_content, style_yaml_data['relationship'])))

  for relationship_name, relationship_content in erd_yaml_data['relationships'].items():
      # switch case for self relationships
    if len(relationship_content['entities'].keys()) == 1:
      self_lined_entity, self_lined_cardinality = list(relationship_content['entities'].items())[0]
      card = parse_card(self_lined_cardinality)

      graph.edge(self_lined_entity, relationship_name,
                 label=format_card(card['min'], card['max']),
                 arrowhead="none",
                 arrowtail="none",
                 arrowsize="2")
      graph.edge(relationship_name, self_lined_entity,
                 label=format_card(card['min'], card['max']),
                 arrowhead="none",
                 arrowtail="none",
                 arrowsize="2")
    else:
      for linked_entity, cardinality in relationship_content['entities'].items():
        card = parse_card(cardinality)
        graph.edge(linked_entity, relationship_name,
                   label=format_card(card['min'], card['max']),
                   arrowhead="none",
                   arrowtail="none",
                   arrowsize="2")

  # TODO notes & cluster

  return graph


def validate_and_convert_yaml_to_dot(input_stream, style_stream, layout="dot", html=True):
  erd_yaml_data = load_yaml_file(input_stream)
  valid, validation_errors = validate_erd_schema(erd_yaml_data)
  if not valid:
    eprint("\n".join(validation_errors))
    return None

  style_yaml_data = load_style(style_stream)
  valid, validation_errors = validate_style_schema(style_yaml_data)

  if not valid:
    eprint("\n".join(validation_errors))
    return None

  return convert_yaml_to_dot(erd_yaml_data, layout, style_yaml_data['style'], html=html)


def render_graph(graph, basename, format=('png', 'svg', 'pdf')):
  for f in format:
    graph.render(format=f, outfile=basename + "." + f)
