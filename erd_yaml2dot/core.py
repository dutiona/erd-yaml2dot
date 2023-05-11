import yaml
import re
import graphviz
from erd_yaml2dot.validate import validate_erd_schema
import erd_yaml2dot.format as fmt
from erd_yaml2dot.style import Style
from erd_yaml2dot.utility import load_yaml_file, eprint


def parse_card(card_str):
  card_regex = r"(0|1),(1|\*)"
  card_reg = re.compile(card_regex, re.MULTILINE | re.IGNORECASE)
  m = card_reg.match(card_str)

  return {
    'min': m.group(1),
    'max': m.group(2)
  }


def convert_yaml_to_dot(erd_yaml_data, layout, style):
  graph = graphviz.Digraph(name="ER",
                           engine=layout,
                           renderer="cairo",
                           formatter="cairo",
                           encoding="utf-8")

  graph.attr(beautify="true",
             overlap="false",
             splines="true",
             compound="true",
             rankdir="TB")

  # entities
  graph.attr('node',
             shape=style.get('entity/shape-type'),
             fontname=style.get('entity/field/fontname'),
             fontsize=str(style.get('entity/field/fontsize')),
             fillcolor=style.get('entity/fillcolor'),
             style=style.get('entity/style'))

  for entity_name, entity_content in erd_yaml_data['entities'].items():
    if 'weak' in entity_content and entity_content['weak']:
      graph.node(entity_name,
                 shape=style.get('entity-weak/shape-type'),
                 fontname=style.get('entity-weak/field/fontname'),
                 fontsize=str(style.get('entity-weak/field/fontsize')),
                 fillcolor=style.get('entity-weak/fillcolor'),
                 style=style.get('entity-weak/style'),
                 label="<\n{}\n>".format(
                   fmt.format_label_entity_for_dot_html(entity_name, entity_content, style, weak=True))
                 )
    else:
      graph.node(entity_name, label="<\n{}  \n>".format(fmt.format_label_entity_for_dot_html(
        entity_name, entity_content, style)))

  if 'clusters' in erd_yaml_data:
    if layout == "neato":
      print("WARNING: The <neato> layout engine does not support clusters. They will be ignored.\n"
            "To support clusters, use the <dot> layout enfine instead.")
    for cluster_name, cluster_content in erd_yaml_data['clusters'].items():
      with graph.subgraph(name=cluster_name) as cluster:
        cluster.attr(
          cluster="true",
          label="<\n{}  \n>".format(fmt.format_label_cluster_for_dot_html(cluster_name, style)),
          color=style.get("cluster/color"),
          bgcolor=style.get("cluster/bgcolor")
        )
        for n in cluster_content:
          cluster.node(n)

  # relationships
  graph.attr('node',
             shape=style.get('relationship/shape-type'),
             fontname=style.get('relationship/field/fontname'),
             fontsize=str(style.get('relationship/field/fontsize')),
             fillcolor=style.get('relationship/fillcolor'),
             style=style.get('relationship/style'))
  graph.attr('edge',
             fontname=style.get('relationship/field/fontname'),
             fontsize=str(style.get('relationship/field/fontsize')),
             color=style.get('relationship/field/color'))

  for relationship_name, relationship_content in erd_yaml_data['relationships'].items():
    graph.node(relationship_name, label="<\n{}  \n>".format(fmt.format_label_relationship_for_dot_html(
      relationship_name, relationship_content, style)))

    # Notes
    if 'notes' in relationship_content and len(relationship_content['notes']) > 0:
      for num, note in zip(range(1, len(relationship_content['notes']) + 1), relationship_content['notes']):
        note_name = relationship_name + " --- note-{}".format(num)
        graph.node(note_name,
                   shape=style.get('relationship/note/shape/shape-type'),
                   fontname=style.get('relationship/note/text/fontname'),
                   fontsize=str(style.get('relationship/note/text/fontsize')),
                   fillcolor=style.get('relationship/note/shape/fillcolor'),
                   style=style.get('relationship/note/shape/style'),
                   label="<\n{}  \n>".format(fmt.format_label_relationship_note_for_dot_html(note, style)))
        graph.edge(note_name, relationship_name,
                   arrowhead="vee",
                   style="dotted",
                   arrowtail="none")

  for relationship_name, relationship_content in erd_yaml_data['relationships'].items():
    # switch case for self relationships
    if len(relationship_content['entities'].keys()) == 1:
      self_lined_entity, self_lined_cardinality = list(relationship_content['entities'].items())[0]
      card = parse_card(self_lined_cardinality)

      if 'clusters' in erd_yaml_data and linked_entity in list(erd_yaml_data['clusters'].keys()):
        first_entity = erd_yaml_data['clusters'][linked_entity][0]
        graph.edge(first_entity, relationship_name,
                   label=fmt.format_card(card['min'], card['max']),
                   ltail=linked_entity,
                   arrowhead="none",
                   arrowtail="none")
        graph.edge(relationship_name, first_entity,
                   label=fmt.format_card(card['min'], card['max']),
                   lhead=linked_entity,
                   arrowhead="none",
                   arrowtail="none")
      else:
        graph.edge(self_lined_entity, relationship_name,
                   label=fmt.format_card(card['min'], card['max']),
                   arrowhead="none",
                   arrowtail="none")
        graph.edge(relationship_name, self_lined_entity,
                   label=fmt.format_card(card['min'], card['max']),
                   arrowhead="none",
                   arrowtail="none")
    else:
      for linked_entity, cardinality in relationship_content['entities'].items():
        card = parse_card(cardinality)
        if 'clusters' in erd_yaml_data and linked_entity in list(erd_yaml_data['clusters'].keys()):
          first_entity = erd_yaml_data['clusters'][linked_entity][0]
          graph.edge(first_entity, relationship_name,
                     label=fmt.format_card(card['min'], card['max']),
                     ltail=linked_entity,
                     arrowhead="none",
                     arrowtail="none")
        else:
          graph.edge(linked_entity, relationship_name,
                     label=fmt.format_card(card['min'], card['max']),
                     arrowhead="none",
                     arrowtail="none")

  return graph


def validate_and_convert_yaml_to_dot(input_stream, style_stream, layout="dot"):
  erd_yaml_data = load_yaml_file(input_stream)
  valid, validation_errors = validate_erd_schema(erd_yaml_data)
  if not valid:
    eprint(str(validation_errors))
    return None

  return convert_yaml_to_dot(erd_yaml_data, layout, Style(style_stream))


def render_graph(graph, basename, format=('png', 'svg', 'pdf')):
  for f in format:
    graph.render(format=f, outfile=basename + "." + f)
