# coding: utf-8

"""
    Seeq REST API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 0.44.04
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class FunctionGroupModel(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'children': 'list[SeeAlsoModel]',
        'description': 'str',
        'documentation_href': 'str',
        'examples': 'list[ExampleModel]',
        'function_group_id': 'str',
        'functions': 'list[FunctionModel]',
        'keywords': 'list[str]',
        'parameters': 'list[ParameterModel]',
        'parents': 'list[SeeAlsoModel]',
        'see_alsos': 'list[SeeAlsoModel]',
        'title': 'str'
    }

    attribute_map = {
        'children': 'children',
        'description': 'description',
        'documentation_href': 'documentationHref',
        'examples': 'examples',
        'function_group_id': 'functionGroupId',
        'functions': 'functions',
        'keywords': 'keywords',
        'parameters': 'parameters',
        'parents': 'parents',
        'see_alsos': 'seeAlsos',
        'title': 'title'
    }

    def __init__(self, children=None, description=None, documentation_href=None, examples=None, function_group_id=None, functions=None, keywords=None, parameters=None, parents=None, see_alsos=None, title=None):
        """
        FunctionGroupModel - a model defined in Swagger
        """

        self._children = None
        self._description = None
        self._documentation_href = None
        self._examples = None
        self._function_group_id = None
        self._functions = None
        self._keywords = None
        self._parameters = None
        self._parents = None
        self._see_alsos = None
        self._title = None

        if children is not None:
          self.children = children
        if description is not None:
          self.description = description
        if documentation_href is not None:
          self.documentation_href = documentation_href
        if examples is not None:
          self.examples = examples
        if function_group_id is not None:
          self.function_group_id = function_group_id
        if functions is not None:
          self.functions = functions
        if keywords is not None:
          self.keywords = keywords
        if parameters is not None:
          self.parameters = parameters
        if parents is not None:
          self.parents = parents
        if see_alsos is not None:
          self.see_alsos = see_alsos
        if title is not None:
          self.title = title

    @property
    def children(self):
        """
        Gets the children of this FunctionGroupModel.

        :return: The children of this FunctionGroupModel.
        :rtype: list[SeeAlsoModel]
        """
        return self._children

    @children.setter
    def children(self, children):
        """
        Sets the children of this FunctionGroupModel.

        :param children: The children of this FunctionGroupModel.
        :type: list[SeeAlsoModel]
        """

        self._children = children

    @property
    def description(self):
        """
        Gets the description of this FunctionGroupModel.

        :return: The description of this FunctionGroupModel.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this FunctionGroupModel.

        :param description: The description of this FunctionGroupModel.
        :type: str
        """

        self._description = description

    @property
    def documentation_href(self):
        """
        Gets the documentation_href of this FunctionGroupModel.

        :return: The documentation_href of this FunctionGroupModel.
        :rtype: str
        """
        return self._documentation_href

    @documentation_href.setter
    def documentation_href(self, documentation_href):
        """
        Sets the documentation_href of this FunctionGroupModel.

        :param documentation_href: The documentation_href of this FunctionGroupModel.
        :type: str
        """

        self._documentation_href = documentation_href

    @property
    def examples(self):
        """
        Gets the examples of this FunctionGroupModel.

        :return: The examples of this FunctionGroupModel.
        :rtype: list[ExampleModel]
        """
        return self._examples

    @examples.setter
    def examples(self, examples):
        """
        Sets the examples of this FunctionGroupModel.

        :param examples: The examples of this FunctionGroupModel.
        :type: list[ExampleModel]
        """

        self._examples = examples

    @property
    def function_group_id(self):
        """
        Gets the function_group_id of this FunctionGroupModel.

        :return: The function_group_id of this FunctionGroupModel.
        :rtype: str
        """
        return self._function_group_id

    @function_group_id.setter
    def function_group_id(self, function_group_id):
        """
        Sets the function_group_id of this FunctionGroupModel.

        :param function_group_id: The function_group_id of this FunctionGroupModel.
        :type: str
        """

        self._function_group_id = function_group_id

    @property
    def functions(self):
        """
        Gets the functions of this FunctionGroupModel.

        :return: The functions of this FunctionGroupModel.
        :rtype: list[FunctionModel]
        """
        return self._functions

    @functions.setter
    def functions(self, functions):
        """
        Sets the functions of this FunctionGroupModel.

        :param functions: The functions of this FunctionGroupModel.
        :type: list[FunctionModel]
        """

        self._functions = functions

    @property
    def keywords(self):
        """
        Gets the keywords of this FunctionGroupModel.

        :return: The keywords of this FunctionGroupModel.
        :rtype: list[str]
        """
        return self._keywords

    @keywords.setter
    def keywords(self, keywords):
        """
        Sets the keywords of this FunctionGroupModel.

        :param keywords: The keywords of this FunctionGroupModel.
        :type: list[str]
        """

        self._keywords = keywords

    @property
    def parameters(self):
        """
        Gets the parameters of this FunctionGroupModel.

        :return: The parameters of this FunctionGroupModel.
        :rtype: list[ParameterModel]
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """
        Sets the parameters of this FunctionGroupModel.

        :param parameters: The parameters of this FunctionGroupModel.
        :type: list[ParameterModel]
        """

        self._parameters = parameters

    @property
    def parents(self):
        """
        Gets the parents of this FunctionGroupModel.

        :return: The parents of this FunctionGroupModel.
        :rtype: list[SeeAlsoModel]
        """
        return self._parents

    @parents.setter
    def parents(self, parents):
        """
        Sets the parents of this FunctionGroupModel.

        :param parents: The parents of this FunctionGroupModel.
        :type: list[SeeAlsoModel]
        """

        self._parents = parents

    @property
    def see_alsos(self):
        """
        Gets the see_alsos of this FunctionGroupModel.

        :return: The see_alsos of this FunctionGroupModel.
        :rtype: list[SeeAlsoModel]
        """
        return self._see_alsos

    @see_alsos.setter
    def see_alsos(self, see_alsos):
        """
        Sets the see_alsos of this FunctionGroupModel.

        :param see_alsos: The see_alsos of this FunctionGroupModel.
        :type: list[SeeAlsoModel]
        """

        self._see_alsos = see_alsos

    @property
    def title(self):
        """
        Gets the title of this FunctionGroupModel.

        :return: The title of this FunctionGroupModel.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """
        Sets the title of this FunctionGroupModel.

        :param title: The title of this FunctionGroupModel.
        :type: str
        """

        self._title = title

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, FunctionGroupModel):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
