import abc
import pydoc

import six
import terminaltables
from halo import halo

from gradient.logger import Logger
from gradient.utils import get_terminal_lines


@six.add_metaclass(abc.ABCMeta)
class BaseCommand:
    def __init__(self, api_key, logger=Logger()):
        self.api_key = api_key
        self.client = self._get_client(api_key, logger)
        self.logger = logger

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def _get_client(self, api_key, logger):
        pass


@six.add_metaclass(abc.ABCMeta)
class ListCommandMixin(object):
    WAITING_FOR_RESPONSE_MESSAGE = "Waiting for data..."
    TOTAL_ITEMS_KEY = "total"

    def execute(self, **kwargs):
        with halo.Halo(text=self.WAITING_FOR_RESPONSE_MESSAGE, spinner="dots"):
            instances = self._get_instances(kwargs)

        self._log_objects_list(instances)

    @abc.abstractmethod
    def _get_instances(self, kwargs):
        pass

    @abc.abstractmethod
    def _get_table_data(self, objects):
        pass

    def _log_objects_list(self, objects):
        if not objects:
            self.logger.warning("No data found")
            return

        table_data = self._get_table_data(objects)
        table_str = self._make_list_table(table_data)
        if len(table_str.splitlines()) > get_terminal_lines():
            pydoc.pager(table_str)
        else:
            self.logger.log(table_str)

    @staticmethod
    def _make_list_table(table_data):
        ascii_table = terminaltables.AsciiTable(table_data)
        table_string = ascii_table.table
        return table_string

    def _generate_data_table(self, **kwargs):
        limit = kwargs.get("limit")
        offset = kwargs.get("offset")
        meta_data = dict()
        while self.TOTAL_ITEMS_KEY not in meta_data or offset < meta_data.get(self.TOTAL_ITEMS_KEY):
            with halo.Halo(text=self.WAITING_FOR_RESPONSE_MESSAGE, spinner="dots"):
                kwargs["offset"] = offset
                instances, meta_data = self._get_instances(
                    **kwargs
                )
            next_iteration = False
            if instances:
                table_data = self._get_table_data(instances)
                table_str = self._make_list_table(table_data) + "\n"
                if offset + limit < meta_data.get(self.TOTAL_ITEMS_KEY):
                    next_iteration = True
            else:
                table_str = "No data found"

            yield table_str, next_iteration
            offset += limit


@six.add_metaclass(abc.ABCMeta)
class DetailsCommandMixin(object):
    WAITING_FOR_RESPONSE_MESSAGE = "Waiting for data..."

    def execute(self, id_):
        with halo.Halo(text=self.WAITING_FOR_RESPONSE_MESSAGE, spinner="dots"):
            instance = self._get_instance(id_)

        self._log_object(instance)

    def _get_instance(self, id_):
        instance = self.client.get(id_)

        return instance

    def _log_object(self, instance):

        table_str = self._make_table(instance)
        if len(table_str.splitlines()) > get_terminal_lines():
            pydoc.pager(table_str)
        else:
            self.logger.log(table_str)

    def _make_table(self, instance):
        data = self._get_table_data(instance)
        ascii_table = terminaltables.AsciiTable(data)
        table_string = ascii_table.table
        return table_string

    @abc.abstractmethod
    def _get_table_data(self, instance):
        pass
