import yaml
import jsonschema
import importlib.resources


def load_schema():
  with importlib.resources.open_text('erd_yaml2dot.resources', 'erd_schema.yaml') as file:
    return yaml.safe_load(file)


def validate_entities(yaml_to_validate):
  # 2 constraints are not checked with the schema (limitations):
  #   - the fields in primary_key is properly declared (in fields)
  #   - fields name are unique

  validation_errors = []

  entities = yaml_to_validate['entities']

  for entity_name, entity_content in entities.items():

    for field in entity_content['']:
      nb = entity_content['fields'].count(field)
      if nb > 1:
        validation_errors.append(
          "ERROR: In entity <{}> duplicate field named <{}> ({}). Fields must have a unique name."
            .format(entity_name, field, nb))

  for entity_name, entity_content in entities.items():
    # Check that field exists if primary key exist
    if 'primary_keys' in entity_content and not 'fields' in entity_content:
      validation_errors.append(
          "ERROR: In entity <{}> primary_key is declared with no fields.".format(entity_name))

    # Check unique field names
    if 'fields' in entity_content:
      for field in entity_content['fields']:
        nb = entity_content['fields'].count(field)
        if nb > 1:
          validation_errors.append(
            "ERROR: In entity <{}> duplicate field named <{}> ({}). Fields must have a unique name."
              .format(entity_name, field, nb))

    # Check that primary key exists in fields
    if 'primary_keys' in entity_content and 'fields' in entity_content:
      for pk_field in entity_content['primary_key']:
        if not pk_field in entity_content['fields']:
          validation_errors.append(
            "ERROR: In entity <{}> primary key <{}> is not a field declared in fields (existing fields: <>)."
              .format(entity_name, pk_field, entity_content['fields']))

  return validation_errors


def validate_relationships(yaml_to_validate):
  #  2 constraints are not checked with the schema (limitations):
  #    - the entities referenced in relationships exists in entities
  #    - that the additional fields are unique
  validation_errors = []

  entities = yaml_to_validate['entities']
  relationships = yaml_to_validate['relationships']

  return validation_errors


def validate_schema(yaml_to_validate):
  valid = True
  validation_errors = []

  schema_data = load_schema()

  try:
    jsonschema.validate(instance=yaml_to_validate, schema=schema_data)
    # Success
  except jsonschema.exceptions.ValidationError as e:
    # Failure
    valid = False
    validation_errors.append(e)

  errors_entities = validate_entities(yaml_to_validate)
  if not errors_entities:  # list not empty
    valid = False
    validation_errors += errors_entities

  errors_relationships = validate_relationships(yaml_to_validate)
  if not errors_relationships:  # list not empty
    valid = False
    validation_errors += errors_relationships

  return (valid, validation_errors)


def main():
  pass


if __name__ == "__main__":
  main()
