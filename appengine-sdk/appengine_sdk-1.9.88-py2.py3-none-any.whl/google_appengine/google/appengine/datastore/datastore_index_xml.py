#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Directly processes text of datastore-indexes.xml.

IndexesXmlParser is called with an XML string to produce an IndexXml object
containing the data from the XML.

IndexesXmlParser: converts XML to Index object.
Index: describes a single index specified in datastore-indexes.xml
"""







from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from xml.etree import ElementTree

from google.appengine.api.validation import ValidationError
from google.appengine.datastore.datastore_index import Index
from google.appengine.datastore.datastore_index import IndexDefinitions
from google.appengine.datastore.datastore_index import Property

MISSING_KIND = '<datastore-index> node has missing attribute "kind".'
BAD_DIRECTION = ('<property> tag attribute "direction" must have value "asc"'
                 ' or "desc", given "%s"')
BAD_MODE = ('<property> tag attribute "mode" must have value "geospatial",'
            ' given "%s"')
NAME_MISSING = ('<datastore-index> node with kind "%s" needs to have a name'
                ' attribute specified for its <property> node')
MODE_AND_DIRECTION_SPECIFIED = ('<datastore-index> node has both direction '
                                'and mode specfied')
MODE_AND_ANCESTOR_SPECIFIED = ('<property> tag attribute "mode" cannot be '
                               'specifed with "ancestor"')


def IndexesXmlToIndexDefinitions(xml_str):
  """Convert a <datastore-indexes> XML string into an IndexDefinitions objects.

  Args:
    xml_str: a string containing a complete XML document where the root node is
      <datastore-indexes>.

  Returns:
    an IndexDefinitions object parsed out of the XML string.

  Raises:
    ValidationError: in case of malformed XML or illegal inputs.
  """
  parser = IndexesXmlParser()
  return parser.Parse(xml_str)


def IsAutoGenerated(xml_str):
  """Test if the given datastore-indexes.xml string implies auto-generation."""
  try:
    xml_root = ElementTree.fromstring(xml_str)
    return (xml_root.tag == 'datastore-indexes' and
            _BooleanAttribute(xml_root.attrib.get('autoGenerate', 'false')))
  except ElementTree.ParseError:
    return False


class IndexesXmlParser(object):
  """Provides logic for walking down XML tree and pulling data."""

  def Parse(self, xml_str):
    """Parses XML string and returns object representation of relevant info.

    Args:
      xml_str: The XML string.
    Returns:
      An IndexDefinitions object containing the result of parsing the XML.
    Raises:
      ValidationError: In case of malformed XML or illegal inputs.
    """

    try:
      self.indexes = []
      self.errors = []
      xml_root = ElementTree.fromstring(xml_str)
      if xml_root.tag != 'datastore-indexes':
        raise ValidationError('Root tag must be <datastore-indexes>')

      for child in xml_root.getchildren():
        self.ProcessIndexNode(child)

      if self.errors:
        raise ValidationError('\n'.join(self.errors))

      return IndexDefinitions(indexes=self.indexes)
    except ElementTree.ParseError as e:
      raise ValidationError('Bad input -- not valid XML: %s' % e)

  def ProcessIndexNode(self, node):
    """Processes XML <datastore-index> nodes into Index objects.

    The following information is parsed out:
    kind: specifies the kind of entities to index.
    ancestor: true if the index supports queries that filter by
      ancestor-key to constraint results to a single entity group.
    property: represents the entity properties to index, with a name
      and direction attribute.

    Args:
      node: <datastore-index> XML node in datastore-indexes.xml.
    """
    if node.tag != 'datastore-index':
      self.errors.append('Unrecognized node: <%s>' % node.tag)
      return

    index = Index()
    index.kind = node.attrib.get('kind')
    if not index.kind:
      self.errors.append(MISSING_KIND)
    ancestor = node.attrib.get('ancestor', 'false')
    index.ancestor = _BooleanAttribute(ancestor)
    if index.ancestor is None:
      self.errors.append(
          'Value for ancestor should be true or false, not "%s"' % ancestor)
    properties = []
    property_nodes = [n for n in node.getchildren() if n.tag == 'property']


    has_geospatial = any(
        property_node.attrib.get('mode') == 'geospatial'
        for property_node in property_nodes)

    for property_node in property_nodes:
      name = property_node.attrib.get('name', '')
      if not name:
        self.errors.append(NAME_MISSING % index.kind)
        continue

      direction = property_node.attrib.get('direction')
      mode = property_node.attrib.get('mode')
      if mode:
        if index.ancestor:
          self.errors.append(MODE_AND_ANCESTOR_SPECIFIED)
          continue
        if mode != 'geospatial':
          self.errors.append(BAD_MODE % mode)
          continue
        if direction:
          self.errors.append(MODE_AND_DIRECTION_SPECIFIED)
          continue
      else:
        if not direction:


          if not has_geospatial:
            direction = 'asc'
        elif direction not in ('asc', 'desc'):
          self.errors.append(BAD_DIRECTION % direction)
          continue
      properties.append(Property(name=name, direction=direction, mode=mode))
    index.properties = properties
    self.indexes.append(index)


def _BooleanAttribute(value):
  """Parse the given attribute value as a Boolean value.

  This follows the specification here:
  http://www.w3.org/TR/2012/REC-xmlschema11-2-20120405/datatypes.html#boolean

  Args:
    value: the value to parse.

  Returns:
    True if the value parses as true, False if it parses as false, None if it
    parses as neither.
  """
  if value in ['true', '1']:
    return True
  elif value in ['false', '0']:
    return False
  else:
    return None
