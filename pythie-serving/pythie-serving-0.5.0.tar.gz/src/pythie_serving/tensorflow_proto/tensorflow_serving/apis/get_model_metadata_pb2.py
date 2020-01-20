# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow_serving/apis/get_model_metadata.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from pythie_serving.tensorflow_proto.tensorflow.core.protobuf import meta_graph_pb2 as tensorflow_dot_core_dot_protobuf_dot_meta__graph__pb2
from pythie_serving.tensorflow_proto.tensorflow_serving.apis import model_pb2 as tensorflow__serving_dot_apis_dot_model__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorflow_serving/apis/get_model_metadata.proto',
  package='tensorflow.serving',
  syntax='proto3',
  serialized_options=_b('\370\001\001'),
  serialized_pb=_b('\n0tensorflow_serving/apis/get_model_metadata.proto\x12\x12tensorflow.serving\x1a\x19google/protobuf/any.proto\x1a)tensorflow/core/protobuf/meta_graph.proto\x1a#tensorflow_serving/apis/model.proto\"\xae\x01\n\x0fSignatureDefMap\x12L\n\rsignature_def\x18\x01 \x03(\x0b\x32\x35.tensorflow.serving.SignatureDefMap.SignatureDefEntry\x1aM\n\x11SignatureDefEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\'\n\x05value\x18\x02 \x01(\x0b\x32\x18.tensorflow.SignatureDef:\x02\x38\x01\"d\n\x17GetModelMetadataRequest\x12\x31\n\nmodel_spec\x18\x01 \x01(\x0b\x32\x1d.tensorflow.serving.ModelSpec\x12\x16\n\x0emetadata_field\x18\x02 \x03(\t\"\xe2\x01\n\x18GetModelMetadataResponse\x12\x31\n\nmodel_spec\x18\x01 \x01(\x0b\x32\x1d.tensorflow.serving.ModelSpec\x12L\n\x08metadata\x18\x02 \x03(\x0b\x32:.tensorflow.serving.GetModelMetadataResponse.MetadataEntry\x1a\x45\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12#\n\x05value\x18\x02 \x01(\x0b\x32\x14.google.protobuf.Any:\x02\x38\x01\x42\x03\xf8\x01\x01\x62\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_any__pb2.DESCRIPTOR,tensorflow_dot_core_dot_protobuf_dot_meta__graph__pb2.DESCRIPTOR,tensorflow__serving_dot_apis_dot_model__pb2.DESCRIPTOR,])




_SIGNATUREDEFMAP_SIGNATUREDEFENTRY = _descriptor.Descriptor(
  name='SignatureDefEntry',
  full_name='tensorflow.serving.SignatureDefMap.SignatureDefEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='tensorflow.serving.SignatureDefMap.SignatureDefEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='tensorflow.serving.SignatureDefMap.SignatureDefEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
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
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=277,
  serialized_end=354,
)

_SIGNATUREDEFMAP = _descriptor.Descriptor(
  name='SignatureDefMap',
  full_name='tensorflow.serving.SignatureDefMap',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='signature_def', full_name='tensorflow.serving.SignatureDefMap.signature_def', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_SIGNATUREDEFMAP_SIGNATUREDEFENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=180,
  serialized_end=354,
)


_GETMODELMETADATAREQUEST = _descriptor.Descriptor(
  name='GetModelMetadataRequest',
  full_name='tensorflow.serving.GetModelMetadataRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='model_spec', full_name='tensorflow.serving.GetModelMetadataRequest.model_spec', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='metadata_field', full_name='tensorflow.serving.GetModelMetadataRequest.metadata_field', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=356,
  serialized_end=456,
)


_GETMODELMETADATARESPONSE_METADATAENTRY = _descriptor.Descriptor(
  name='MetadataEntry',
  full_name='tensorflow.serving.GetModelMetadataResponse.MetadataEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='tensorflow.serving.GetModelMetadataResponse.MetadataEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='tensorflow.serving.GetModelMetadataResponse.MetadataEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
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
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=616,
  serialized_end=685,
)

_GETMODELMETADATARESPONSE = _descriptor.Descriptor(
  name='GetModelMetadataResponse',
  full_name='tensorflow.serving.GetModelMetadataResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='model_spec', full_name='tensorflow.serving.GetModelMetadataResponse.model_spec', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='metadata', full_name='tensorflow.serving.GetModelMetadataResponse.metadata', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_GETMODELMETADATARESPONSE_METADATAENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=459,
  serialized_end=685,
)

_SIGNATUREDEFMAP_SIGNATUREDEFENTRY.fields_by_name['value'].message_type = tensorflow_dot_core_dot_protobuf_dot_meta__graph__pb2._SIGNATUREDEF
_SIGNATUREDEFMAP_SIGNATUREDEFENTRY.containing_type = _SIGNATUREDEFMAP
_SIGNATUREDEFMAP.fields_by_name['signature_def'].message_type = _SIGNATUREDEFMAP_SIGNATUREDEFENTRY
_GETMODELMETADATAREQUEST.fields_by_name['model_spec'].message_type = tensorflow__serving_dot_apis_dot_model__pb2._MODELSPEC
_GETMODELMETADATARESPONSE_METADATAENTRY.fields_by_name['value'].message_type = google_dot_protobuf_dot_any__pb2._ANY
_GETMODELMETADATARESPONSE_METADATAENTRY.containing_type = _GETMODELMETADATARESPONSE
_GETMODELMETADATARESPONSE.fields_by_name['model_spec'].message_type = tensorflow__serving_dot_apis_dot_model__pb2._MODELSPEC
_GETMODELMETADATARESPONSE.fields_by_name['metadata'].message_type = _GETMODELMETADATARESPONSE_METADATAENTRY
DESCRIPTOR.message_types_by_name['SignatureDefMap'] = _SIGNATUREDEFMAP
DESCRIPTOR.message_types_by_name['GetModelMetadataRequest'] = _GETMODELMETADATAREQUEST
DESCRIPTOR.message_types_by_name['GetModelMetadataResponse'] = _GETMODELMETADATARESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SignatureDefMap = _reflection.GeneratedProtocolMessageType('SignatureDefMap', (_message.Message,), {

  'SignatureDefEntry' : _reflection.GeneratedProtocolMessageType('SignatureDefEntry', (_message.Message,), {
    'DESCRIPTOR' : _SIGNATUREDEFMAP_SIGNATUREDEFENTRY,
    '__module__' : 'tensorflow_serving.apis.get_model_metadata_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.serving.SignatureDefMap.SignatureDefEntry)
    })
  ,
  'DESCRIPTOR' : _SIGNATUREDEFMAP,
  '__module__' : 'tensorflow_serving.apis.get_model_metadata_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.serving.SignatureDefMap)
  })
_sym_db.RegisterMessage(SignatureDefMap)
_sym_db.RegisterMessage(SignatureDefMap.SignatureDefEntry)

GetModelMetadataRequest = _reflection.GeneratedProtocolMessageType('GetModelMetadataRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETMODELMETADATAREQUEST,
  '__module__' : 'tensorflow_serving.apis.get_model_metadata_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.serving.GetModelMetadataRequest)
  })
_sym_db.RegisterMessage(GetModelMetadataRequest)

GetModelMetadataResponse = _reflection.GeneratedProtocolMessageType('GetModelMetadataResponse', (_message.Message,), {

  'MetadataEntry' : _reflection.GeneratedProtocolMessageType('MetadataEntry', (_message.Message,), {
    'DESCRIPTOR' : _GETMODELMETADATARESPONSE_METADATAENTRY,
    '__module__' : 'tensorflow_serving.apis.get_model_metadata_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.serving.GetModelMetadataResponse.MetadataEntry)
    })
  ,
  'DESCRIPTOR' : _GETMODELMETADATARESPONSE,
  '__module__' : 'tensorflow_serving.apis.get_model_metadata_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.serving.GetModelMetadataResponse)
  })
_sym_db.RegisterMessage(GetModelMetadataResponse)
_sym_db.RegisterMessage(GetModelMetadataResponse.MetadataEntry)


DESCRIPTOR._options = None
_SIGNATUREDEFMAP_SIGNATUREDEFENTRY._options = None
_GETMODELMETADATARESPONSE_METADATAENTRY._options = None
# @@protoc_insertion_point(module_scope)
