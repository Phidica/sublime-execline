import logging
import os
import re
import sublime

# external dependencies (see dependencies.json)
import jsonschema
import yaml # pyyaml


# This plugin generates a hidden syntax file containing rules for additional
# chainloading commands defined by the user. The syntax is stored in the cache
# directory to avoid the possibility of it falling under user version control in
# the usual packages directory


userSyntaxName = 'execline-user-chainload.sublime-syntax'

pkgName = 'execline'
settingsName = 'execline.sublime-settings'
mainSyntaxPath = 'Packages/{}/execline.sublime-syntax'.format(pkgName)
schemaPath = 'Packages/{}/execline.sublime-settings.schema.json'.format(pkgName)

ruleNamespaces = {
  'keyword': 'keyword.other',
  'function': 'support.function',
}
ruleContexts = {
  'argument': {
    'generic': 'command-call-common-arg-aside-&pop',
    'variable': 'command-call-common-variable-&pop',
    'pattern': 'command-call-common-glob-&pop',
  },
  'block': {
    'program': 'block-run-prog',
    'arguments': 'block-run-arg',
    'trap': 'block-trap',
    'multidefine': 'block-multidefine',
  },
  'options': {
    'list': 'command-call-common-opt-list-&pop',
    'list-with-args': {
      'match': '(?=-[{}])',
      'push': 'command-call-common-opt-arg-&pop',
      'include': 'command-call-common-opt-list-&pop',
    },
  },
}


logging.basicConfig()
logger = logging.getLogger(__name__)


# Fully resolve the name of a context in the main syntax file
def _resolve_context(context):
  return mainSyntaxPath + '#' + context


# Create a match rule describing a command of a certain type, made of a list of
# elements
def _make_rule(cmd_name, cmd_elements, cmd_type):
  try:
    namespace = ruleNamespaces[cmd_type]
  except KeyError:
    logger.warning("Ignoring command of unrecognised type '{}'".format(cmd_type))
    return

  rule = {}

  # Careful to sanitise user input. Only literal command names accepted here
  rule['match'] = r'{{chain_pre}}' + re.escape(cmd_name) + r'{{chain_post}}'

  rule['scope'] = ' '.join([
    'meta.function-call.name.execline',
    '{}.user.{}.execline'.format(namespace, cmd_name),
    'meta.string.unquoted.execline',
  ])

  contextSeq = []

  for elem in cmd_elements:
    context = None

    # Resolve the element into a name and possible argument
    elemType,elemSubtype = elem[0:2]
    try:
      elemArg = elem[2]
    except IndexError:
      elemArg = ''

    # Look up the context named by this element
    try:
      contextData = ruleContexts[elemType][elemSubtype]
      if isinstance(contextData, str):
        contextData = { 'include': contextData }
    except KeyError:
      logger.warning("Ignoring key '{}' not found in context dictionary".format(elem))
      continue

    if len(contextData) > 1 and not elemArg:
      logger.warning("Ignoring element '{}' with missing data".format(elem))
      continue

    if len(contextData) == 1:
      # context = _resolve_context(contextData['include'])
      # Although a basic include could be provided as the target context name
      # directly to the 'push' list, this can break if there are a mix of other
      # types of contexts being pushed to the stack. A context containing a sole
      # include is safe from this
      context = [ {'include': _resolve_context(contextData['include'])} ]
    elif elemType == 'options':
      # Careful to sanitise user input, this must behave as a list of characters
      matchPattern = contextData['match'].format( re.escape(elemArg) )

      context = [
        {'match': matchPattern, 'push': _resolve_context(contextData['push'])},
        {'include': _resolve_context(contextData['include'])},
      ]

    if context:
      contextSeq.append(context)

  # Convert context sequence into context stack
  if contextSeq:
    rule['push'] = contextSeq
    rule['push'].reverse()

  return rule


