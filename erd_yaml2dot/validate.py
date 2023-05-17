import yaml
import jsonschema
import importlib.resources
from erd_yaml2dot.utility import eprint  # , save_yaml_file


def load_erd_schema():
  with importlib.resources.open_text('erd_yaml2dot.resources.schemas', 'erd_schema.yaml') as file:
    return yaml.safe_load(file)


def validate_entities(yaml_to_validate):
  # 2 constraints are not checked with the schema (limitations):
  #   - the fields in primary-key is properly declared (in fields)
  #   - fields name are unique
  #   - a weak entity is required to be in a relationship with a non-weak (strong) entity.

  validation_errors = []

  entities = yaml_to_validate['entities']
  known_entities_fields = ['fields', 'primary-key', 'weak']

  for entity_name, entity_content in entities.items():
    for k in entity_content.keys():
      if not k in known_entities_fields:
        print("WARNING: In entity <{}>: unknown field <{}> will be ignored!"
              .format(entity_name, k))

    if 'fields' in entity_content:
      for field in entity_content['fields']:
        nb = entity_content['fields'].count(field)
        if nb > 1:
          validation_errors.append(
            "ERROR: In entity <{}> duplicate field named <{}> ({}). Fields must have a unique name."
              .format(entity_name, field, nb))

  for entity_name, entity_content in entities.items():
    # Check that field exists if primary key exist
    if 'primary-keys' in entity_content and not 'fields' in entity_content:
      validation_errors.append(
          "ERROR: In entity <{}> primary-key is declared with no fields.".format(entity_name))

    # Check unique field names
    if 'fields' in entity_content:
      for field in entity_content['fields']:
        nb = entity_content['fields'].count(field)
        if nb > 1:
          validation_errors.append(
            "ERROR: In entity <{}> duplicate field named <{}> ({}). Fields must have a unique name."
              .format(entity_name, field, nb))

    # Check that primary key exists in fields
    if 'primary-key' in entity_content and 'fields' in entity_content:
      for pk_field in entity_content['primary-key']:
        if not pk_field in entity_content['fields']:
          validation_errors.append(
            "ERROR: In entity <{}> primary key <{}> is not a field declared in fields (existing fields: <{}>)."
              .format(entity_name, pk_field, entity_content['fields']))

    # Check if the weak entity is associated with at least one strong entity
    if 'weak' in entity_content and entity_content['weak']:
      for relationship_name, relationship_content in yaml_to_validate['relationships'].items():
        if 'entities' in relationship_content and entity_name in relationship_content['entities']:
          linked_entities = [linked_e for linked_e in relationship_content['entities'].keys() if linked_e in entities]
          if not any([not ('weak' in entities[linked_e] and not entities[linked_e]['weak']) for linked_e in linked_entities]):
            validation_errors.append(
                "ERROR: The *weak* entity <{}> is not in a relationship with at least one non-weak (strong) entity."
                "In a relationship with <{}>"
                .format(entity_name, linked_entities))

  return validation_errors


def validate_relationships(yaml_to_validate):
  #  2 constraints are not checked with the schema (limitations):
  #    - the entities referenced in relationships exists in entities
  #    - that the additional fields are unique
  validation_errors = []

  entities = yaml_to_validate['entities']
  relationships = yaml_to_validate['relationships']
  relationships_known_fields = ['entities', 'fields', 'notes']

  for relationship_name, relationship_content in relationships.items():
    for k in relationship_content.keys():
      if not k in relationships_known_fields:
        print("WARNING: In relationship <{}>: unknown field <{}> will be ignored!"
              .format(relationship_name, k))

    # Check that referenced entities do exist
    if 'clusters' in yaml_to_validate:
      clusters = yaml_to_validate['clusters']
      entities_name = list(entities.keys())
      clusters_name = list(clusters.keys())
      for entity in relationship_content['entities'].keys():
        if not entity in [*entities_name, *clusters_name]:
          validation_errors.append(
              "ERROR: In relationship <{}> the entity named <{}> is not declared! (existing entities: <{}>)."
              .format(relationship_name, entity, entities_name))

    # Check that (optional) fields are uniques
    if 'fields' in relationship_content:
      for field in relationship_content['fields']:
        nb = relationship_content['fields'].count(field)
        if nb > 1:
          validation_errors.append(
            "ERROR: In relationship <{}> duplicate field named <{}> ({}). Fields must have a unique name."
              .format(relationship_name, field, nb))

  return validation_errors


def validate_clusters(yaml_to_validate):
  validation_errors = []

  if 'clusters' in yaml_to_validate:
    entities = list(yaml_to_validate['entities'].keys())
    relationships = list(yaml_to_validate['relationships'].keys())
    all = entities + relationships

    for cluster_name, cluster_content in yaml_to_validate['clusters'].items():
      for elem in cluster_content:
        if not elem in all:
          validation_errors.append(
            "ERROR: In cluster <{}>, element (entity or relationship) named <{}>  does not exist! "
            "(Elements considered = <{}>).".format(cluster_name, elem, all))

  return validation_errors


def validate_erd_schema(yaml_to_validate):
  valid = True
  validation_errors = []

  schema_data = load_erd_schema()

  # with open("./test_diagram_bis.yaml", "w") as fp:
  #   save_yaml_file(yaml_to_validate, fp)

  try:
    jsonschema.validate(instance=yaml_to_validate, schema=schema_data)
    # Success
  except jsonschema.exceptions.ValidationError as e:
    # Failure
    valid = False
    validation_errors.append(e)

  errors_entities = validate_entities(yaml_to_validate)
  if len(errors_entities) > 0:   # list not empty
    valid = False
    validation_errors = validation_errors + errors_entities

  errors_relationships = validate_relationships(yaml_to_validate)
  if len(errors_relationships):  # list not empty
    valid = False
    validation_errors = validation_errors + errors_relationships

  errors_clusters = validate_clusters(yaml_to_validate)
  if len(errors_clusters):  # list not empty
    valid = False
    validation_errors = validation_errors + errors_clusters

  return (valid, validation_errors)


def load_style_schema():
  with importlib.resources.open_text('erd_yaml2dot.resources.schemas', 'style_schema.yaml') as file:
    return yaml.safe_load(file)


def validate_style_schema(yaml_to_validate):
  valid = True
  validation_errors = []

  schema_data = load_style_schema()

  try:
    jsonschema.validate(instance=yaml_to_validate, schema=schema_data)
    # Success
  except jsonschema.exceptions.ValidationError as e:
    # Failure
    valid = False
    validation_errors.append(e)
  except jsonschema.exceptions.SchemaError as e:
    eprint("".join(str(e)))
    raise e

  return (valid, validation_errors)
