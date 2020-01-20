# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from tinkoff_voicekit_client.speech_utils.apis import stt_pb2 as apis_dot_stt__pb2


class SpeechToTextStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Recognize = channel.unary_unary(
        '/tinkoff.cloud.stt.v1.SpeechToText/Recognize',
        request_serializer=apis_dot_stt__pb2.RecognizeRequest.SerializeToString,
        response_deserializer=apis_dot_stt__pb2.RecognizeResponse.FromString,
        )
    self.StreamingRecognize = channel.stream_stream(
        '/tinkoff.cloud.stt.v1.SpeechToText/StreamingRecognize',
        request_serializer=apis_dot_stt__pb2.StreamingRecognizeRequest.SerializeToString,
        response_deserializer=apis_dot_stt__pb2.StreamingRecognizeResponse.FromString,
        )


class SpeechToTextServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Recognize(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def StreamingRecognize(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_SpeechToTextServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Recognize': grpc.unary_unary_rpc_method_handler(
          servicer.Recognize,
          request_deserializer=apis_dot_stt__pb2.RecognizeRequest.FromString,
          response_serializer=apis_dot_stt__pb2.RecognizeResponse.SerializeToString,
      ),
      'StreamingRecognize': grpc.stream_stream_rpc_method_handler(
          servicer.StreamingRecognize,
          request_deserializer=apis_dot_stt__pb2.StreamingRecognizeRequest.FromString,
          response_serializer=apis_dot_stt__pb2.StreamingRecognizeResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'tinkoff.cloud.stt.v1.SpeechToText', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
