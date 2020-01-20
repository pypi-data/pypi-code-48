import logging
from pathlib import Path

import ffmpeg
import numpy as np
from PIL import Image, ImageDraw
from eyewitness.utils import make_path
from eyewitness.mot.video import is_program_exists

LOG = logging.getLogger(__name__)


def draw_tracking_result(  # noqa
    parsed_tracked_objects,
    color_list,
    video_obj,
    output_images_dir=None,
    output_video_path=None,
    n_trajectory=50,
    ffmpeg_quiet=True,
):
    """ this method used to draw the tracked result back to original video
    notice that, if you want to export to output_video_path, you need to
    install it in your host, e.g. apt install ffmpeg

    Parameters
    ----------
    parsed_tracked_objects: Dict[int, List[BoundedBoxObject]]
        key is the frame_idx, value is the objects detected in this frame
        and the label field in BoundedBoxObject were set as object_id
    color_list: List[tuple[int]]
        the color_list used to draw each object_id
    video_obj: VideoData
        the original video object
    output_images_dir: Optional[str]
        the dir used to stored drawn image, the stored template is
        Path(output_images_dir, "%s.jpg" % str(t).zfill(6)), t is current frame number
    output_video_path: Optional[str]
        the output path of video
    n_trajectory: int
        the number of previous point to be drawn
    ffmpeg_quiet: bool
        route the ffmpeg_quiet logging to stdout or not
    """

    if output_images_dir is not None:
        LOG.info("export drawn images to %s", output_images_dir)
        make_path(output_images_dir)

    if output_video_path is not None:
        LOG.info("export drawn video to %s", output_video_path)
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
                s="{}x{}".format(*video_obj.frame_shape),
                framerate=video_obj.frame_rate,
            )
            .output(output_video_path, pix_fmt="yuv420p")
            .overwrite_output()
            .run_async(pipe_stdin=True, quiet=ffmpeg_quiet)
        )

    n_frames = min(max(parsed_tracked_objects.keys()), video_obj.n_frames)

    LOG.info("n_frames: %s, frame_rate: %s", n_frames, video_obj.frame_rate)

    for t in range(1, int(n_frames) + 1):
        img = video_obj[t].convert("RGBA")

        # plot the trajectory for previous n frames
        previous_frames = [
            i for i in range(t, t - 50, -1) if t in parsed_tracked_objects
        ]
        bb_size = 5
        empty_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
        for t_previous in previous_frames:
            empty_draw = ImageDraw.Draw(empty_img)
            alpha = int(0.9 ** (t - t_previous) * 255)  # Transparency factor.
            bbox_objects = parsed_tracked_objects[t_previous]
            # plot the major bbox
            for bbox_object in bbox_objects:
                color_ind = bbox_object.label % len(color_list)
                color_with_alpha = tuple([i for i in color_list[color_ind]] + [alpha])
                xc = int((bbox_object.x1 + bbox_object.x2) / 2)
                yc = bbox_object.y2
                empty_draw.rectangle(
                    [(xc, yc), (xc + bb_size, yc + bb_size)], fill=color_with_alpha
                )
        img = Image.alpha_composite(img, empty_img)

        # plot the major bbox
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)
        bbox_objects = parsed_tracked_objects[t]
        for bbox_object in bbox_objects:
            color_ind = bbox_object.label % len(color_list)
            draw.rectangle(
                [(bbox_object.x1, bbox_object.y1), (bbox_object.x2, bbox_object.y2)],
                outline=color_list[color_ind],
                width=3,
            )

        if output_video_path is not None:
            video_output.stdin.write(np.array(img).tobytes())

        if output_images_dir is not None:
            output_img_path = Path(output_images_dir, "%s.jpg" % str(t).zfill(6))
            img.save(str(output_img_path))

    # cleanup
    LOG.info("clean up ....")
    if output_video_path is not None:
        video_output.stdin.close()
        video_output.wait()
