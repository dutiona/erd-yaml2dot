
def rchop(s, suffix):
  if suffix and s.endswith(suffix):
    return s[:-len(suffix)]
  return s


def format_card(min, max):
  return "{}..{}".format(min, max)


def format_text_data_html(text, style):
  html = "<td bgcolor='{}' align='{}'>".format(style['bgcolor'], style['align'])
  html += "<font color='{}' face='{}' point-size='{}'>".format(style['color'], style['fontname'], style['fontsize'])
  if style['bold']:
    html += "<b>"
  if style['underlined']:
    html += "<u>"
  if style['italic']:
    html += "<i>"
  html += text
  if style['italic']:
    html += "</i>"
  if style['underlined']:
    html += "</u>"
  if style['bold']:
    html += "</b>"

  html += "</font></td>"
  return html


def format_label_entity_for_dot_text(entity_name, entity_content):
  max_size = max([len(field) for field in entity_content['fields']])
  dashes = '-' * (max_size + 2)
  label = '{}\\n{}\\n'.format(entity_name, dashes)
  for field in entity_content['fields']:
    if 'primary-key' in entity_content and field in entity_content['primary-key']:
      label += '*{}*\\n'.format(field)
    else:
      label += '{}\\n'.format(field)
  # trim last \n
  label = rchop(label, '\\n')

  return label


def format_label_relationship_for_dot_text(relationship_name, relationship_content):
  max_size = max([len(field) for field in relationship_content['fields']])
  dashes = '-' * (max_size + 2)
  label = '{}\\n{}\\n'.format(relationship_name, dashes)
  for field in relationship_content['fields']:
    label += '{}\\n'.format(field)
  # trim last \n
  label = rchop(label, '\\n')

  return label


def format_label_entity_for_dot_html(entity_name, entity_content, style, weak=False):
  prefix = "entity-weak" if weak else "entity"
  label = "    <table border='0' cellborder='0' cellspacing='0'>\n"
  label += "      <tr>{}</tr>\n".format(format_text_data_html(entity_name, style.get(prefix + '/title')))
  if 'fields' in entity_content:
    for field in entity_content['fields']:
      if 'primary-key' in entity_content and field in entity_content['primary-key']:
        label += "      <tr>{}</tr>\n".format(format_text_data_html(field, style.get(prefix + '/primary-key')))
      else:
        label += "      <tr>{}</tr>\n".format(format_text_data_html(field, style.get(prefix + '/field')))
  label += "    </table>"

  return label


def format_label_relationship_for_dot_html(relationship_name, relationship_content, style):
  label = "    <table border='0' cellborder='0' cellspacing='0'>\n"
  label += "      <tr>{}</tr>\n".format(format_text_data_html(relationship_name, style.get('relationship/title')))
  if 'fields' in relationship_content:
    for field in relationship_content['fields']:
      label += "      <tr>{}</tr>\n".format(format_text_data_html(field, style.get('relationship/field')))
  label += "    </table>"

  return label


def format_label_relationship_note_for_dot_html(relationship_name, note, style):
  label = "    <table border='0' cellborder='0' cellspacing='0'>\n"
  label += "      <tr>{}</tr>\n".format(format_text_data_html(note, style.get('relationship/note/text')))
  label += "    </table>"

  return label
