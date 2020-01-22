"""Functions and interfaces regarding the creation of audio/visual media."""
import abc

import alsaaudio
import seaborn as sns


class Visual(metaclass=abc.ABCMeta):
    """Interface that signifies an object can be plotted."""

    @property
    @abc.abstractmethod
    def x_plot():
        pass

    @property
    @abc.abstractmethod
    def y_plot():
        pass


class Audio(metaclass=abc.ABCMeta):
    """Interface that signifies an object can be played."""

    @abc.abstractmethod
    def read_bytes():
        pass

    @abc.abstractmethod
    def bytesPerSample():
        pass

    @abc.abstractmethod
    def seek():
        pass


def play(audio_object, sample_rate=44100, n_channels=1, device="default"):
    device = alsaaudio.PCM(device=device)

    device.setchannels(n_channels)
    frame_rate = int(sample_rate / n_channels)
    device.setrate(frame_rate)
    device.setchannels(n_channels)

    bytesPerSample = audio_object.bytesPerSample
    if bytesPerSample == 1:
        device.setformat(alsaaudio.PCM_FORMAT_U8)
    # Otherwise we assume signed data, little endian
    elif bytesPerSample == 2:
        device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    elif bytesPerSample == 3:
        device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
    elif bytesPerSample == 4:
        device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
    else:
        raise ValueError("Unsupported format")

    bytesPerFrame = bytesPerSample * n_channels * 10
    periodsize = bytesPerFrame * 10
    device.setperiodsize(periodsize)

    audio_object.seek()

    chunk = audio_object.read_bytes(periodsize)
    while chunk:
        while len(chunk) != periodsize:
            chunk = chunk + b" "
        device.write(chunk)
        chunk = audio_object.read_bytes(periodsize)


def plot(visual_object, **kwargs):
    """Plot timeseries as a seaborn plot."""
    x_lim = kwargs.get("xlim", None)
    print(x_lim)
    y_lim = kwargs.get("ylim", None)

    x_attr = kwargs.get("x_attr", visual_object.x_plot)
    y_attr = kwargs.get("y_attr", visual_object.y_plot)

    z = sns.scatterplot(x=x_attr, y=y_attr)

    z.set(xlim=x_lim)
    z.set(ylim=y_lim)

    return z

