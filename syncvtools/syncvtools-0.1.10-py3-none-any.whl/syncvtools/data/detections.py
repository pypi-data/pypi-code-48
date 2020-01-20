from typing import Tuple, Any, Union, List, Dict, Callable
from syncvtools.data.image import ImgSize, Image
from syncvtools.data.bbox import Bbox
from syncvtools.data.center_point import CenterPoint
# from syncvtools.utils.bbox import normalize_bbox
import syncvtools.utils.file_tools as ft
from syncvtools.utils.bbox import box_fusion
# from syncvtools.utils.bbox import bbox_flip, bbox_rot90
# import syncvtools.data.annotated_tag as annotated_tag

from syncvtools.utils.file_tools import _mpath
import logging, re, numpy as np, bisect
import syncvtools.metrics.coco_eval as coco_eval
from collections import defaultdict

full_tag_to_tag = None


class UnknownTagException(Exception):
    pass


class DetectionEntity:
    def __init__(self,
                 label_text: str = None,  # actual class like sharp, handgun, ammo-single, etc.
                 bbox_abs: Tuple[int, int, int, int] = None,
                 bbox_norm: Tuple[float, float, float, float] = None,
                 score: float = None,
                 mask: Tuple[Union[float, int]] = None,
                 point_abs: Tuple[int, int] = None,
                 point_norm: Tuple[float, float] = None,
                 label_id: int = None,  # index assigned by labelmaps
                 label_full_tag=None,  # full annotation from annotators
                 img_size: Tuple[int, int] = None
                 ):

        # if label_text is None or len(label_text) == 0:
        #     raise ValueError("label_text param is None or zero length")
        # that's what goes to model as label_map text. SOmething like "sharp" or "gun"
        # that's what we store in image/object/category field -- original full tag of the detection. "sharp-c2"
        self.label_full_tag = label_full_tag
        if label_text:
            self.label_text = label_text
        else:
            self.label_text = None
            if label_full_tag:
                parsed_tag = DetectionEntity.parse_full_tag(label_full_tag)
                if parsed_tag:
                    self.label_text = parsed_tag
                else:
                    logging.debug(
                        "Wasn't able to parse a full tag: {}.Setting 'unknown_tag' to label_text as is".format(
                            label_full_tag))
                    self.label_text = 'unknown_tag'

        if img_size is not None:
            if len(img_size) not in (2, 3):
                raise ValueError("Image size should be a tuple of size 2 or 3")
            self._img_size = ImgSize(width=img_size[0], height=img_size[1])
        else:
            self._img_size = None

        if bbox_norm is not None or bbox_abs is not None:
            # setting bounding box coordinates either from absolute values or from normalized
            self.bbox = Bbox(bbox_norm=bbox_norm, bbox_abs=bbox_abs, img_size=self._img_size)
        else:
            self.bbox = None

        if point_norm is not None or point_abs is not None:
            self.point = CenterPoint(point_norm=point_norm, point_abs=point_abs, img_size=img_size)
        else:
            self.point = None

        if score is not None:
            if score < 0.0 or score > 1.0:
                raise ValueError("Score (confidence) should be [0;1] range")
            self.score = score

        self.label_id = label_id

    @staticmethod
    def parse_full_tag(full_tag):
        def remove_difficulty_rating(cat):
            return re.sub(r'-[0-4][A-C]$', '', cat)

        global full_tag_to_tag

        def remove_orientation(cat):
            return re.sub(r'-c[1-3]$', "", cat)

        def parse_bucket_map(bucket_map_str):
            lines = bucket_map_str.split("\n")
            bucket_tuples = [tuple(line.strip().split()) for line in lines if line != ""]
            bucket_map = {}
            for fine_class, coarse_class in bucket_tuples:
                bucket_map[fine_class] = coarse_class
            return bucket_map

        if not full_tag_to_tag:
            with open(_mpath("syncvtools/resources/full_tag_to_tag.txt"), "r") as bucket_map_file:
                bucket_map_str = bucket_map_file.read()
                bucket_map = parse_bucket_map(bucket_map_str)
            full_tag_to_tag = bucket_map

        full_tag = remove_orientation(remove_difficulty_rating(full_tag))
        if full_tag in full_tag_to_tag:
            return full_tag_to_tag[full_tag]
        elif full_tag == '?3C':  # hack for wrong diff annotation (should be ?-3C)
            return '?'
        else:
            return None

    def set_img_size(self, img_size: ImgSize):
        if img_size is None:
            raise Exception("None image size provided")
        self._img_size = img_size
        if self.bbox:
            self.bbox.img_size = self._img_size
        if self.point:
            self.point.img_size = self._img_size
        return self

    @property
    def img_size(self):
        return self._img_size

    @img_size.setter
    def img_size(self, v: ImgSize):
        self.set_img_size(v)


