from collections import defaultdict

import pandas as pd
import numpy as np
from eyewitness.config import BoundedBoxObject
from eyewitness.utils import bbox_intersection_over_union
import motmetrics


class VideoTrackedObjects(defaultdict):
    """ actually a VideoTrackedObjects object is a subclass of defaultdict with list
    and expected result were Dict[int, List[BoundedBoxObject]]
    """
    def __init__(self):
        super(VideoTrackedObjects, self).__init__(list)

    def to_file(self, dest_file):
        keys = sorted(list(self.keys()))
        output = []
        for frame_id in keys:
            bboxes = self[frame_id]
            for bbox in bboxes:
                width = bbox.x2 - bbox.x1
                height = bbox.y2 - bbox.y1
                output.append((frame_id, bbox.label, bbox.x1, bbox.y1, width, height, bbox.score))
        pd.DataFrame(output).to_csv(dest_file, header=False, index=False)

    @classmethod
    def from_tracked_file(cls, trajectory_file, ignore_gt_flag=False):
        """
        parsed the trajectory file, and reuse the BoundedBoxObject class

        Parameters
        ----------
        track_file: str
            the file path of object tracking ground_truth, format is
            `<frame>, <id>, <bb_left>, <bb_top>, <bb_width>, <bb_height>, <conf>...`

        Returns
        -------
        parsed_tracked_objects: Dict[int, List[BoundedBoxObject]]
            key is the frame_idx, value is the objects detected in this frame
            and the label field in BoundedBoxObject were set as object_id
        """

        df = pd.read_csv(trajectory_file, header=None)

        # as mentioned at https://motchallenge.net/instructions/
        # the <conf> field in gt means this field is not used to
        # evaluation
        if ignore_gt_flag:
            df = df[df.iloc[:, 7].astype(int) == 1]

        df = df.iloc[:, :7]
        df.columns = [
            "frame",
            "object_id",
            "left",
            "top",
            "width",
            "height",
            "conf"
        ]
        parsed_tracked_objects = cls()
        for _, row in df.iterrows():
            x1, y1 = float(row.left), float(row.top)
            x2, y2 = float(row.left + row.width), float(row.top + row.height)
            parsed_tracked_objects[int(row.frame)].append(
                BoundedBoxObject(x1, y1, x2, y2, int(row.object_id), float(row.conf), "")
            )
        return parsed_tracked_objects

    @classmethod
    def from_dict(cls, tracked_obj_dict):
        video_tracked_objects = cls()
        for k, v in tracked_obj_dict.items():
            video_tracked_objects[k] = v
        return video_tracked_objects


def mot_evaluation(video_gt_objects, video_tracked_objects, threshold=0.5):
    """ with the help of motmetrics we can evaluate our mot tracker

    Parameters:
    -----------
    video_gt_objects: Dict[int, List[BoundedBoxObject]]
        ground_truth object of video,
        key is the frame_idx, value is the objects detected in this frame
        and the label field in BoundedBoxObject were set as object_id
    video_tracked_objects: Dict[int, List[BoundedBoxObject]]
        predicted mot result of video,
        key is the frame_idx, value is the objects detected in this frame
        and the label field in BoundedBoxObject were set as object_id

    Returns:
    --------
    summary: Dataframe
        the dataframe of evaluation result with the fields used in
        MOT2019 https://motchallenge.net/results/CVPR_2019_Tracking_Challenge/

    """
    mh = motmetrics.metrics.create()
    acc = motmetrics.MOTAccumulator(auto_id=True)
    frame_ids = sorted(video_gt_objects.keys())
    for frame_id in frame_ids:
        gt_bboxes = video_gt_objects[frame_id]
        gt_ids = [i.label for i in gt_bboxes]
        if frame_id in video_tracked_objects:
            tracked_objects = video_tracked_objects[frame_id]
            tracked_ids = [i.label for i in tracked_objects]

            frame_iou_list = []
            for gt_idx, gt_bbox in enumerate(gt_bboxes):
                iou_list = []
                for tracked_object in tracked_objects:
                    iou = bbox_intersection_over_union(gt_bbox[:4], tracked_object[:4])
                    iou_list.append(iou)
                frame_iou_list.append(iou_list)

            distance_matrix = 1 - np.vstack(frame_iou_list)
            # iou < threshold need to be set as nan
            distance_matrix[distance_matrix > (1 - threshold)] = np.nan

            acc.update(
                gt_ids,
                tracked_ids,
                distance_matrix,
            )
        else:
            acc.update(
                gt_ids,
                [],
                [[], []],
            )

    summary = mh.compute(
        acc,
        metrics=[
            "motp",
            "mota",
            "idf1",
            "mostly_tracked",
            "mostly_lost",
            "num_false_positives",
            "num_misses",  # fn
            "num_switches",
            "num_fragmentations",
        ],
        name="final",
    )
    return summary
