from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class ObjectTracker(object):
    @abstractmethod
    def track(self, video_data):
        """
        Parameters
        ----------
        video_data: VideoData
            the video data to be tracked
        Returns
        -------
        video_tracked_result: VideoTrackedObjects
            the tracked video result
        """
        pass
