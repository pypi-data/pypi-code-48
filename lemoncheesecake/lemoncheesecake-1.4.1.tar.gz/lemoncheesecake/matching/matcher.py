'''
Created on Mar 27, 2017

@author: nicolas
'''

import re

from typing import Optional, Any

CONJUGATION_FORMS = {
    re.compile(r"^(to be)"): ("is", "is not", "to not be"),
    re.compile(r"^(to have)"): ("has", "has not", "to have no"),
    re.compile(r"^(to match)"): ("matches", "does not match", "to not match"),
    re.compile(r"^(can)"): ("can", "cannot", "to cannot")
}


class MatcherDescriptionTransformer(object):
    """
    This class is used as a callable and passed to :py:meth:`Matcher.build_description`
    to transform the leading verb in description according to the transformer settings.
    """
    def __init__(self, conjugate=False, negative=False):
        #: indicate whether or not the verb in the description will be conjugated
        self.conjugate = conjugate
        #: indicate whether or not the description will be turned into the negative form
        self.negative = negative

    def __call__(self, description):
        # type: (str) -> str
        """
        Transform the description according transformer settings.
        """
        ###
        # No transformation to do
        ###
        if not self.conjugate and not self.negative:
            return description

        ###
        # Transformation of irregular verb
        ###
        for pattern, forms in CONJUGATION_FORMS.items():
            conjugated, conjugated_negative, infinitive_negative = forms
            if self.conjugate and self.negative:
                substitution = conjugated_negative
            elif self.conjugate:
                substitution = conjugated
            else:  # self.negative
                substitution = infinitive_negative

            if pattern.match(description):
                return pattern.sub(substitution, description)

        ###
        # Transformation of regular verb
        ###
        pattern = re.compile(r"^to (\w+)")
        m = pattern.match(description)
        if m:
            if self.conjugate and self.negative:
                substitution = "does not " + m.group(1)
            elif self.conjugate:
                substitution = m.group(1) + "s"
            elif self.negative:
                substitution = "to not " + m.group(1)
            else:
                substitution = "not " + m.group(1)

            return pattern.sub(substitution, description)

        ###
        # No verb detected
        ###
        return description


# In 1.1.0, MatchDescriptionTransformer has been renamed into MatcherDescriptionTransformer
# keep a MatchDescriptionTransformer alias for backward-compatibility
MatchDescriptionTransformer = MatcherDescriptionTransformer


class MatchResult(object):
    def __init__(self, is_successful, description=None):
        # type: (bool, Optional[str]) -> None
        #: whether or not the match did succeed
        self.is_successful = is_successful
        #: optional description
        self.description = description

    @classmethod
    def success(cls, description=None):
        # type: ( Optional[str]) -> "MatchResult"
        """
        Shortcut used to create a "successful" MatchResult.
        """
        return cls(True, description)

    @classmethod
    def failure(cls, description=None):
        # type: ( Optional[str]) -> "MatchResult"
        """
        Shortcut used to create a "failed" MatchResult.
        """
        return cls(False, description)

    def __bool__(self):
        """
        Returns whether or not the match is successful.
        """
        return self.is_successful

    def __nonzero__(self):  # Python 2.7 compatibility
        return self.__bool__()


class Matcher(object):
    def build_description(self, transformation):
        # type: (MatcherDescriptionTransformer) -> str
        """
        Build a description for the matcher given the instance of :py:class:`MatcherDescriptionTransformer`
        passed as argument.
        """
        raise NotImplementedError()

    def build_short_description(self, transformation):
        return self.build_description(transformation)

    def matches(self, actual):
        # type: (Any) -> MatchResult
        """
        Test if the passed argument matches.

        :param actual: the actual value to match
        :return: an instance of :py:class:`MatchResult`
        """
        raise NotImplementedError()