def _validate_settings():
  # Read the schema using Sublime Text's builtin JSON parser
  try:
    schema = sublime.decode_value( sublime.load_resource(schemaPath) )
  except Exception as ex:
    logger.error("Failed loading schema: {}".format(ex))
    return validSets

  settings = sublime.load_settings(settingsName)
  activeSets = settings.get('user_chainload_active')

  if not activeSets:
    return []

  validSets = []
  for setName in activeSets:
    if not setName:
      sublime.error_message("Error in {}: Set name cannot be the empty string".format(settingsName))
      continue

    setName = 'user_chainload_set_' + setName
    setDict = settings.get(setName)

    if setDict == None:
      sublime.error_message("Error in {}: Couldn't find expected setting '{}'".format(settingsName, setName))
      continue

    try:
      jsonschema.validate(setDict, schema)
      logger.debug("Validation success for {}".format(setName))
      validSets.append(setName)
    except jsonschema.exceptions.SchemaError as ex:
      # A problem in the schema itself for me as the developer to resolve
      logger.error("Failed validating schema: {}".format(ex))
      break
    except jsonschema.exceptions.ValidationError as ex:
      # A problem in the settings file for the user to resolve
      sublime.error_message("Error in {} in setting '{}': \n{}".format(settingsName, setName, str(ex)))
      continue

  return validSets if validSets else None


def _write_user_chainload():
  # Read settings file and validate
  settings = sublime.load_settings(settingsName)
  validSets = _validate_settings()

  # Prepare output syntax file
  cacheDir = os.path.join(sublime.cache_path(), pkgName)
  if not os.path.isdir(cacheDir):
    os.mkdir(cacheDir)

  userSyntaxPath = os.path.join(cacheDir, userSyntaxName)
  userSyntaxExists = os.path.isfile(userSyntaxPath)

  # Skip writing the syntax if it already exists in a valid form and we don't
  # have a valid set of rules for regenerating it
  if userSyntaxExists:
    if validSets == None:
      logger.warning("Not regenerating syntax due to lack of any valid settings")
      return
    else:
      logger.info("Regenerating syntax with sets: {}".format(validSets))
  else:
    logger.info("Generating syntax with sets: {}".format(validSets))

  userSyntax = open(userSyntaxPath, 'w')

  # Can't seem to get PyYAML to write a header, so do it manually
  header = '\n'.join([
    r'%YAML 1.2',
    r'# THIS IS AN AUTOMATICALLY GENERATED FILE.',
    r'# DO NOT EDIT. CHANGES WILL BE LOST.',
    r'---',
    '',
  ])
  userSyntax.write(header)

  yaml.dump({'hidden': True, 'scope': 'source.shell.execline'}, userSyntax)

  # Repeat all the variables from the main syntax file, for convenience
  mainDB = yaml.load(sublime.load_resource(mainSyntaxPath),
    Loader = yaml.BaseLoader)
  yaml.dump({'variables': mainDB['variables']}, userSyntax)

  # Create list of rules from the sets of user settings which are currently
  # valid
  rulesList = []
  for rule in [r for s in validSets for r in settings.get(s)]:
    # Schema validation guarantees we can trust all the following inputs

    # Read a name or list of names
    cmdNames = rule['name']
    if isinstance(cmdNames, str):
      cmdNames = [cmdNames]

    # Get type with 'function' being default if not provided
    cmdType = rule.get('type', 'function')

    cmdElements = []
    for elem in rule['elements']:
      # Get the sole kv pair, apparently this is most efficient way
      key,value = next( iter(elem.items()) )

      if key in ruleContexts:
        cmdElements.append( (key,value) )
      elif 'options_then_' in key:
        opts = ''.join( value.get('options_taking_arguments', []) )
        if opts:
          cmdElements.append( ('options', 'list-with-args', opts) )
        else:
          cmdElements.append( ('options', 'list') )

        then = key.split('_')[-1]
        if then == 'end':
          # Ignore all further elements
          break
        else:
          # Add the block, etc
          cmdElements.append( (then, value[then]) )

    for cmdName in cmdNames:
      rulesList.append( _make_rule(cmdName, cmdElements, cmdType) )

  # Only keep non-empty rules. Sublime doesn't mind if the list of rules ends up
  # empty
  content = {'contexts': {'main': [r for r in rulesList if r]}}
  yaml.dump(content, userSyntax)


def plugin_loaded():
  settings = sublime.load_settings(settingsName)

  settings.clear_on_change(__name__)
  settings.add_on_change(__name__, _write_user_chainload)

  if settings.get('user_chainload_debugging'):
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.WARNING)

  _write_user_chainload()
