# coding: utf-8

"""
    Flywheel

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 11.0.0-dev.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


## NOTE: This file is auto generated by the swagger code generator program.
## Do not edit the file manually.

import pprint
import re  # noqa: F401

import six

from flywheel.models.job_inputs_array_item import JobInputsArrayItem  # noqa: F401,E501
from flywheel.models.rule_any import RuleAny  # noqa: F401,E501

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.


class Rule(object):

    swagger_types = {
        'project_id': 'str',
        'gear_id': 'str',
        'name': 'str',
        'config': 'object',
        'fixed_inputs': 'list[JobInputsArrayItem]',
        'auto_update': 'bool',
        'any': 'list[RuleAny]',
        'all': 'list[RuleAny]',
        '_not': 'list[RuleAny]',
        'disabled': 'bool',
        'compute_provider_id': 'str',
        'id': 'str'
    }

    attribute_map = {
        'project_id': 'project_id',
        'gear_id': 'gear_id',
        'name': 'name',
        'config': 'config',
        'fixed_inputs': 'fixed_inputs',
        'auto_update': 'auto_update',
        'any': 'any',
        'all': 'all',
        '_not': 'not',
        'disabled': 'disabled',
        'compute_provider_id': 'compute_provider_id',
        'id': '_id'
    }

    rattribute_map = {
        'project_id': 'project_id',
        'gear_id': 'gear_id',
        'name': 'name',
        'config': 'config',
        'fixed_inputs': 'fixed_inputs',
        'auto_update': 'auto_update',
        'any': 'any',
        'all': 'all',
        'not': '_not',
        'disabled': 'disabled',
        'compute_provider_id': 'compute_provider_id',
        '_id': 'id'
    }

    def __init__(self, project_id=None, gear_id=None, name=None, config=None, fixed_inputs=None, auto_update=None, any=None, all=None, _not=None, disabled=None, compute_provider_id=None, id=None):  # noqa: E501
        """Rule - a model defined in Swagger"""
        super(Rule, self).__init__()

        self._project_id = None
        self._gear_id = None
        self._name = None
        self._config = None
        self._fixed_inputs = None
        self._auto_update = None
        self._any = None
        self._all = None
        self.__not = None
        self._disabled = None
        self._compute_provider_id = None
        self._id = None
        self.discriminator = None
        self.alt_discriminator = None

        if project_id is not None:
            self.project_id = project_id
        if gear_id is not None:
            self.gear_id = gear_id
        if name is not None:
            self.name = name
        if config is not None:
            self.config = config
        if fixed_inputs is not None:
            self.fixed_inputs = fixed_inputs
        if auto_update is not None:
            self.auto_update = auto_update
        if any is not None:
            self.any = any
        if all is not None:
            self.all = all
        if _not is not None:
            self._not = _not
        if disabled is not None:
            self.disabled = disabled
        if compute_provider_id is not None:
            self.compute_provider_id = compute_provider_id
        if id is not None:
            self.id = id

    @property
    def project_id(self):
        """Gets the project_id of this Rule.


        :return: The project_id of this Rule.
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this Rule.


        :param project_id: The project_id of this Rule.  # noqa: E501
        :type: str
        """

        self._project_id = project_id

    @property
    def gear_id(self):
        """Gets the gear_id of this Rule.


        :return: The gear_id of this Rule.
        :rtype: str
        """
        return self._gear_id

    @gear_id.setter
    def gear_id(self, gear_id):
        """Sets the gear_id of this Rule.


        :param gear_id: The gear_id of this Rule.  # noqa: E501
        :type: str
        """

        self._gear_id = gear_id

    @property
    def name(self):
        """Gets the name of this Rule.


        :return: The name of this Rule.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Rule.


        :param name: The name of this Rule.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def config(self):
        """Gets the config of this Rule.


        :return: The config of this Rule.
        :rtype: object
        """
        return self._config

    @config.setter
    def config(self, config):
        """Sets the config of this Rule.


        :param config: The config of this Rule.  # noqa: E501
        :type: object
        """

        self._config = config

    @property
    def fixed_inputs(self):
        """Gets the fixed_inputs of this Rule.


        :return: The fixed_inputs of this Rule.
        :rtype: list[JobInputsArrayItem]
        """
        return self._fixed_inputs

    @fixed_inputs.setter
    def fixed_inputs(self, fixed_inputs):
        """Sets the fixed_inputs of this Rule.


        :param fixed_inputs: The fixed_inputs of this Rule.  # noqa: E501
        :type: list[JobInputsArrayItem]
        """

        self._fixed_inputs = fixed_inputs

    @property
    def auto_update(self):
        """Gets the auto_update of this Rule.


        :return: The auto_update of this Rule.
        :rtype: bool
        """
        return self._auto_update

    @auto_update.setter
    def auto_update(self, auto_update):
        """Sets the auto_update of this Rule.


        :param auto_update: The auto_update of this Rule.  # noqa: E501
        :type: bool
        """

        self._auto_update = auto_update

    @property
    def any(self):
        """Gets the any of this Rule.


        :return: The any of this Rule.
        :rtype: list[RuleAny]
        """
        return self._any

    @any.setter
    def any(self, any):
        """Sets the any of this Rule.


        :param any: The any of this Rule.  # noqa: E501
        :type: list[RuleAny]
        """

        self._any = any

    @property
    def all(self):
        """Gets the all of this Rule.


        :return: The all of this Rule.
        :rtype: list[RuleAny]
        """
        return self._all

    @all.setter
    def all(self, all):
        """Sets the all of this Rule.


        :param all: The all of this Rule.  # noqa: E501
        :type: list[RuleAny]
        """

        self._all = all

    @property
    def _not(self):
        """Gets the _not of this Rule.


        :return: The _not of this Rule.
        :rtype: list[RuleAny]
        """
        return self.__not

    @_not.setter
    def _not(self, _not):
        """Sets the _not of this Rule.


        :param _not: The _not of this Rule.  # noqa: E501
        :type: list[RuleAny]
        """

        self.__not = _not

    @property
    def disabled(self):
        """Gets the disabled of this Rule.


        :return: The disabled of this Rule.
        :rtype: bool
        """
        return self._disabled

    @disabled.setter
    def disabled(self, disabled):
        """Sets the disabled of this Rule.


        :param disabled: The disabled of this Rule.  # noqa: E501
        :type: bool
        """

        self._disabled = disabled

    @property
    def compute_provider_id(self):
        """Gets the compute_provider_id of this Rule.

        Unique database ID

        :return: The compute_provider_id of this Rule.
        :rtype: str
        """
        return self._compute_provider_id

    @compute_provider_id.setter
    def compute_provider_id(self, compute_provider_id):
        """Sets the compute_provider_id of this Rule.

        Unique database ID

        :param compute_provider_id: The compute_provider_id of this Rule.  # noqa: E501
        :type: str
        """

        self._compute_provider_id = compute_provider_id

    @property
    def id(self):
        """Gets the id of this Rule.


        :return: The id of this Rule.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Rule.


        :param id: The id of this Rule.  # noqa: E501
        :type: str
        """

        self._id = id


    @staticmethod
    def positional_to_model(value):
        """Converts a positional argument to a model value"""
        return value

    def return_value(self):
        """Unwraps return value from model"""
        return self

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Rule):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    # Container emulation
    def __getitem__(self, key):
        """Returns the value of key"""
        key = self._map_key(key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        """Sets the value of key"""
        key = self._map_key(key)
        setattr(self, key, value)

    def __contains__(self, key):
        """Checks if the given value is a key in this object"""
        key = self._map_key(key, raise_on_error=False)
        return key is not None

    def keys(self):
        """Returns the list of json properties in the object"""
        return self.__class__.rattribute_map.keys()

    def values(self):
        """Returns the list of values in the object"""
        for key in self.__class__.attribute_map.keys():
            yield getattr(self, key)

    def items(self):
        """Returns the list of json property to value mapping"""
        for key, prop in self.__class__.rattribute_map.items():
            yield key, getattr(self, prop)

    def get(self, key, default=None):
        """Get the value of the provided json property, or default"""
        key = self._map_key(key, raise_on_error=False)
        if key:
            return getattr(self, key, default)
        return default

    def _map_key(self, key, raise_on_error=True):
        result = self.__class__.rattribute_map.get(key)
        if result is None:
            if raise_on_error:
                raise AttributeError('Invalid attribute name: {}'.format(key))
            return None
        return '_' + result
