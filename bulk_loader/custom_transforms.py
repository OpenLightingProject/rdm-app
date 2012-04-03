
def list(fn):
  """Return function that returns a list of objects.

  Args:

  Returns:
  """
  def to_list_lambda(value):
    if not value:
      return None
    x = eval(value)
    if len(x) > 0:
      return map(fn, x)
    return None

  return to_list_lambda


def export_list(fn):
  def list_to_string(values):
    if not values:
      return ''
    output = []
    for v in values:
      output.append(fn(v))
    return '[' + ','.join(output) + ']'

  return list_to_string