class ModelDetections:
    '''
    Detections of one model
    '''

    def __init__(self, dets=None, params=None):
        if not dets:
            self.dets = []
        else:
            self.dets = dets
        if not params:
            self.params = {}
        else:
            self.params = params


class ImageLevelDetections:
    def __init__(self,
                 img: Image = None,
                 detections: List[DetectionEntity] = None,
                 ground_truth: List[DetectionEntity] = None):
        self._img = None
        # dictionary of detections {'model_type' => {'model_id' => ModelDetections(dets=[list of detections])}}
        self._detections = None
        # calculated detections (averaged)
        self._detections_cached = None
        self._ground_truth = None
        # all other image level fields that can be parsed, i.e. filename and path may come from PascalVOC XML,
        # although it's image related stuff. But actual image can be absent at all!!
        self.gt_metadata = {}
        self.img = img
        self.detections = detections
        # metrics from MSCOCO: mAP, AP0.5 by label and by area of bounding boxes.
        # organized as multi-dim array: [label_id][area_id] -> dict (output of coco_eval.evaluateImg)
        self.detection_evaluations = None
        self.detection_metrics = None
        # label map. Maps class IDs to class text names. Also has .asarray property which is just array of class text names.
        self.label_map = None
        self.ground_truth = ground_truth
        self.detection_entities = ['img', 'detections', 'ground_truth']

    @property
    def detections(self):
        # TODO implement merging of differnet types of models. I.e. hs and agp
        if self._detections is None:
            return None
        if self._detections_cached is not None:
            return self._detections_cached

        models_count = len(self._detections['default'])
        # there are two types of detections right now: bboxes and points (center points)

        boxes_list = {}
        points_list = {}
        if len(self._detections['default']) <= 1:
            return next(iter(self._detections['default'].items()))[1].dets
        for model_key in self._detections['default']:
            dets = self._detections['default'][model_key].dets
            for det in dets:
                if det.bbox:
                    # since in ImageLevelDetections detections field is just list, we don't
                    # know upfront what type of detections this list consists of
                    if model_key not in boxes_list:
                        boxes_list[model_key] = []
                    try:
                        boxes_list[model_key].append([det.label_id, det.score] + list(det.bbox.bbox_norm))
                    except Exception as e:
                        logging.warning("Bounding box is broken. Can't infer _norm size during attempt to merge detections: {}. Error: {}".format(det.bbox, str(e)))
                elif det.point:
                    if model_key not in points_list:
                        points_list[model_key] = []
                    points_list[model_key].append([det.label_id, det.score] + list(det.point.point_norm))
        merged_boxes_list = box_fusion(boxes_list, points_list)
        fused_dets = []
        for i in range(len(merged_boxes_list)):
            det = DetectionEntity(label_id=merged_boxes_list[i][0],
                                  label_text=self.label_map[merged_boxes_list[i][0]],
                                  score=merged_boxes_list[i][1],
                                  bbox_norm=merged_boxes_list[i][2:],
                                  img_size=self.img.img_size.as_tuple()
                                  )
            fused_dets.append(det)
        self._detections_cached = fused_dets

        return fused_dets

    @detections.setter
    def detections(self, dets):
        if dets is None:
            return
        if isinstance(dets, list):
            self._set_img_size(dets)
            if self._detections is None:
                # type (hs/agp) => model_id (anything, i.e. for ensembles resnet50_1, resnet50_2) => {params: a=1, dets: []
                self._detections = {'default': {'default': ModelDetections()}}
            self._detections['default']['default'].dets = dets
        elif isinstance(dets, dict):
            self._set_img_size(dets['dets'].dets)
            # self.restore_boxes(dets['dets'])
            type_ = 'default'
            model_ = 'default'
            if 'type' in dets:
                type_ = dets['type']
            if 'model' in dets:
                model_ = dets['model']
            if self._detections is None:
                self._detections = {}
            if type_ not in self._detections:
                self._detections[type_] = {}
            if model_ not in self._detections[type_]:
                assert isinstance(dets['dets'], ModelDetections)
                self._detections[type_][model_] = dets['dets']
        self._detections_cached = None

    def _set_img_size(self, dets):
        if dets is not None:
            if self.img is not None:
                for det in dets:
                    if det.img_size is None:
                        det.img_size = self.img.img_size

    UNKNOWN_TAG_DROP_BOX = 0
    UNKNOWN_TAG_RAISE_EXCEPTION = 1
    UNKNOWN_TAG_KEEP = 2

    def process_labelmap(self, label_map: Dict[int, str], inverse_label_map=None,
                         unknown_tag_action=UNKNOWN_TAG_DROP_BOX):
        '''
        Applies label map and delets all unknown labels
        :param label_map:
        :param inverse_label_map:
        :return:
        '''
        if inverse_label_map is None:
            inverse_label_map = {v: k for k, v in label_map.items()}
        self.label_map = label_map

        if self._detections is not None:
            for model_type in self._detections:
                for model_id in self._detections[model_type]:
                    dets_per_model_per_type = self._detections[model_type][model_id].dets
                    for det in dets_per_model_per_type:
                        if det.label_text is None and det.label_id is not None:
                            if det.label_id in label_map:
                                det.label_text = label_map[det.label_id]
                            else:
                                logging.debug(
                                    "label_dict ({}) doesn't have corresponding label_id found in detections: {}".format(
                                        list(label_map.keys()), det.label_id))
                        elif det.label_id is None and det.label_text is not None:
                            if det.label_text in inverse_label_map:
                                det.label_id = inverse_label_map[det.label_text]
                            else:
                                logging.debug(
                                    "label_dict ({}) doesn't have corresponding label_text found in detections: {}".format(
                                        list(label_map.values()), det.label_text))

        if self.ground_truth is not None:
            for gt in self.ground_truth[:]:
                if gt.label_text is None and gt.label_id is not None:
                    if gt.label_id in label_map:
                        gt.label_text = label_map[gt.label_id]
                    else:
                        logging.debug(
                            "label_dict ({}) doesn't have corresponding label_id found in ground truth: {}".format(
                                list(label_map.keys()), gt.label_id))
                        self.ground_truth.remove(gt)
                elif gt.label_id is None and gt.label_text is not None:
                    if gt.label_text in inverse_label_map:
                        gt.label_id = inverse_label_map[gt.label_text]
                    else:
                        logging.debug(
                            "label_dict ({}) doesn't have corresponding label_text found in ground truth: {}".format(
                                list(label_map.values()), gt.label_text))
                        if unknown_tag_action == ImageLevelDetections.UNKNOWN_TAG_DROP_BOX:
                            logging.debug("^ Removing that box")
                            self.ground_truth.remove(gt)
                        elif unknown_tag_action == ImageLevelDetections.UNKNOWN_TAG_RAISE_EXCEPTION:
                            logging.debug("^ Raising exception. Likely whole image will be dropped")
                            raise UnknownTagException(
                                "label_dict ({}) doesn't have corresponding label_text found in ground truth: {}".format(
                                    list(label_map.values()), gt.label_text))
                        elif unknown_tag_action == ImageLevelDetections.UNKNOWN_TAG_KEEP:
                            logging.debug("^ That box will be preserved")
                            pass
                        else:
                            raise Exception(
                                "Unknown value for unknown_tag_action:{}. What to do with unknown tags?".format(
                                    unknown_tag_action))

    # @detections.setter
    # def detections(self, dets: List[DetectionEntity]):
    #     #when detections are added, check if img size is not set there, and try to link it to images (if they added already)
    #     if self.img is not None:
    #         for det in dets:
    #             if det.img_size is None:
    #                 det.img_size = self.img.img_size
    #     self._detections = dets

    def evaluate_detections(self):
        '''
        Prepares evaluations for further calculating AP, mAP, etc..
        :return: list [label, areaRng, evaluations] for particular Image
        '''
        if self.detection_evaluations:
            return
        if self.ground_truth is None:
            logging.warning("Ground truth is not set")
            return
        if self.detections is None:
            logging.warning("Detections is not set")
            return
        if self.label_map is None:
            logging.warning("Label_map is not set")
            return
        evalImgs = []
        for label_i, label_text in enumerate(list(self.label_map.values())):
            eval_area = []
            evalImgs.append(eval_area)
            for area_i, area_rng in enumerate(coco_eval.COCOParams.areaRng):
                eval_area.append(coco_eval.evaluateImg(
                    dts_all=self.detections,
                    gts_all=self.ground_truth,
                    catId=label_text,
                    aRng=area_rng))
        self.detection_evaluations = evalImgs

    def calculate_metrics(self):
        if self.detection_metrics:
            return
        self.evaluate_detections()
        if not self.detection_evaluations:
            return
        accumulated = coco_eval.accumulate(det_col=self.detection_evaluations,
                                           catIds=list(self.label_map.values()),
                                           per_image=True)
        ap10, ap10_by_cat = coco_eval.summarize(acc_result=accumulated,
                                                iouThr=0.1,
                                                areaRng='all',
                                                maxDets=100)
        ap10_by_cat = dict(zip(self.label_map.values(), ap10_by_cat))

        mAP, mAP_by_cat = coco_eval.summarize(acc_result=accumulated,
                                              iouThr=None,
                                              areaRng='all',
                                              maxDets=100)
        mAP_by_cat = dict(zip(self.label_map.values(), mAP_by_cat))

        self.detection_metrics = {
            'ap10': {"sum": ap10,
                     "by_cat": ap10_by_cat},
            'mAP': {"sum": mAP,
                    "by_cat": mAP_by_cat},

        }

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, im):
        # when img is added, check if detections are already present, update their size if needed
        if im is not None and im.img_size is not None:
            if self._detections is not None:
                for model_type in self._detections:
                    for model_id in self._detections[model_type]:
                        dets_per_model_per_type = self._detections[model_type][model_id].dets
                        for det in dets_per_model_per_type:
                            if det.img_size is None:
                                det.img_size = im.img_size
            if self.ground_truth is not None:
                for gt in self.ground_truth:
                    if gt.img_size is None:
                        gt.img_size = im.img_size
        self._img = im

    @property
    def ground_truth(self):
        return self._ground_truth

    @ground_truth.setter
    def ground_truth(self, gts: List[DetectionEntity]):
        # when gts are added, check if img size is not set there, and try to link it to images (if they added already)
        if gts is not None:
            if self.img is not None:
                for gt in gts:
                    if gt.img_size is None:
                        gt.img_size = self.img.img_size
        self._ground_truth = gts

    def __str__(self):
        if self.ground_truth:
            gt = ",".join(["{} ({}) - [{}]".format(gt.label_text, gt.label_full_tag, gt.bbox.bbox_abs) for gt in
                           self.ground_truth])
        else:
            gt = "Not set"
        if self.img:
            img = "size {}".format(self.img._img_size)
        else:
            img = "None"
        return "|Img: {}, GT: {}|".format(img, gt)


