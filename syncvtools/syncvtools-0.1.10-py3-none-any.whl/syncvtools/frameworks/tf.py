import numpy as np, cv2

from syncvtools.data.image import img_rot90, img_flip, img_rotate
from syncvtools.utils._dependencies import dep
from syncvtools.data import detections as det_mod
from syncvtools.utils import file_tools as ft
from syncvtools.utils.draw_detections import DrawDetections, imshow
from syncvtools.utils.bbox import restore_boxes
from syncvtools.utils.center_point import backward_rotation_bbox_tf
import logging

tf = dep('tf')


def encode_image(input_image):
    # the input should be BGR
    input_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR)
    ret, img_buf = cv2.imencode('.png', input_image)
    if not ret:
        raise ValueError("Input image cannot be encoded")
    images_encoded = np.array([img_buf.tostring()])
    # images_encoded = img_buf.tostring()
    return images_encoded


class TensorflowInference:
    def __init__(self,
                 graph_src=None,
                 checkpoint_path = None,
                 label_map: str = None,
                 # label_map_read_func = ft.pbmap_read_to_dict
                 ):
        self.graph_data = {}

        # inference tensors and session
        self.input_tensor = None
        self.session = None
        self.output_tensors = None
        self.graph_loaded = False

        if graph_src:
            graph_src = ft.cache_file(graph_src)
            self.initialize_inference_graph(graph_src=graph_src)
            self.graph_loaded = True
        elif checkpoint_path:
            self.initialize_from_checkpoint(checkpoint_path=checkpoint_path)
            self.graph_loaded = True

        if label_map:
            label_map = ft.cache_file(label_map)
            self.label_map = ft.pbmap_read_to_dict(label_map)

    def initialize_inference_graph(self, graph_src,
                                   read_func=lambda x: tf.gfile.GFile(x, 'rb').read(),
                                   input_tensor_name='encoded_image_string_tensor:0',
                                   output_tensor_names=("detection_boxes",
                                                        "detection_scores",
                                                        "detection_classes",
                                                        "num_detections")
                                   ):
        # get a pointer to default graph
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            # make a serializable graph
            od_graph_def = tf.GraphDef()
            # graph can be written to string by any function (read_func param). Default is gfile.GFile
            serialized_graph = read_func(graph_src)
            # load from string to serializabl graph
            try:
                od_graph_def.ParseFromString(serialized_graph)
            except Exception:
                print("Graph is not frozen/readble: {}".format(graph_src))
            # import this text-graph to real default one (which is currently detection_graph)
            tf.import_graph_def(od_graph_def, name='')
            # create TF session
            self.session = tf.Session(graph=detection_graph)
            # get a pointer to input image from the graph

            self.input_tensor = detection_graph.get_tensor_by_name(input_tensor_name)
            self.output_tensors = [detection_graph.get_tensor_by_name("%s:0" % t) for t in output_tensor_names]

    def initialize_from_checkpoint(self, checkpoint_path,
                                   input_tensor_name='encoded_image_string_tensor:0',
                                   output_tensor_names=("detection_boxes",
                                                        "detection_scores",
                                                        "detection_classes",
                                                        "num_detections")
                                   ):
        # get a pointer to default graph
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            # make a serializable graph
            saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_path))
            self.session = tf.Session(graph=detection_graph)
            saver.restore(self.session, checkpoint_path)
            self.input_tensor = detection_graph.get_tensor_by_name(input_tensor_name)
            self.output_tensors = [detection_graph.get_tensor_by_name("%s:0" % t) for t in output_tensor_names]

    def detect_image_raw(self,
                         input_image: np.ndarray,
                         preprocess_func=encode_image,
                         rot90: int = None,
                         flip: int = None,
                         rotate = 0,
                         padding = 0,
                         ):
        '''

        :param input_image: RGB image (numpy array)
        :param preprocess_func: should output an encoded BGR PNG in bytes
        :return: dict of values. BOXES ARE IN ymin, xmin, ymax, xmax format
        '''
        if not self.graph_loaded:
            raise Exception(
                "Graph is not loaded! Run either constructor with graph_src param or initialize_inference_graph()")
        orig_size = input_image.shape[:2][::-1]
        if rotate:
            input_image = img_rotate(img_np=input_image,degree=rotate)
            rotated_size = input_image.shape[:2][::-1]

        if flip:
            input_image = img_flip(img_np=input_image, d=flip)

        if rot90:
            input_image = img_rot90(img_np=input_image, factor=rot90)

        if padding:
            input_image = cv2.copyMakeBorder(input_image,padding,padding,padding,padding,
                                             cv2.BORDER_CONSTANT,value=(255,255,255))

        images_encoded = preprocess_func(input_image)
        boxes, scores, classes, num = self.session.run(self.output_tensors,
                                                       feed_dict={self.input_tensor: images_encoded})

        classes = classes.astype(int)

        if rot90 or flip or padding:
            logging.debug("Restoring boxes..")
            boxes = restore_boxes(boxes=boxes,
                                  rot90=rot90,
                                  flip=flip,
                                  org_size = orig_size,
                                  modified_img_size=input_image.shape[:2][::-1],
                                  padding=padding)

        if rotate:
            logging.debug("Restoring original center points from rotated boxes..")
            points = backward_rotation_bbox_tf(bbox_norm=boxes, angle=rotate, org_size=orig_size, rot_size=rotated_size)
            return {'points': points, 'scores': scores, 'classes': classes, 'img_inf_size': input_image.shape}

            # boxes - (batch, num, min_y, min_x, max_y, max_x)
        return {'boxes': boxes, 'scores': scores, 'classes': classes, 'img_inf_size':input_image.shape}

    def detect_image(self,
                     input_image: np.ndarray,
                     preprocess_func=encode_image,
                     rot90: int = None,
                     flip: int = None,
                     rotate = 0,
                     padding = 0,
                     ):
        detections_raw = self.detect_image_raw(input_image=input_image, preprocess_func=preprocess_func,
                                               rot90=rot90, flip=flip,rotate=rotate,padding = padding)
        detections = []

        if rotate:
            for point, score, label_id in zip(detections_raw['points'][0], detections_raw['scores'][0],
                                            detections_raw['classes'][0]):
                label_id = int(label_id)
                label_text = self.label_map[label_id] if label_id in self.label_map else None
                detection_obj = det_mod.DetectionEntity(label_id=label_id,
                                                        label_text=label_text,
                                                        point_abs=tuple(map(int,point))[:2],
                                                        score=float(score),
                                                        img_size=(input_image.shape[1], input_image.shape[0]))
                detections.append(detection_obj)
        else:
            for box, score, label_id in zip(detections_raw['boxes'][0], detections_raw['scores'][0],
                                            detections_raw['classes'][0]):
                label_id = int(label_id)
                label_text = self.label_map[label_id] if label_id in self.label_map else None
                detection_obj = det_mod.DetectionEntity(label_id=label_id,
                                                        label_text=label_text,
                                                        bbox_norm=(box[1], box[0], box[3], box[2]),
                                                        score=float(score),
                                                        img_size=(input_image.shape[1], input_image.shape[0]))
                detections.append(detection_obj)
        return detections


