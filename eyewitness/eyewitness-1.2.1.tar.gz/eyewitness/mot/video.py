import os
import logging
from pathlib import Path
from abc import ABCMeta, abstractmethod

import six
import ffmpeg
import numpy as np
from PIL import Image

LOG = logging.getLogger(__name__)


def is_program_exists(program):
    """ since the python-ffmpeg needs the host install ffmpeg first
    thus we need a method that can used to find executable file exists

    Parameters:
    -----------
    program: str
        the executable file to fine

    Returns:
    --------
    is_file_exists: bool
        return the executable file exists or not

    """
    return any(
        os.access(os.path.join(path, program), os.X_OK)
        for path in os.environ["PATH"].split(os.pathsep)
    )


@six.add_metaclass(ABCMeta)
class VideoData:
    """
    this class were used to represent a Video (List of Frames)
    """

    @abstractmethod
    def __getitem__(self, index):
        """
        Parameters:
        -----------
        index: int
            the index of frame to return

        Returns
        -------
        image_obj: PIL.Image.Image
            return the image_obj
        """
        pass

    @property
    @abstractmethod
    def n_frames(self):
        pass

    @property
    @abstractmethod
    def frame_shape(self):
        pass

    @property
    @abstractmethod
    def frame_rate(self):
        pass


class FilesAsVideoData(VideoData):
    def __init__(self, image_files, frame_shape=None, frame_rate=3):
        self.image_files = list(image_files)
        if frame_shape is None:
            self.frame_shape_ = Image.open(self.image_files[0]).size
        else:
            self.frame_shape_ = frame_shape
        self.frame_rate_ = frame_rate

    def __getitem__(self, index):
        """
        Parameters:
        -----------
        index: int
            the index of frame to return, frame idx starts from 1

        Returns
        -------
        pil_image_obj: PIL.Image.Image
            return the image_obj
        """
        img = Image.open(str(self.image_files[index - 1]))
        if img.size == self.frame_shape:
            return img
        else:
            return img.resize(self.frame_shape)

    @property
    def n_frames(self):
        return len(self.image_files)

    @property
    def frame_shape(self):
        return self.frame_shape_

    @property
    def frame_rate(self):
        return self.frame_rate_

    def to_video(self, video_output_path, ffmpeg_quiet=True):
        if not is_program_exists("ffmpeg"):
            LOG.critical(
                "if you want to export video, you need to install ffmpeg in you host first,"
                "since the python-ffmpeg were depend on this library"
            )
        video_output = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
                s="{}x{}".format(*self.frame_shape),
                framerate=self.frame_rate,
            )
            .output(video_output_path, pix_fmt="yuv420p")
            .overwrite_output()
            .run_async(pipe_stdin=True, quiet=ffmpeg_quiet)
        )

        for idx in range(1, self.n_frames + 1):
            img = self[idx]
            video_output.stdin.write(np.array(img).tobytes())

        video_output.stdin.close()
        video_output.wait()


class FolderAsVideoData(FilesAsVideoData):
    def __init__(self, images_dir, file_template="*[0-9].jpg"):
        images = sorted(Path(images_dir).glob(file_template))
        super(FolderAsVideoData, self).__init__(images)


class Mp4AsVideoData(VideoData):
    def __init__(self, video_file, ffmpeg_quiet=True, in_memory=True):
        if not is_program_exists("ffmpeg"):
            LOG.critical(
                "if you want to export video, you need to install ffmpeg in you host first,"
                "since the python-ffmpeg were depend on this library"
            )
        # get video information
        self.video = ffmpeg.input(str(video_file))
        self.ffmpeg_quiet = ffmpeg_quiet

        video_stream_probe = [
            i
            for i in ffmpeg.probe(str(video_file))["streams"]
            if i["codec_type"] == "video"
        ][0]
        self.frame_shape_ = (video_stream_probe["width"], video_stream_probe["height"])
        # FIXME: notice that not all the mp4 with nb_frames / avg_frame_rate field
        self.n_frames_ = int(video_stream_probe["nb_frames"])
        self.frame_rate_ = self.n_frames_ / float(video_stream_probe["duration"])

        # load all frames into memory

        if in_memory:
            self.images_in_memory = []
            out, _ = (
                ffmpeg.input(str(video_file))
                .output("pipe:", format="rawvideo", pix_fmt="rgb24")
                .run(capture_stdout=True, quiet=ffmpeg_quiet)
            )
            video = np.frombuffer(out, np.uint8).reshape(
                [-1, self.frame_shape[1], self.frame_shape[0], 3]
            )
            for idx in range(video.shape[0]):
                self.images_in_memory.append(Image.fromarray(video[idx, :, :, :]))
        else:
            self.images_in_memory = None

    def __getitem__(self, index):
        """
        Parameters:
        -----------
        index: int
            the index of frame to return, frame idx starts from 1

        Returns
        -------
        pil_image_obj: PIL.Image.Image
            return the image_obj
        """
        if self.images_in_memory is None:
            out, _ = (
                self.video.filter("select", "gte(n,{})".format(index - 1))
                .output("pipe:", vframes=1, format="rawvideo", pix_fmt="rgb24")
                .run(capture_stdout=True, quiet=self.ffmpeg_quiet)
            )

            np_array = np.frombuffer(out, np.uint8).reshape(
                [self.frame_shape[1], self.frame_shape[0], 3]
            )
            img = Image.fromarray(np_array)
        else:
            img = self.images_in_memory[index - 1]

        if img.size == self.frame_shape:
            return img
        else:
            return img.resize(self.frame_shape)

    @property
    def n_frames(self):
        return self.n_frames_

    @property
    def frame_shape(self):
        return self.frame_shape_

    @property
    def frame_rate(self):
        return self.frame_rate_