class DetectionsCollection(dict):
    '''
    Consists of key=>value storage for ImageLevelDetections (or ScanLevelDetections in future)
    Provides options to create/update images, ground_truths, detections.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # label map - dict in TF format pbtxt of mapping id to class
        self.label_map = None
        # AP, mAP per dataset (with breakdown per class)
        self.detection_metrics = None
        # dictionary of counts for classes (labels)
        self.gt_counts = None
        # dictionary of FP and FN for detections. Obtained through self.get_misses()
        self.detection_misses = None
        self._fa_vs_recall_data = None

    def process_images(self, img_dict: Dict[str, Image], update_only: bool = False):
        '''
        Adds images to collection. If update_only, then it will only add image detections to existing elements
        (image name exist in collection)
        :param img_dict:
        :param update_only:
        :return:
        '''
        for img_key in img_dict:
            if img_key in self:
                self[img_key].img = img_dict[img_key]
            else:
                if update_only:  # don't need to create new dict elements
                    continue
                self[img_key] = ImageLevelDetections(img=img_dict[img_key])

    def process_detections(self, det_dict: Dict[str, List[DetectionEntity]], update_only: bool = False):
        '''
        Adds detections to collection. If update_only, then it will only add detections to existing elements
        (image name exist in collection)
        :param det_dict:
        :param update_only:
        :return:
        '''
        for det_key in det_dict:
            if det_key in self:
                self[det_key].detections = det_dict[det_key]
            else:
                if update_only:  # don't need to create new dict elements
                    continue
                self[det_key] = ImageLevelDetections(detections=det_dict[det_key])

    def apply_filters(self, image_level=(), bbox_level=()):
        '''
        Apply image-level and bbox-level filters to detection collection. Filter can modify
        bbox/imagelevel-detection or just return False so it's deleted.
        Right now implementation implies, that when filter returns False - no further filters are applied
        So all "void" filters should go first.
        :param image_level:
        :param bbox_level:
        :return:
        '''
        stat = {'image_level': defaultdict(int), 'bbox_level': defaultdict(int)}
        stat_samples = {'image_level': defaultdict(list), 'bbox_level': defaultdict(list)}

        for bbox_func in bbox_level:
            if not bbox_func:
                raise ValueError("Empty box function passed")
        for image_func in image_level:
            if not image_func:
                raise ValueError("Emptmy image function passed")

        for img_key in list(self):
            logging.debug("GT before filtration {}: {}".format(img_key, self[img_key]))
            if self[img_key].ground_truth:
                gts = self[img_key].ground_truth
                for gt_i, gt in enumerate(gts):
                    bbox_result = False  # don't remove this bbox
                    for bbox_func in bbox_level:
                        bbox_result = bbox_func(gts[gt_i])
                        if bbox_result:
                            stat['bbox_level'][bbox_func.__name__] += 1
                            stat_samples['bbox_level'][bbox_func.__name__].append(
                                "{} - {}".format(img_key, gt.label_text))
                            # TODO or should we continue? in case there void functions down the list
                            break
                    if bbox_result:  # remove this bbox
                        gts.remove(gts[gt_i])

            image_result = False
            for image_func in image_level:
                if image_func.__name__ not in stat['image_level']:
                    stat['image_level'][image_func.__name__] = 0
                image_result = image_func(self[img_key], img_key)
                if image_result:
                    stat['image_level'][image_func.__name__] += 1
                    stat_samples['image_level'][image_func.__name__].append("{}: {}".format(img_key, self[img_key]))
                    # TODO or should we continue? in case there void functions down the list
                    break
            if image_result:  # remove this bbox
                del self[img_key]
            logging.debug(
                "GT after filtration {}: {}".format(img_key, self[img_key] if img_key in self else 'Image deleted'))
        stat = {'image_level': dict(stat['image_level']), 'bbox_level': dict(stat['bbox_level'])}
        logging.info("Filter application result: %s", stat)
        for typ_ in stat_samples:
            for sample_type in stat_samples[typ_]:
                logging.info("Samples for {}: {}".format(typ_, sample_type))
                for sample_ in stat_samples[typ_][sample_type][:20]:
                    logging.info(sample_)
        return True

    def process_ground_truth(self, gt_dict: Dict[str, List[DetectionEntity]],
                             update_only: bool = False):
        # stat={'dropped_unknown': 0, 'dropped_question': 0}
        for gt_key in gt_dict:
            # is_drop = False
            # for gt in gt_dict[gt_key]:
            #     if drop_unknown and gt.label_text == 'unknown_tag':
            #         is_drop = True
            #         stat['dropped_unknown'] +=1
            #         break
            #     elif gt.label_text == '?':
            #         is_drop = True
            #         stat['dropped_question'] += 1
            #         break
            # if is_drop:
            #     if gt_key in self:
            #         del self[gt_key]
            #     continue

            if gt_key in self:
                self[gt_key].ground_truth = gt_dict[gt_key]
            else:
                if update_only:  # don't need to create new dict elements
                    continue
                self[gt_key] = ImageLevelDetections(ground_truth=gt_dict[gt_key])
            logging.debug("Set GT {}: {}".format(gt_key, self[gt_key]))
        # logging.info("Dropped images while processing GT: {}".format(stat))

    def process_field(self, field_name, field_dict: Dict[str, Dict], update_only: bool = False):
        '''
        Updates field in ImageLevelDetections
        :param field_name:
        :param field_dict:
        :param update_only:
        :return:
        '''
        for field_key in field_dict:
            if field_key in self:
                if not hasattr(self[field_key], field_name) or not isinstance(getattr(self[field_key], field_name),
                                                                              dict):
                    raise TypeError(
                        "Every ImageLevelDetection should have a property of type `dict`: {}".format(field_name))
                old_dict = getattr(self[field_key], field_name)
                setattr(self[field_key], field_name, {**old_dict, **field_dict[field_key]})
            else:
                if update_only:  # don't need to create new dict elements
                    continue
                pass  # don't know what to do here. Is it the case to have an ImageLevelDetections with just this data?

    def process_labelmap(self,
                         label_dict: Any,
                         input_parser: Callable[[str], Any] = ft.pbmap_read_to_dict,
                         unknown_tag_action=ImageLevelDetections.UNKNOWN_TAG_DROP_BOX
                         ):
        '''
        Adds label_map to property of this class. Also to each of the ImageLevelDetections, which in turn updates all
        label_txt/label_id fields in detections.
        :param label_dict:
        :param input_parser:
        :return:
        '''
        label_dict = ft.cache_file(label_dict)
        label_dict = input_parser(label_dict)
        self.label_map = label_dict
        inverse_label_dict = {v: k for k, v in label_dict.items()}
        for key in list(self):
            try:
                self[key].process_labelmap(label_map=label_dict, inverse_label_map=inverse_label_dict,
                                           unknown_tag_action=unknown_tag_action)
            except UnknownTagException as e:
                if unknown_tag_action == ImageLevelDetections.UNKNOWN_TAG_RAISE_EXCEPTION:
                    del self[key]
                    logging.warning("Dropping image {} with unknown box.".format(key))
                else:
                    raise UnknownTagException(
                        'Detection Collection does not know what to do with unknown tag:').with_traceback(
                        e.__traceback__)

    def calculate_metrics(self):
        for img_key in self:
            self[img_key].evaluate_detections()
        accumulated = coco_eval.accumulate(det_col=self,
                                           catIds=list(self.label_map.values()))

        ap10, ap10_by_cat = coco_eval.summarize(acc_result=accumulated,
                                                iouThr=0.1,
                                                areaRng='all',
                                                maxDets=100)
        ap10_by_cat = dict(zip(self.label_map.values(), ap10_by_cat))

        mAP, mAP_by_cat = coco_eval.summarize(acc_result=accumulated,
                                              iouThr=None,
                                              areaRng='all',
                                              maxDets=100)
        mAP_by_cat = dict(zip(self.label_map.values(), mAP_by_cat))

        self.detection_metrics = {
            'ap10': {"sum": ap10,
                     "by_cat": ap10_by_cat},
            'mAP': {"sum": mAP,
                    "by_cat": mAP_by_cat},
        }

    def get_counts(self):
        if self.gt_counts is None:
            counts = defaultdict(int)
            for img_key in self:
                if self[img_key].ground_truth:
                    for gt in self[img_key].ground_truth:
                        counts[gt.label_text] += 1
                counts['total'] += 1
            self.gt_counts = counts
        return self.gt_counts

    def get_fa_vs_recall_data(self, debug_mode=False):
        '''
        Collects Highest FA score for each box. Also collects thresholds of detections for each GT box.
        :param debug_mode:
        :return:
        '''

        if self._fa_vs_recall_data is None:
            self._fa_vs_recall_data = {}
            label_keys = self.label_map.keys()
            label_values = tuple(self.label_map.values())

            for label_i in range(len(label_keys)):
                fa_rate_per_img = []
                gt_recall_per_box = []
                for img_key in self:
                    is_good = None
                    self[img_key].evaluate_detections()
                    # [0]- first size range
                    eval_img = self[img_key].detection_evaluations[label_i][0]  # for specific label, first range

                    if eval_img is not None:  # [iouthreshold, dtId index for each gt box]
                        matched_dt_ids = set()
                        if len(eval_img['gtMatches']) > 0:
                            for gt_indx, dt_id in enumerate(
                                    eval_img['gtMatches'][0]):  # [0.5 iOu, gtId index for each dt box]
                                dtId = int(dt_id)
                                if dtId == 0:
                                    gt_recall_per_box.append(0.0)
                                else:
                                    gt_recall_per_box.append(self[img_key].detections[dtId - 1].score)
                                    matched_dt_ids.add(dtId)
                        # all_dt_ids = set()
                        max_fa = 0.0
                        for i, dt_id in enumerate(eval_img['dtIds']):
                            dtId = int(dt_id)
                            if dtId in matched_dt_ids:  # not FA
                                continue
                            if self[img_key].detections[dtId - 1].score > max_fa:  # highest FA so far?
                                max_fa = self[img_key].detections[dtId - 1].score
                        fa_rate_per_img.append(max_fa)
                fa_rate_per_img.sort()
                gt_recall_per_box.sort()
                self._fa_vs_recall_data[label_values[label_i]] = {'fa_rate_per_img': fa_rate_per_img,
                                                                  'gt_recall_per_box': gt_recall_per_box}
        return self._fa_vs_recall_data

    def draw_fa_vs_recall_graphs(self, save_path, steps=100):
        import matplotlib.pyplot as plt
        data = self.get_fa_vs_recall_data()
        step_thresh = np.linspace(0.0, 1.0, num=steps)

        for label_i, label_text in enumerate(data):
            fig, ax = plt.subplots(2, 1, figsize=(65, 60))
            fa_graph = np.zeros((len(step_thresh)))
            recall_graph = np.zeros((len(step_thresh)))
            for i in range(len(step_thresh)):
                # images with FA rate lower or equal to this threshold
                fa_graph[i] = 1 - bisect.bisect_left(data[label_text]['fa_rate_per_img'], step_thresh[i]) / (
                            len(data[label_text]['fa_rate_per_img']) + 1e-10)

                if len(data[label_text]['gt_recall_per_box']):
                    # boxes with TPs with greater or equal to this threshold
                    recall_graph[i] = 1 - bisect.bisect_left(data[label_text]['gt_recall_per_box'], step_thresh[i]) / (
                                len(data[label_text]['gt_recall_per_box']) + 1e-10)
            print("{} FA rates:".format(label_text))
            fa_dict = dict(zip(step_thresh, fa_graph))
            for fa_rate in fa_dict:
                print("{:.2f}: {:.4f}, ({}/{})".format(fa_rate, fa_dict[fa_rate],
                                                       int(fa_dict[fa_rate] * (
                                                                   len(data[label_text]['fa_rate_per_img']) + 1e-10)),
                                                       (len(data[label_text]['fa_rate_per_img']))), end=", ")
            print("")
            ax[1].scatter(step_thresh, recall_graph, s=100)
            ax[1].set_title('{} Recall'.format(label_text))
            ax[1].xaxis.set_ticks(np.arange(0, 1, 0.01))
            ax[1].yaxis.set_ticks(np.arange(0, 1, 0.01))
            ax[1].grid()

            ax[0].scatter(step_thresh, fa_graph, s=100)
            ax[0].set_title('{} FA Rate'.format(label_text))
            ax[0].xaxis.set_ticks(np.arange(0, 1, 0.01))
            ax[0].yaxis.set_ticks(np.arange(0, 1, 0.01))
            ax[0].grid()
            fig.savefig("{}-{}.png".format(save_path, label_text))

    def get_misses(self, fp_threshold=0.5, fn_threshold=0.0, debug_mode=True):
        '''

        :param fp_threshold: False-Positive threshold. All predicted boxes with confidence higher then this threshold
        and no matching ground-truth are considered as FP. Lower value - tougher.
        :param fn_threshold: False-Negative threshold. Predicted boxes are matched to GT only if their confidence
        higher than this threshold. Otherwise GT counted as False Negative. Higher value - tougher.
        :return:
        '''
        if debug_mode:
            from syncvtools.utils.draw_detections import DrawDetections
            drawer = DrawDetections(bbox_line_height=1, threshold=0.1)
            import cv2
        if not self.detection_misses:
            fn_imgs = defaultdict(set)
            fp_imgs = defaultdict(set)
            # good_imgs = defaultdict(set)
            label_keys = self.label_map.keys()
            label_values = tuple(self.label_map.values())
            good_imgs = set(self.keys())
            for label_i in range(len(label_keys)):
                for img_key in self:
                    is_good = None
                    self[img_key].evaluate_detections()
                    # [0]- first size range
                    eval_img = self[img_key].detection_evaluations[label_i][0]  # for specific label

                    if eval_img is not None and len(
                            eval_img['gtMatches']) > 0:  # [iouthreshold, dtId index for each gt box]
                        matched_dt_ids = set()
                        for gt_indx, dt_id in enumerate(
                                eval_img['gtMatches'][0]):  # [0.5 iOu, gtId index for each dt box]
                            if is_good is None:
                                is_good = True
                            # getting matched dt box
                            # dtId = int(evaled_img['dtIds'][int(dt_indx)])
                            dtId = int(dt_id)
                            if dtId == 0 or self[img_key].detections[dtId - 1].score < fn_threshold:  # unmatched GT
                                fn_imgs[label_values[label_i]].add(img_key)
                                is_good = False
                                logging.debug("Image {}. Class: {} : FN".format(img_key, label_values[label_i]
                                                                                )
                                              )
                            else:
                                matched_dt_ids.add(dtId)
                        all_dt_ids = set()
                        for i, dt_id in enumerate(eval_img['dtIds']):
                            if eval_img['dtScores'][i] > fp_threshold:
                                all_dt_ids.add(int(dt_id))
                        # all_dt_ids = set(evaled_img['dtIds'])
                        unmatched_dt_ids = all_dt_ids - matched_dt_ids
                        if len(unmatched_dt_ids) > 0:
                            fp_imgs[label_values[label_i]].add(img_key)
                            is_good = False
                            logging.debug("Image {} Class: {} : FP".format(img_key, label_values[label_i]))
                        elif is_good is None:
                            is_good = True

                        if not is_good:
                            good_imgs.discard(img_key)
                            # good_imgs[label_values[label_i]].add(img_key)

                        if debug_mode:
                            logging.debug("GT matches: {}".format(eval_img['gtMatches'][0]))
                            img_bbox = drawer.draw_imageleveldetections(img_dets=self[img_key])
                            img_bbox = cv2.cvtColor(img_bbox, cv2.COLOR_RGB2BGR)
                            cv2.imshow('test', img_bbox)
                            cv2.waitKey(0)
            good_img_dict = defaultdict(list)
            for img_key in good_imgs:
                gt_set = set()
                for gt in self[img_key].ground_truth:
                    gt_set.add(gt.label_text)
                good_img_dict[tuple(sorted(gt_set))].append(img_key)

            self.detection_misses = {'fp': fp_imgs, 'fn': fn_imgs, 'good': good_img_dict}
        return self.detection_misses

    def save_misses(self, save_dir: str, fp_threshold: float, fn_threshold: float, drawer_options={}):
        from syncvtools.utils.draw_detections import DrawDetections
        if 'threshold' not in drawer_options:
            drawer_options['threshold'] = fp_threshold

        drawer = DrawDetections(**drawer_options)
        misses = self.get_misses(fp_threshold=fp_threshold,
                                 fn_threshold=fn_threshold)
        for type_ in misses:
            for label in misses[type_]:
                for img_key in misses[type_][label]:
                    img_bbox = drawer.draw_imageleveldetections(img_dets=self[img_key])
                    ft.img_np_to_disk(img_np=img_bbox,
                                      save_path='{}/{}/{}/{}.jpg'.format(save_dir, type_, label, img_key))

    def __add__(self, other):
        for key in self:
            if key in other:
                for attr in self[key].detection_entities:
                    if getattr(self[key], attr) is None and getattr(other[key], attr) is not None:
                        setattr(self[key], attr, getattr(other[key], attr))
        return self

    def __getitem__(self, key):
        if not isinstance(key, slice):
            return super().__getitem__(key)
        slicedkeys = list(self.keys())[key]
        data = DetectionsCollection()
        for key in slicedkeys:
            data[key] = self[key]
        return data