if __name__ == '__main__':
    from syncvtools.utils.data_export import ProdDetectionsExport
    from syncvtools.utils.data_import import TFRecords
    from tqdm import tqdm
    import os

    if os.path.exists('/Users/apatsekin/projects'):
        path_to_projects = '/Users/apatsekin/projects'
    elif os.path.exists('/home/apatsekin/projects'):
        path_to_projects = '/home/apatsekin/projects'
    else:
        raise Exception("Path to projects not found")
    print("Project dir: {}".format(path_to_projects))
    # file_src = '/Users/apatsekin/Downloads/ammo_scans/SP-200H-231_20190920_00000547_top.png'
    inf = TensorflowInference(graph_src=os.path.join(path_to_projects,
                                                     'inference_models/tf/kix_6040_agp/20190719_AGP_6040ATIX_KIX_PNG_TF190.pb'),
                              label_map=os.path.join(path_to_projects,
                                                     'datasets/synapse/20190717_sdmv_ammo_gunparts_kix/label_map.pbtxt'))
    drawer = DrawDetections(bbox_line_height=2, threshold=0.1)
    print("parsing tf record")
    tfrec_obj = TFRecords.parse(
        tfrecord_src=os.path.join(path_to_projects, 'datasets/synapse/20190717_sdmv_ammo_gunparts_kix/val100.record'))
    print("inference started")
    for img_key in tqdm(tfrec_obj):
        img_obj = tfrec_obj[img_key]
        dets = inf.detect_image(input_image=img_obj.img.img_np)
        img_obj.detections = dets
        pred_json = os.path.join(path_to_projects,
                                 "datasets/synapse/20190717_sdmv_ammo_gunparts_kix/val100_detections/{}.json".format(
                                     img_key))

        ProdDetectionsExport.convert_one_save(path_src=pred_json, img_det=img_obj)
        # img_bbox = drawer.draw_imageleveldetections(img_dets=img_obj)
        # cv2.imshow('test', img_bbox)
        # cv2.waitKey(0)
