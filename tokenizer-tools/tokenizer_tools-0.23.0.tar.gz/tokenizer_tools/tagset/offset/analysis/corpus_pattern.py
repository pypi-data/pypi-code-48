import itertools
from typing import Dict, List

from tokenizer_tools.tagset.offset.analysis.express_pattern import \
    ExpressPattern
from tokenizer_tools.tagset.offset.corpus import Corpus


class CorpusPattern(Corpus):
    @classmethod
    def create_from_corpus(cls, corpus: Corpus) -> "CorpusPattern":
        pattern_set = set()
        for doc in corpus:
            pattern = ExpressPattern.convert_to_pattern(doc)
            pattern_set.add(pattern)

        return cls(pattern_set)

    def render(self, dictionary: Dict[str, List[str]]):
        doc_list = []

        for pattern in self:
            placeholder_names = [i.entity for i in pattern.get_placeholders()]
            pattern_specific_dictionary = {i: dictionary[i] for i in placeholder_names}

            #
            instance_list_variable = list(itertools.product(*pattern_specific_dictionary.values()))

            for instance_variable in instance_list_variable:
                instance_mapping = dict(
                    zip(pattern_specific_dictionary.keys(),
                        instance_variable))

                doc = pattern.render(**instance_mapping)
                doc_list.append(doc)

        return Corpus(doc_list)

    def _render_single_pattern(self, pattern: ExpressPattern):
        pass

    def _generate_entity_candidate(self) -> List[Dict[str, str]]:
        pass
