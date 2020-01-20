import matplotlib.pyplot as plt


class DataSegment(object):
    def __init__(self, data, metadata, label=None):
        self._metadata = metadata
        self._label = label
        self._original_index = data.index
        self._data = data.reset_index(drop=True)

    def __str__(self):
        return " ".join(["{}:{}".format(k, v) for k, v in self._metadata.items()])


class DataSegments(list):
    def plot(self):
        for segment in self.__iter__():
            segment._data.plot(title=str(segment))
            plt.show()
