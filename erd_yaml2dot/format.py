
def rchop(s, suffix):
  if suffix and s.endswith(suffix):
    return s[:-len(suffix)]
  return s


def format_label_entity_for_dot(entity_name, entity_content, html=True, with_pk=False):
  if html:
    label = "    <table border='0' cellborder='0' cellspacing='0'>\n"
    label += "      <tr><td bgcolor='darkgrey'><b><u>{}</u></b></td></tr>\n".format(
        entity_name)
    for field in entity_content['fields']:
      if with_pk and 'primary key' in entity_content and field in entity_content['primary key']:
        label += "      <tr><td align='left'><b>{}</b></td></tr>\n".format(
            field)
      else:
        label += "      <tr><td align='left'>{}<br/></td></tr>\n".format(
            field)
    label += "    </table>"

    # return '"{}" [label=<\n{}\n  >];'.format(entity_name, label)
    return label

  else:
    max_size = max([len(field) for field in entity_content['fields']])
    dashes = '-' * (max_size + 2)
    label = '{}\\n{}\\n'.format(entity_name, dashes)
    for field in entity_content['fields']:
      if with_pk and 'primary key' in entity_content and field in entity_content['primary key']:
        label += '*{}*\\n'.format(field)
      else:
        label += '{}\\n'.format(field)
    # trim last \n
    label = rchop(label, '\\n')

    # return '"{}" [label="{}"];'.format(entity_name, label)
    return label


def format_label_relationship_for_dot(rel_name, rel_dict, html=True, with_pk=False):
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

    # return '"{}" [label=<\n{}\n  >];'.format(rel_name, label)
    return label

  else:
    max_size = max([len(field) for field in rel_dict['fields']])
    dashes = '-' * (max_size + 2)
    label = '{}\\n{}\\n'.format(rel_name, dashes)
    for field in rel_dict['fields']:
      if with_pk and 'primary key' in rel_dict and field in rel_dict['primary key']:
        label += '*{}*\\n'.format(field)
      else:
        label += '{}\\n'.format(field)
    # trim last \n
    label = rchop(label, '\\n')

    # return '"{}" [label="{}"];'.format(rel_name, label)
    return label


def format_card(min, max):
  return "{}..{}".format(min, max)
