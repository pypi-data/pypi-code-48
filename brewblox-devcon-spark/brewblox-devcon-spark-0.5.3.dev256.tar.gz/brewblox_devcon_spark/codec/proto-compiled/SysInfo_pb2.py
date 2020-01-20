# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: SysInfo.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import brewblox_pb2 as brewblox__pb2
import nanopb_pb2 as nanopb__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='SysInfo.proto',
  package='blox',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\rSysInfo.proto\x12\x04\x62lox\x1a\x0e\x62rewblox.proto\x1a\x0cnanopb.proto\"\xb6\x02\n\x07SysInfo\x12(\n\x08\x64\x65viceId\x18\x01 \x01(\x0c\x42\x16\x8a\xb5\x18\x02(\x01\x92?\x02\x08\x0c\x92?\x02x\x01\x8a\xb5\x18\x02\x38\x01\x12\x1c\n\x07version\x18\x02 \x01(\tB\x0b\x8a\xb5\x18\x02(\x01\x92?\x02\x08\x0c\x12\x30\n\x08platform\x18\x03 \x01(\x0e\x32\x16.blox.SysInfo.PlatformB\x06\x8a\xb5\x18\x02(\x01\x12$\n\x0fprotocolVersion\x18\x07 \x01(\tB\x0b\x8a\xb5\x18\x02(\x01\x92?\x02\x08\x0c\x12 \n\x0breleaseDate\x18\x08 \x01(\tB\x0b\x8a\xb5\x18\x02(\x01\x92?\x02\x08\x0c\x12!\n\x0cprotocolDate\x18\t \x01(\tB\x0b\x8a\xb5\x18\x02(\x01\x92?\x02\x08\x0c\"=\n\x08Platform\x12\x14\n\x10unknown_platform\x10\x00\x12\x07\n\x03gcc\x10\x03\x12\n\n\x06photon\x10\x06\x12\x06\n\x02p1\x10\x08:\x07\x8a\xb5\x18\x03\x18\x80\x02\x62\x06proto3')
  ,
  dependencies=[brewblox__pb2.DESCRIPTOR,nanopb__pb2.DESCRIPTOR,])



_SYSINFO_PLATFORM = _descriptor.EnumDescriptor(
  name='Platform',
  full_name='blox.SysInfo.Platform',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='unknown_platform', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='gcc', index=1, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='photon', index=2, number=6,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='p1', index=3, number=8,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=294,
  serialized_end=355,
)
_sym_db.RegisterEnumDescriptor(_SYSINFO_PLATFORM)


_SYSINFO = _descriptor.Descriptor(
  name='SysInfo',
  full_name='blox.SysInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='deviceId', full_name='blox.SysInfo.deviceId', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212\265\030\002(\001\222?\002\010\014\222?\002x\001\212\265\030\0028\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='version', full_name='blox.SysInfo.version', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212\265\030\002(\001\222?\002\010\014'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='platform', full_name='blox.SysInfo.platform', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212\265\030\002(\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='protocolVersion', full_name='blox.SysInfo.protocolVersion', index=3,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212\265\030\002(\001\222?\002\010\014'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='releaseDate', full_name='blox.SysInfo.releaseDate', index=4,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212\265\030\002(\001\222?\002\010\014'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='protocolDate', full_name='blox.SysInfo.protocolDate', index=5,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\212\265\030\002(\001\222?\002\010\014'), file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SYSINFO_PLATFORM,
  ],
  serialized_options=_b('\212\265\030\003\030\200\002'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=54,
  serialized_end=364,
)

_SYSINFO.fields_by_name['platform'].enum_type = _SYSINFO_PLATFORM
_SYSINFO_PLATFORM.containing_type = _SYSINFO
DESCRIPTOR.message_types_by_name['SysInfo'] = _SYSINFO
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SysInfo = _reflection.GeneratedProtocolMessageType('SysInfo', (_message.Message,), dict(
  DESCRIPTOR = _SYSINFO,
  __module__ = 'SysInfo_pb2'
  # @@protoc_insertion_point(class_scope:blox.SysInfo)
  ))
_sym_db.RegisterMessage(SysInfo)


_SYSINFO.fields_by_name['deviceId']._options = None
_SYSINFO.fields_by_name['version']._options = None
_SYSINFO.fields_by_name['platform']._options = None
_SYSINFO.fields_by_name['protocolVersion']._options = None
_SYSINFO.fields_by_name['releaseDate']._options = None
_SYSINFO.fields_by_name['protocolDate']._options = None
_SYSINFO._options = None
# @@protoc_insertion_point(module_scope)
