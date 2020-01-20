import collections
import numpy as np


def convert_examples_to_features_sentence(question_text, tokenizer, max_seq_length):
    """Loads a data file into a list of `InputBatch`s."""

    query_tokens = tokenizer.tokenize(question_text)

    if len(query_tokens) > max_seq_length-2:  # one is for [CLS], the other is for [SEP]
        query_tokens = query_tokens[0:max_seq_length-2]

    tokens = []
    segment_ids = []
    tokens.append("[CLS]")
    segment_ids.append(1)
    for token in query_tokens:
        tokens.append(token)
        segment_ids.append(0)
    tokens.append("[SEP]")
    segment_ids.append(0)
    input_ids = tokenizer.convert_tokens_to_ids(tokens)
    # The mask has 1 for real tokens and 0 for padding tokens. Only real
    # tokens are attended to.
    input_mask = [1] * len(input_ids)
    # Zero-pad up to the sequence length.
    while len(input_ids) < max_seq_length:
        input_ids.append(0)
        input_mask.append(0)
        segment_ids.append(0)

    assert len(input_ids) == max_seq_length
    assert len(input_mask) == max_seq_length
    assert len(segment_ids) == max_seq_length

    def create_int_feature(values):
        feature = np.asarray(values, dtype=np.int32, order=None)
        return feature
    features = collections.OrderedDict()
    features["input_ids"] = create_int_feature(input_ids)
    features["input_mask"] = create_int_feature(input_mask)
    features["segment_ids"] = create_int_feature(segment_ids)
    features["tokens"] = tokens
    return features









