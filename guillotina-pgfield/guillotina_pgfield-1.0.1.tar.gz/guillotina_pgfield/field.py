from guillotina import configure
from guillotina import schema
from guillotina.component import get_adapter
from guillotina.interfaces import IJSONToValue
from zope.interface import Interface, Attribute
from zope.interface import implementer
from guillotina.schema.interfaces import IField
from guillotina.fields.interfaces import IPatchFieldOperation
from guillotina.interfaces import ISchemaFieldSerializeToJson
from guillotina.json.serialize_schema_field import DefaultSchemaFieldSerializer
from guillotina.fields import patch
from guillotina.component import get_utility
from guillotina_pgfield.interfaces import IPGFieldUtility
import logging
import sqlalchemy as sa
import jsonschema
from datetime import datetime
from guillotina.utils import get_current_request
from guillotina.json.deserialize_value import datetime_converter

logger = logging.getLogger(__name__)


class IPGListValue(Interface):

    json_schema = Attribute("JSON schema of data")
    json_serializer = Attribute("JSON serializer")
    json_deserializer = Attribute("JSON deserializer")
    pg_schema = Attribute("PG mini schema")
    pg_table = Attribute("PG table name")


class IPGListField(IField):
    """PG Field."""


@implementer(IPGListValue)
class PGList:
    def __init__(self, json_schema, pg_schema, pg_table, zoid):
        # need to check for table on pg_list db
        self.json_schema = json_schema
        self.pg_schema = pg_schema
        self.pg_table = pg_table
        self.zoid = zoid

    def get_table(self, utility):
        return utility.get_table(self.pg_table, self.pg_schema)

    async def append(self, request, utility, value):
        values_to_serialize = {}
        for column in self.pg_schema:
            if column.name in value:
                values_to_serialize[column.name] = value[column.name]
        table = self.get_table(utility)
        statement = table.insert().values(zoid=self.zoid, ts=datetime.utcnow(), **values_to_serialize)
        await utility.add_statement(request, statement)

    async def extend(self, request, utility, value):
        table = self.get_table(utility)
        for real_value in value:
            values_to_serialize = {}
            for column in self.pg_schema:
                if column.name in real_value:
                    values_to_serialize[column.name] = real_value[column.name]
            statement = table.insert().values(zoid=self.zoid, ts=datetime.utcnow(), **values_to_serialize)
            await utility.add_statement(request, statement)

    async def remove(self, request, utility, item_index):
        table = self.get_table(utility)
        statement = sa.select([table.c.ts]).where(table.c.zoid == self.zoid)
        result = await utility.query(statement)
        if item_index < len(result):
            statement = table.delete().where(table.c.zoid == self.zoid).where(table.c.ts == result[item_index][0])
            await utility.add_statement(request, statement)

    async def length(self, utility):
        utility = get_utility(IPGFieldUtility)
        table = self.get_table(utility)
        statement = sa.select([sa.func.count(sa.text("*"))]).where(table.c.zoid == self.zoid)
        result = await utility.query(statement)
        return result[0][0]


class PGListPatchValue:
    def __init__(self, json_value, real_object, operation):
        self.json_value = json_value
        self.real_object = real_object
        self.operation = operation


@configure.adapter(for_=IPGListField, provides=IPatchFieldOperation, name="append")
class PatchPGListAppend(patch.PatchListAppend):
    def get_existing_value(self, field_context):
        existing = getattr(field_context, self.field.__name__, None)
        if existing is None:
            existing = PGList(
                json_schema=self.field._json_schema,
                pg_schema=self.field._pg_schema,
                pg_table=self.field._pg_table,
                zoid=field_context.__uuid__,
            )
            setattr(field_context, self.field.__name__, existing)
            field_context.register()

        return existing

    async def __call__(self, context, value):
        existing = self.get_existing_value(context)

        value = get_adapter(self.field, IJSONToValue, args=[value, context])

        request = get_current_request()
        utility = get_utility(IPGFieldUtility)
        operation = await existing.append(request, utility, value)
        return PGListPatchValue(value, existing, operation)

    async def set(self, value):
        await value.operation


@configure.adapter(for_=IPGListField, provides=IPatchFieldOperation, name="extend")
class PatchPGListExtend(PatchPGListAppend):
    async def __call__(self, context, value):
        existing = self.get_existing_value(context)

        value = get_adapter(self.field, IJSONToValue, args=[value, context])

        request = get_current_request()
        utility = get_utility(IPGFieldUtility)
        operation = await existing.extend(request, utility, value)
        return PGListPatchValue(value, existing, operation)


@configure.adapter(for_=IPGListField, provides=IPatchFieldOperation, name="del")
class PatchPGListDel(PatchPGListAppend):
    async def __call__(self, context, value):
        existing = self.get_existing_value(context)

        value = get_adapter(self.field, IJSONToValue, args=[value, context])

        request = get_current_request()
        utility = get_utility(IPGFieldUtility)
        operation = await existing.remove(request, utility, int(value))
        return PGListPatchValue(value, existing, operation)


@configure.value_serializer(IPGListValue)
async def pg_list_converter(value):
    utility = get_utility(IPGFieldUtility)
    return {"total": await value.length(utility)}


@configure.value_deserializer(IPGListField)
def pg_list_deserializer(field, value, context):
    for key, values in field._json_schema["properties"].items():
        if isinstance(value, dict) and key in value:
            if values["type"] == "datetime":
                value[key] = datetime_converter(field, value[key], context)
    return value


@configure.adapter(for_=(IPGListField, Interface, Interface), provides=ISchemaFieldSerializeToJson)
class DefaultFileSchemaFieldSerializer(DefaultSchemaFieldSerializer):
    @property
    def field_type(self):
        return "array"


@implementer(IPGListField)
class PGListField(schema.Field):
    def __init__(self, *args, json_schema=None, validator=None, pg_schema=None, pg_table=None, **kwargs):
        self._json_schema = json_schema
        self._validator = validator
        self._pg_schema = pg_schema
        self._pg_table = pg_table
        super().__init__(*args, **kwargs)

    def validate(self, value):
        if isinstance(value, list):
            for v in value.json_value:
                jsonschema.validate(v, self._json_schema)
        elif isinstance(value, dict):
            jsonschema.validate(value.json_value, self._json_schema)

    async def set(self, obj, value):
        if self._validator:
            await self._validator(obj, value)
        utility = get_utility(IPGFieldUtility)
        if not await utility.exist(self._pg_table):
            await utility.create(self._pg_table, self._pg_schema)

        if value.operation is None:
            return
        await value.operation
