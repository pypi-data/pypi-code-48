import cv2
from PIL import ImageFont, ImageDraw, Image
from typing import Tuple
from syncvtools.utils.file_tools import _mpath
from syncvtools.data.detections import ImageLevelDetections
import numpy as np


class DrawDetections:
    def __init__(self, bbox_line_height=2, threshold=0.5, top_boxes=100):
        self.bbox_line_height = bbox_line_height
        self.color_map = [(240, 0, 240), (0, 240, 240), (255, 255, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.threshold = threshold
        self.top_boxes = top_boxes

    def _resolve_text(self, det):
        if not det.label_text and not det.label_full_tag:
            return 'Class #{}'.format(det.label_id)
        if det.label_text and det.label_full_tag:
            return '{} ({})'.format(det.label_text, det.label_full_tag)
        return '{}'.format(det.label_text or det.label_full_tag)

    def draw_imageleveldetections(self, img_dets: ImageLevelDetections):
        if not img_dets.img:
            raise ValueError("The image in ImageLevelDetection object is empty/none. Can't visualize")
        dets_global = []
        gts_global = []
        imgs_global = []

        if img_dets._detections and len(img_dets._detections['default']) > 1:
            for model_id in img_dets._detections['default']:
                dets_global.append(img_dets._detections['default'][model_id].dets)
                gts_global.append(img_dets.ground_truth)
        dets_global.append(img_dets.detections)
        gts_global.append(img_dets.ground_truth)


        for dets, gts in zip(dets_global,gts_global):
            img = img_dets.img.img_np.copy()
            tag_orientation = 0
            if dets is not None:
                sort_inds = sorted(range(len(dets)), key=lambda k: -dets[k].score)
                for sorted_det_i in range(len(sort_inds)):
                    if sorted_det_i >= self.top_boxes:
                        break
                    det_i = sort_inds[sorted_det_i]
                    det = dets[det_i]
                    if det.score > self.threshold:
                        if det.bbox:
                            if det.bbox.bbox_abs is None:
                                raise Exception(
                                    "Bbox abs coords can't be figured out. Need to provide img_size or abs coordinates.")
                            draw_obj = det.bbox.bbox_abs
                        elif det.point:
                            draw_obj = (det.point.point_abs[0]-3, det.point.point_abs[1]-3,det.point.point_abs[0]+3,det.point.point_abs[1]+3)
                        else:
                            raise ValueError("Nothing to draw! No detected objects set")
                        label_txt = self._resolve_text(det=det)

                        img = self.draw_one(img_np=img,
                                            bbox=draw_obj,
                                            label_txt=label_txt,
                                            score=det.score,
                                            prefix='[{}]'.format(det_i),
                                            tag_orientation=tag_orientation)
                tag_orientation += 1

            if gts is not None:
                for gt_i, gt in enumerate(gts):
                    label_txt = self._resolve_text(det=gt)
                    img = self.draw_one(img_np=img,
                                        bbox=gt.bbox.bbox_abs,
                                        label_txt=label_txt,
                                        score=None,  # no score for GT
                                        color_id=1,
                                        prefix='[{}]'.format(gt_i),
                                        tag_orientation=tag_orientation)
                tag_orientation += 1
            imgs_global.append(img)

        img = np.concatenate(imgs_global,axis=1)
        if img_dets.ground_truth and img_dets.detections and img_dets.label_map:
            img_dets.calculate_metrics()
        if img_dets.detection_metrics:
            metrics_for_drawing = {}
            for metric_type in img_dets.detection_metrics:
                metrics_for_drawing[metric_type] = img_dets.detection_metrics[metric_type]['sum']
            img = self.draw_metrics(img_np=img,
                                    metrics=metrics_for_drawing)
        return img

    def _get_bg_tag_coords(self, bbox: Tuple[int, int, int, int],
                           tag_size: Tuple[int, int],
                           tag_orientation: int,
                           img_size: Tuple[int, int],
                           text_padding=2):
        # x1,y1,x2,y2 = [0]*4
        bhs = self.bbox_line_height // 2
        if tag_orientation == 0:
            x1 = bbox[0] - bhs
            y1 = bbox[1] - tag_size[1] - 2 * text_padding + bhs
            x2 = x1 + tag_size[0] + (2 * text_padding)
            y2 = y1 + tag_size[1] + 2 * text_padding
        elif tag_orientation == 1:
            x1 = bbox[0]
            y1 = bbox[3] + bhs
            x2 = x1 + tag_size[0] + (2 * text_padding)
            y2 = y1 + tag_size[1] + 2 * text_padding
        else:
            raise ValueError("This orientation is not implemented yet: {}".format(tag_orientation))

        if x1 < 0:
            # shift it to the right
            x2 = min(img_size[0] - 1, x2 - x1)
            # set to boundary
            x1 = 0

        if y1 < 0:
            y2 = min(img_size[1] - 1, y2 - y1)
            y1 = 0

        if x2 >= img_size[0]:
            x1 = max(0, x1 - (x2 - (img_size[0] - 1)))
            x2 = img_size[0] - 1

        if y2 >= img_size[1]:
            y1 = max(0, y1 - (y2 - (img_size[1] - 1)))
            y2 = img_size[1] - 1
        return x1, y1, x2, y2

    def draw_metrics(self,
                     img_np: np.ndarray,
                     metrics: dict,
                     ):
        '''
        Draws a key=>value metrics on a pledge added to picture.
        :param img_np:
        :param metrics:
        :return:
        '''
        font = ImageFont.truetype(font=_mpath("syncvtools/resources/tahoma.ttf"), size=12)
        text = "\n".join(["{}: {:0.4f}".format(k, v) for k, v in metrics.items()])
        txt_w, txt_h = font.getsize_multiline(text=text)
        txt_shift = (10, 10)
        padding = (4, 4)
        label_box = (
        txt_shift[0], txt_shift[1], txt_shift[0] + txt_w + 2 * padding[0], txt_shift[1] + txt_h + 2 * padding[1])
        pil_im = Image.fromarray(img_np)
        draw = ImageDraw.Draw(pil_im, 'RGBA')
        draw.rectangle(label_box, fill=(50, 50, 50) + (150,), outline=(50, 50, 50) + (150,))
        draw.text((label_box[0] + padding[0], label_box[1] + padding[1]), text, font=font, fill=(255, 255, 255, 255))
        img_np = np.array(pil_im)
        return img_np

    def draw_one(self,
                 img_np: np.ndarray,
                 bbox: Tuple[int, int, int, int],
                 label_txt="Detection",
                 score: float = None,
                 prefix: str = "",
                 suffix: str = "",
                 color_id=0,
                 tag_orientation=0) -> np.ndarray:

        if color_id >= len(self.color_map):
            raise ValueError("Color id can't be bigger than: {}".format(len(self.color_map)))

        font = ImageFont.truetype(font=_mpath("syncvtools/resources/tahoma.ttf"), size=13)
        if score is not None:
            score = "[{:.2f}] ".format(score)
        else:
            score = ""
        box_txt = "{}{}{}{}".format(prefix, score, label_txt, suffix)
        txt_w, txt_h = font.getsize(text=box_txt)
        # drawing a box
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        cv2.rectangle(img_np, (bbox[0], bbox[1]), (bbox[2], bbox[3]), self.color_map[color_id][::-1],
                      self.bbox_line_height)
        label_box = self._get_bg_tag_coords(bbox=bbox,
                                            tag_size=(txt_w, txt_h),
                                            tag_orientation=tag_orientation,
                                            img_size=(img_np.shape[1], img_np.shape[0])
                                            )
        img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        # drawing a filled rectangle for text
        # cv2.rectangle(img_np,
        #               (label_box[0], label_box[1]),
        #               (label_box[2], label_box[3]),
        #               self.color_map[color_id],
        #               thickness=-1)

        pil_im = Image.fromarray(img_np)
        draw = ImageDraw.Draw(pil_im, 'RGBA')
        draw.rectangle(label_box, fill=self.color_map[color_id] + (100,), outline=self.color_map[color_id] + (190,))
        draw.text((label_box[0] + 2, label_box[1] + 2), box_txt, font=font, fill=(255, 255, 255, 255))
        img_np = np.array(pil_im)

        return img_np


def imshow(img_np, waittime=0, title='Image'):
    '''

    :param img_np: RGB image in numpy uint8
    :param waittime: 0 - wait for any key press, >0 - wait milliseconds, -1 - don't wait at all
    :param title: different if you want a separate window
    :return:
    '''
    cv2.imshow(title, cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
    stop = False
    if waittime != -1:
        while (1):
            k = cv2.waitKey(waittime)
            if k == 27:  # Esc key to stop
                stop = True
                break
            elif waittime > 0:
                break
            elif waittime>0 or k == 32:  # normally -1 returned,so don't print it
                break
        if stop:
            return False
    return True


if __name__ == "__main__":
    test_bbox = DrawDetections(bbox_line_height=1)
    or_img = np.random.rand(np.random.randint(500, 800), np.random.randint(500, 800), 3) * 255
    or_img = or_img.astype(np.uint8)
    img_bbox = test_bbox.draw_one(img_np=or_img,
                                  bbox=(100, 100, 400, 400),
                                  label_txt="Demo detection", score=0.435, prefix="[prefix] sdfs dfs dfsd fsdf ",
                                  suffix="[suffix]",
                                  color_id=0, tag_orientation=0)

    img_bbox = test_bbox.draw_one(img_np=img_bbox,
                                  bbox=(105, 105, 396, 400),
                                  label_txt="Ground truth", score=None,
                                  color_id=1, tag_orientation=1)

    img_bbox = test_bbox.draw_one(img_np=img_bbox,
                                  bbox=(0, 0, 25, 25),
                                  label_txt="Big detection", score=0.252363236,
                                  color_id=0, tag_orientation=0)

    img_bbox = test_bbox.draw_one(img_np=img_bbox,
                                  bbox=(or_img.shape[1] - 1 - 200, or_img.shape[0] - 200, or_img.shape[1] - 1,
                                        or_img.shape[0] - 1),
                                  label_txt="Ground truth erew rwer rwe rwerwer test set setset ", score=None,
                                  color_id=1, tag_orientation=1)

    img_bbox = test_bbox.draw_metrics(img_np=img_bbox,
                                      metrics={'AP50': 0.243346346346, 'mAP': 0.23523623463246})

    cv2.imshow('bbox test', cv2.cvtColor(img_bbox, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
