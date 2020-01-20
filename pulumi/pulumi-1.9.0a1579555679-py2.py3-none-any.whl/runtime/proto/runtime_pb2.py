# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: runtime.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import plugin_pb2 as plugin__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='runtime.proto',
  package='pulumirpc',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\rruntime.proto\x12\tpulumirpc\x1a\x0cplugin.proto\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1cgoogle/protobuf/struct.proto\"\x95\x01\n\x10\x43onstructRequest\x12\x13\n\x0blibraryPath\x18\x01 \x01(\t\x12\x10\n\x08resource\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12%\n\x04\x61rgs\x18\x04 \x01(\x0b\x32\x17.google.protobuf.Struct\x12%\n\x04opts\x18\x05 \x01(\x0b\x32\x17.google.protobuf.Struct\":\n\x11\x43onstructResponse\x12%\n\x04outs\x18\x01 \x01(\x0b\x32\x17.google.protobuf.Struct2S\n\x07Runtime\x12H\n\tConstruct\x12\x1b.pulumirpc.ConstructRequest\x1a\x1c.pulumirpc.ConstructResponse\"\x00\x62\x06proto3')
  ,
  dependencies=[plugin__pb2.DESCRIPTOR,google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,google_dot_protobuf_dot_struct__pb2.DESCRIPTOR,])




_CONSTRUCTREQUEST = _descriptor.Descriptor(
  name='ConstructRequest',
  full_name='pulumirpc.ConstructRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='libraryPath', full_name='pulumirpc.ConstructRequest.libraryPath', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='resource', full_name='pulumirpc.ConstructRequest.resource', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='name', full_name='pulumirpc.ConstructRequest.name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='args', full_name='pulumirpc.ConstructRequest.args', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='opts', full_name='pulumirpc.ConstructRequest.opts', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=102,
  serialized_end=251,
)


_CONSTRUCTRESPONSE = _descriptor.Descriptor(
  name='ConstructResponse',
  full_name='pulumirpc.ConstructResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='outs', full_name='pulumirpc.ConstructResponse.outs', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=253,
  serialized_end=311,
)

_CONSTRUCTREQUEST.fields_by_name['args'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_CONSTRUCTREQUEST.fields_by_name['opts'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_CONSTRUCTRESPONSE.fields_by_name['outs'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
DESCRIPTOR.message_types_by_name['ConstructRequest'] = _CONSTRUCTREQUEST
DESCRIPTOR.message_types_by_name['ConstructResponse'] = _CONSTRUCTRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ConstructRequest = _reflection.GeneratedProtocolMessageType('ConstructRequest', (_message.Message,), {
  'DESCRIPTOR' : _CONSTRUCTREQUEST,
  '__module__' : 'runtime_pb2'
  # @@protoc_insertion_point(class_scope:pulumirpc.ConstructRequest)
  })
_sym_db.RegisterMessage(ConstructRequest)

ConstructResponse = _reflection.GeneratedProtocolMessageType('ConstructResponse', (_message.Message,), {
  'DESCRIPTOR' : _CONSTRUCTRESPONSE,
  '__module__' : 'runtime_pb2'
  # @@protoc_insertion_point(class_scope:pulumirpc.ConstructResponse)
  })
_sym_db.RegisterMessage(ConstructResponse)



_RUNTIME = _descriptor.ServiceDescriptor(
  name='Runtime',
  full_name='pulumirpc.Runtime',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=313,
  serialized_end=396,
  methods=[
  _descriptor.MethodDescriptor(
    name='Construct',
    full_name='pulumirpc.Runtime.Construct',
    index=0,
    containing_service=None,
    input_type=_CONSTRUCTREQUEST,
    output_type=_CONSTRUCTRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_RUNTIME)

DESCRIPTOR.services_by_name['Runtime'] = _RUNTIME

# @@protoc_insertion_point(module_scope)
