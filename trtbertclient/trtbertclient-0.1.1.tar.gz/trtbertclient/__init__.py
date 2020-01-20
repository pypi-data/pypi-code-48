from trtbertclient.tokenizer import tokenization
from trtbertclient.tokenizer.extract_features import convert_examples_to_features_sentence
from trtbertclient.api import *


class RequestHandler(object):

    def __init__(self, url, port, proto_string, model_name, model_version, max_seq_length, max_batch_size):
        self.tokenizer = tokenization.FullTokenizer(do_lower_case=True)
        self.url = "%s:%d" % (url, port)
        # self.port = port
        self.protocol = ProtocolType.from_str(proto_string)
        self.model_name = model_name
        self.model_version = model_version
        self.max_seq_length = max_seq_length
        self.infer_handler = InferContext(self.url, self.protocol, self.model_name, self.model_version)
        self.max_batch_size = max_batch_size

    def server_status(self):

        health_ctx = ServerHealthContext(self.url, self.protocol)
        print("Health for model {}".format(self.model_name))
        print("Live: {}".format(health_ctx.is_live()))
        print("Ready: {}".format(health_ctx.is_ready()))

        status_ctx = ServerStatusContext(self.url, self.protocol, self.model_name)
        print(status_ctx.get_server_status())

    def single_embedding(self, text):
        feature = convert_examples_to_features_sentence(text, self.tokenizer, self.max_seq_length)
        result = self.infer_handler.run(inputs={'input_ids': [feature['input_ids']],
                                                'segment_ids': [feature['segment_ids']],
                                                'input_mask': [feature['input_mask']]},
                                        outputs={'avgpooling': InferContext.ResultFormat.RAW},
                                        batch_size=1)
        try:
            vec = result['avgpooling'][0].reshape((1, 480))
        except Exception as e:
            print(e)
            raise ValueError
        return vec

    def batch_embedding(self, text_list):
        length = len(text_list)
        if length > self.max_batch_size:
            raise ValueError("the length of text_list exceeds max_batch_size")

        embedding_list = []

        for text in text_list:
            feature = convert_examples_to_features_sentence(text, self.tokenizer, self.max_seq_length)
            result = self.infer_handler.run(inputs={'input_ids': [feature['input_ids']],
                                                    'segment_ids': [feature['segment_ids']],
                                                    'input_mask': [feature['input_mask']]},
                                            outputs={'avgpooling': InferContext.ResultFormat.RAW},
                                            batch_size=length)
            try:
                vec = result['avgpooling'][0].reshape((1, 480))
            except Exception as e:
                print(e)
                raise ValueError
            embedding_list.append(vec)

        return np.concatenate(embedding_list)





