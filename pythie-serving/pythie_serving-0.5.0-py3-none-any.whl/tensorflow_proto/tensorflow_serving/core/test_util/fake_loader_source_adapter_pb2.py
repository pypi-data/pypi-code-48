# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow_serving/core/test_util/fake_loader_source_adapter.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorflow_serving/core/test_util/fake_loader_source_adapter.proto',
  package='tensorflow.serving.test_util',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\nBtensorflow_serving/core/test_util/fake_loader_source_adapter.proto\x12\x1ctensorflow.serving.test_util\"/\n\x1d\x46\x61keLoaderSourceAdapterConfig\x12\x0e\n\x06suffix\x18\x01 \x01(\tb\x06proto3')
)




_FAKELOADERSOURCEADAPTERCONFIG = _descriptor.Descriptor(
  name='FakeLoaderSourceAdapterConfig',
  full_name='tensorflow.serving.test_util.FakeLoaderSourceAdapterConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='suffix', full_name='tensorflow.serving.test_util.FakeLoaderSourceAdapterConfig.suffix', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=100,
  serialized_end=147,
)

DESCRIPTOR.message_types_by_name['FakeLoaderSourceAdapterConfig'] = _FAKELOADERSOURCEADAPTERCONFIG
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FakeLoaderSourceAdapterConfig = _reflection.GeneratedProtocolMessageType('FakeLoaderSourceAdapterConfig', (_message.Message,), {
  'DESCRIPTOR' : _FAKELOADERSOURCEADAPTERCONFIG,
  '__module__' : 'tensorflow_serving.core.test_util.fake_loader_source_adapter_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.serving.test_util.FakeLoaderSourceAdapterConfig)
  })
_sym_db.RegisterMessage(FakeLoaderSourceAdapterConfig)


# @@protoc_insertion_point(module_scope)
