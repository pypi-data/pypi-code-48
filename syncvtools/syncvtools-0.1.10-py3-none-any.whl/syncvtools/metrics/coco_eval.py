'''
Fork of tsungyi version of COCOeval github library
'''

import numpy as np
import datetime
import time
from collections import defaultdict
#from . import mask as maskUtils
import copy
import logging
#import pycocotools._mask as _mask
#from syncvtools.utils.bbox import abs_x1y1wh_to_abs_x1y1x2y2, abs_x1y1x2y2_to_abs_x1y1wh

def iou_run(bboxes1, bboxes2):
    '''

    :param bboxes1:[n,4] x1,y1,x2,y2 in integers
    :param bboxes2: [m,4] x1,y1,x2,y2 in integers
    :return: [n,m] matrix of ious. To fetch iou: [bboxes1_index, bboxes2_index]
    '''
    #bboxes1 = np.asarray(bboxes1).reshape(-1,4)
    #bboxes2 = np.asarray(bboxes2).reshape(-1,4)
    #bboxes1 = abs_xywh_to_abs_x1y1x2y2(bboxes1)
    #bboxes2 = abs_xywh_to_abs_x1y1x2y2(bboxes2)
    x11, y11, x12, y12 = np.split(bboxes1, 4, axis=1)
    x21, y21, x22, y22 = np.split(bboxes2, 4, axis=1)
    xA = np.maximum(x11, np.transpose(x21))
    yA = np.maximum(y11, np.transpose(y21))
    xB = np.minimum(x12, np.transpose(x22))
    yB = np.minimum(y12, np.transpose(y22))
    interArea = np.maximum((xB - xA + 1), 0) * np.maximum((yB - yA + 1), 0)
    boxAArea = (x12 - x11 + 1) * (y12 - y11 + 1)
    boxBArea = (x22 - x21 + 1) * (y22 - y21 + 1)
    iou = interArea / (boxAArea + np.transpose(boxBArea) - interArea)
    return iou

def iou_run_norm(bboxes1, bboxes2):
    #bboxes1 = np.asarray(bboxes1).reshape(-1,4)
    #bboxes2 = np.asarray(bboxes2).reshape(-1,4)
    #bboxes1 = abs_xywh_to_abs_x1y1x2y2(bboxes1)
    #bboxes2 = abs_xywh_to_abs_x1y1x2y2(bboxes2)
    x11, y11, x12, y12 = np.split(bboxes1, 4, axis=1)
    x21, y21, x22, y22 = np.split(bboxes2, 4, axis=1)
    xA = np.maximum(x11, np.transpose(x21))
    yA = np.maximum(y11, np.transpose(y21))
    xB = np.minimum(x12, np.transpose(x22))
    yB = np.minimum(y12, np.transpose(y22))
    interArea = np.maximum((xB - xA), 0) * np.maximum((yB - yA), 0)
    boxAArea = (x12 - x11) * (y12 - y11)
    boxBArea = (x22 - x21) * (y22 - y21)
    iou = interArea / (boxAArea + np.transpose(boxBArea) - interArea)
    return iou



class COCOParams:
    iouThrs = np.linspace(.1, 0.90, np.round((0.90 - .1) / .1) + 1, endpoint=True)
    recThrs = np.linspace(.0, 1.00, np.round((1.00 - .0) / .01) + 1, endpoint=True)
    maxDets = [100]#[1, 10, 100]
    areaRng = [[0 ** 2, 1e5 ** 2]] #, [0 ** 2, 32 ** 2], [32 ** 2, 96 ** 2], [96 ** 2, 1e5 ** 2]]
    areaRngLbl = ['all', 'small', 'medium', 'large']

def evaluateImg(dts_all, gts_all, aRng, catId, maxDet = 100):

    '''

    :param dts: [{'score': 0.3333,'area':w*h, 'bbox': [1.1,2.2,3.3,4.4]},'id':]
    :param gts: [{'ignore':0, 'area':w*h,'bbox': [1,2,3,4]},'id':]
    :param aRng:
    :return:
    '''

    for i,dt in enumerate(dts_all):
        if dt.label_text != catId:
            continue
        dt.area = (dt.bbox.bbox_abs[2] - dt.bbox.bbox_abs[0]) * (dt.bbox.bbox_abs[3] - dt.bbox.bbox_abs[1])
        dt.id = i+1

    for i, gt in enumerate(gts_all):
        if gt.label_text != catId:
            continue
        gt.area = (gt.bbox.bbox_abs[2] - gt.bbox.bbox_abs[0]) * (gt.bbox.bbox_abs[3] - gt.bbox.bbox_abs[1])
        gt.id = i+1
        gt.ignore = 0 #keep for future use

    dts = []
    gts = []
    for dt in dts_all:
        if dt.label_text == catId:
            dts.append(dt)

    for gt in gts_all:
        if gt.label_text == catId:
            gts.append(gt)




    gt_bboxes = [gt.bbox.bbox_abs for gt in gts]
    inds = np.argsort([-d.score for d in dts], kind='mergesort')
    dt_bboxes = [dt.bbox.bbox_abs for dt in dts]
    dt_bboxes = [dt_bboxes[i] for i in inds]


    iscrowd = [0 for o in gt_bboxes]
    gt_bboxes = np.asarray(gt_bboxes).reshape(-1, 4)
    dt_bboxes = np.asarray(dt_bboxes).reshape(-1, 4)

    #########
    # logging.info("Using COCO native IoU function:")
    # dt_bboxes = abs_x1y1x2y2_to_abs_xywh(dt_bboxes)
    # gt_bboxes = abs_x1y1x2y2_to_abs_xywh(gt_bboxes)
    # ious = _mask.iou(dt_bboxes,gt_bboxes,iscrowd)
    #########

    ious = iou_run(dt_bboxes, gt_bboxes)

    if len(gts) == 0 and len(dts) == 0:
        return None

    for g in gts:
        if g.ignore or (g.area < aRng[0] or g.area > aRng[1]):
            g._ignore = 1
        else:
            g._ignore = 0

    # sort dt highest score first, sort gt ignore last
    gtind = np.argsort([g._ignore for g in gts], kind='mergesort')
    gt = [gts[i] for i in gtind]
    dtind = np.argsort([-d.score for d in dts], kind='mergesort')
    dt = [dts[i] for i in dtind[0:maxDet]]
    # load computed ious
    ious = ious[:, gtind] if len(ious) > 0 else ious

    T = len(COCOParams.iouThrs)
    G = len(gt)
    D = len(dt)
    gtm = np.zeros((T, G))
    dtm = np.zeros((T, D))
    gtIg = np.array([g._ignore for g in gt])
    dtIg = np.zeros((T, D))

    if not len(ious) == 0:
        for tind, t in enumerate(COCOParams.iouThrs):
            for dind, d in enumerate(dt):
                # information about best match so far (m=-1 -> unmatched)
                iou = min([t, 1 - 1e-10])
                m = -1
                for gind, g in enumerate(gt):
                    # if this gt already matched, and not a crowd, continue
                    if gtm[tind, gind] > 0:
                        continue
                    # if dt matched to reg gt, and on ignore gt, stop
                    if m > -1 and gtIg[m] == 0 and gtIg[gind] == 1:
                        break
                    # continue to next gt unless better match made
                    if ious[dind, gind] < iou:
                        continue
                    # if match successful and best so far, store appropriately
                    iou = ious[dind, gind]
                    m = gind
                # if match made store id of match for both dt and gt
                if m == -1:
                    continue
                dtIg[tind, dind] = gtIg[m]
                dtm[tind, dind] = gt[m].id
                gtm[tind, m] = d.id

    # set unmatched detections outside of area range to ignore
    a = np.array([d.area < aRng[0] or d.area > aRng[1] for d in dt]).reshape((1, len(dt)))
    dtIg = np.logical_or(dtIg, np.logical_and(dtm == 0, np.repeat(a, T, 0)))
    # store results for given image and category
    return {
        #'imgKey': imgKey if imgKey else None,
        'category_id': catId,
        'aRng': aRng,
        'maxDet': maxDet,
        'dtIds': [d.id for d in dt], #ids of all dt boxes, corresponds to dtMatches
        'gtIds': [g.id for g in gt], #ids of all gt boxes, corresponds to gtMatches
        'dtMatches': dtm, # shape: [iouthreshold, gtId for each dt box]
        'gtMatches': gtm, # shape: [iouthreshold, dtId  for each gt box]
        'dtScores': [d.score for d in dt],
        'gtIgnore': gtIg,
        'dtIgnore': dtIg,
    }

# def accumulate_singleimg(evalImg_result, catIds: list):
#     '''
#             Accumulate per image evaluation results and store the result in self.eval
#             :param p: input params for evaluation
#             :return: None
#             '''
#     logging.info('Accumulating evaluation results...')
#     tic = time.time()
#     # allows input customized parameters
#     #p.catIds = catIds
#     T = len(COCOParams.iouThrs)
#     R = len(COCOParams.recThrs)
#     K = len(catIds)
#     A = len(COCOParams.areaRng)
#     M = len(COCOParams.maxDets)
#     precision = np.full((T, R, K, A, M), np.nan) #-np.ones((T, R, K, A, M))  # -1 for the precision of absent categories
#     recall = -np.ones((T, K, A, M))
#     scores = -np.ones((T, R, K, A, M))
#
#     # create dictionary for future indexing
#     #_pe = self._paramsEval
#     #catIds = _pe.catIds if _pe.useCats else [-1]
#     # set_cat_ids = set(catIds)
#     # set_area_rngs = set(map(tuple, COCOParams.areaRng))
#     # set_max_dets_limit = set(COCOParams.maxDets)
#     # #setI = set(_pe.imgIds)
#     # # get inds to evaluate
#     # k_list = [n for n, k in enumerate(catIds) if k in set_cat_ids] #list of categories
#     m_list = [m for n, m in enumerate(COCOParams.maxDets)] #list of maxdetection limits [1,10,100]
#     # a_list = [n for n, a in enumerate(map(lambda x: tuple(x), COCOParams.areaRng)) if a in set_area_rngs] #area ranges [0,1,2,3]
#     # #i_list = [n for n, i in enumerate(p.imgIds) if i in setI]
#     # #I0 = len(_pe.imgIds)
#     # A0 = len(COCOParams.areaRng)
#     # retrieve E at each category, area range, and max number of detections
#     for label_i in range(len(catIds)):  # by category
#         for arearng_i  in range(len(COCOParams.maxDets)):  # by areaRng
#             for maxdets_i, maxDet in enumerate(m_list):  # by maxDetes (1, 10, 100)
#                 E = evalImg_result[label_i][arearng_i]
#                 # E = [e for e in E if not e is None]
#                 # if len(E) == 0:
#                 #     continue
#                 if E is None:
#                     continue
#                 dtScores = np.asarray(E['dtScores'][0:maxDet])
#
#                 # different sorting method generates slightly different results.
#                 # mergesort is used to be consistent as Matlab implementation.
#                 inds_by_score = np.argsort(-dtScores, kind='mergesort')
#                 #sorted confidence values across all images
#                 dtScoresSorted = dtScores[inds_by_score]
#                 #dtMatches shape - (len(gt),len(dt)), after concat - len(gt), len(td)
#                 dtm = (E['dtMatches'][:, 0:maxDet])[:,inds_by_score]
#                 dtIg = (E['dtIgnore'][:, 0:maxDet])[:, inds_by_score]
#                 gtIg = E['gtIgnore']
#                 npig = np.count_nonzero(gtIg == 0)
#                 if npig == 0:
#                     continue
#                 tps = np.logical_and(dtm, np.logical_not(dtIg))
#                 fps = np.logical_and(np.logical_not(dtm), np.logical_not(dtIg))
#
#                 tp_sum = np.cumsum(tps, axis=1).astype(dtype=np.float)
#                 fp_sum = np.cumsum(fps, axis=1).astype(dtype=np.float)
#                 for iou_thresh_i, (tp, fp) in enumerate(zip(tp_sum, fp_sum)):
#                     tp = np.array(tp)
#                     fp = np.array(fp)
#                     nd = len(tp)
#                     rc = tp / npig
#                     pr = tp / (fp + tp + np.spacing(1))
#                     q = np.zeros((R,))
#                     ss = np.zeros((R,))
#
#                     if nd:
#                         recall[iou_thresh_i, label_i, arearng_i, maxdets_i] = rc[-1]
#                     else:
#                         recall[iou_thresh_i, label_i, arearng_i, maxdets_i] = 0
#
#                     # numpy is slow without cython optimization for accessing elements
#                     # use python array gets significant speed improvement
#                     pr = pr.tolist()
#                     q = q.tolist()
#
#                     for i in range(nd - 1, 0, -1):
#                         if pr[i] > pr[i - 1]:
#                             pr[i - 1] = pr[i]
#
#                     inds_by_score = np.searchsorted(rc, COCOParams.recThrs, side='left')
#                     try:
#                         for ri, pi in enumerate(inds_by_score):
#                             q[ri] = pr[pi]
#                             ss[ri] = dtScoresSorted[pi]
#                     except:
#                         pass
#                     #: - recall thresholds(101)
#                     precision[iou_thresh_i, :, label_i, arearng_i, maxdets_i] = np.array(q)
#                     scores[iou_thresh_i, :, label_i, arearng_i, maxdets_i] = np.array(ss)
#     eval = {
#         'counts': [T, R, K, A, M],
#         'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#         'precision': precision,
#         'recall': recall,
#         'scores': scores,
#     }
#     return eval


def accumulate(det_col, catIds: list, per_image = False):
    '''
    Accumulates results across all images in dataset.
    '''
#    logging.info('Accumulating evaluation results...')
#    tic = time.time()
    if not det_col:
        raise ValueError("Detection collection is empty")
    # allows input customized parameters
    T = len(COCOParams.iouThrs)
    R = len(COCOParams.recThrs)
    K = len(catIds)
    A = len(COCOParams.areaRng)
    M = len(COCOParams.maxDets)
    precision = np.full((T, R, K, A, M), np.nan) #-np.ones((T, R, K, A, M))  # -1 for the precision of absent categories
    recall = np.full((T, K, A, M), np.nan)#-np.ones((T, K, A, M))
    scores = np.full((T, R, K, A, M), np.nan) #-np.ones((T, R, K, A, M))

    # get inds to evaluate
    #k_list = [n for n, k in enumerate(catIds)]
    m_list = [m for n, m in enumerate(COCOParams.maxDets)]
    #a_list = [n for n, a in enumerate(map(lambda x: tuple(x), COCOParams.areaRng))]
    #i_list = [n for n, i in enumerate(det_col.keys())]
    # retrieve E at each category, area range, and max number of detections
    for label_i in range(len(catIds)):  # by category
        for arearng_i in range(len(COCOParams.maxDets)):  # by areaRng
            for maxdets_i, maxDet in enumerate(m_list):  # by maxDetes (1, 10, 100)
                if per_image:
                    E = [det_col[label_i][arearng_i]]
                else:
                    E = [det_col[img_key].detection_evaluations[label_i][arearng_i] for img_key in det_col]
                E = [e for e in E if not e is None]
                if len(E) == 0:
                    continue
                dtScores = np.concatenate([e['dtScores'][0:maxDet] for e in E])

                # different sorting method generates slightly different results.
                # mergesort is used to be consistent as Matlab implementation.
                inds_by_score = np.argsort(-dtScores, kind='mergesort')
                dtScoresSorted = dtScores[inds_by_score]
                # shape dtm = len(imgs), len(gt), len(dt (maxDet))
                dtm = [e['dtMatches'][:, 0:maxDet] for e in E]  # 1758 (images), 10 (ioThresholds), 1 (detections)
                # shape dtm = len(gt), len(imgs) -- concated by gt
                dtm = np.concatenate(dtm, axis=1)  # 10 (iouThresholds), 1758 (images)
                dtm = dtm[:, inds_by_score]  # resort by score all bboxes through all images
                dtIg = np.concatenate([e['dtIgnore'][:, 0:maxDet] for e in E], axis=1)[:, inds_by_score]  # shape = 10, 1758
                gtIg = np.concatenate([e['gtIgnore'] for e in E])  # shape (952,)
                npig = np.count_nonzero(gtIg == 0)
                if npig == 0:
                    continue
                tps = np.logical_and(dtm, np.logical_not(dtIg))  # 10, 1758
                fps = np.logical_and(np.logical_not(dtm), np.logical_not(dtIg))  # 10, 1758

                tp_sum = np.cumsum(tps, axis=1).astype(dtype=np.float)  # across all images, (10, 1758)
                fp_sum = np.cumsum(fps, axis=1).astype(dtype=np.float)  # (10, 1758)
                for iou_thresh_i, (tp, fp) in enumerate(zip(tp_sum, fp_sum)):
                    tp = np.array(tp)  # shape (1758,)
                    fp = np.array(fp)  # shape (1758,)
                    nd = len(tp)
                    rc = tp / npig
                    pr = tp / (fp + tp + np.spacing(1))  # (1758,)
                    q = np.zeros((R,))  # (101,)
                    ss = np.zeros((R,))

                    if nd:
                        recall[iou_thresh_i, label_i, arearng_i, maxdets_i] = rc[-1]
                    else:
                        recall[iou_thresh_i, label_i, arearng_i, maxdets_i] = 0

                    # numpy is slow without cython optimization for accessing elements
                    # use python array gets significant speed improvement
                    pr = pr.tolist()
                    q = q.tolist()

                    for i in range(nd - 1, 0, -1):
                        if pr[i] > pr[i - 1]:
                            pr[i - 1] = pr[i]
                    # Find the indices into a sorted array a such that, if the corresponding elements in v were inserted before the indices, the order of a would be preserved.
                    inds_by_score = np.searchsorted(rc, COCOParams.recThrs, side='left')
                    try:
                        for ri, pi in enumerate(inds_by_score):
                            q[ri] = pr[pi]
                            ss[ri] = dtScoresSorted[pi]
                    except:
                        pass
                    precision[iou_thresh_i, :, label_i, arearng_i, maxdets_i] = np.array(q)
                    scores[iou_thresh_i, :, label_i, arearng_i, maxdets_i] = np.array(ss)
    eval = {
        'counts': [T, R, K, A, M],
        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'precision': precision,
        'recall': recall,
        'scores': scores,
    }
    return eval




def summarize(acc_result, iouThr = 0.1, areaRng = 'all', maxDets = 100, ap = 1):
    iStr = ' {:<18} {} @[ IoU={:<9} | area={:>6s} | maxDets={:>3d} ] = {:0.3f}'
    typeStr = '(AP)' if ap == 1 else '(AR)'
    titleStr = 'Average Precision' if ap == 1 else 'Average Recall'
    iouStr = '{:0.2f}:{:0.2f}'.format(COCOParams.iouThrs[0], COCOParams.iouThrs[-1]) \
        if iouThr is None else '{:0.2f}'.format(iouThr)
    arearng_i = [i for i, aRng in enumerate(COCOParams.areaRngLbl) if aRng == areaRng]
    maxdets_i = [i for i, mDet in enumerate(COCOParams.maxDets) if mDet == maxDets]
    s = acc_result['precision']
    if iouThr is not None:
        t = np.where(iouThr == COCOParams.iouThrs)[0]
        s = s[t]
    #iou_thresh_i, recall_thresholds, label_i, arearng_i, maxdets_i
    s = s[:, :, :, arearng_i, maxdets_i]
    #cat_mean = [-1] * s.shape[2]
    if len(s[~np.isnan(s)]) == 0:
        mean_s = -1
        mean_by_cat = np.full((s.shape[2],),fill_value=-1)
    else:
        mean_s = np.nanmean(s)
        # for label_i in range(s.shape[2]):
        #     s_cat = s[:,:,[label_i],:]
        #     if len(s_cat[~np.isnan(s_cat)]) > 0:
        #         cat_mean[label_i] = np.nanmean(s_cat)
        mean_by_cat = np.nanmean(s, axis=(0,1,3))

    return mean_s, mean_by_cat
    #print(iStr.format(titleStr, typeStr, iouStr, areaRng, maxDets, mean_s))


if __name__ == '__main__':
    label_map = {0: 'bbox1',1:'bbox2'}
    from syncvtools.data.detections import DetectionEntity, DetectionsCollection, ImageLevelDetections
    from syncvtools.utils.data_import import TFRecords, ProdDetections
    from syncvtools.utils.data_export import COCODetectionsExport, COCOExport
    from syncvtools.utils.draw_detections import DrawDetections
    import cv2
    import syncvtools.utils.file_tools as ft
    # gts = [DetectionEntity(label_text=label_map[0], label_id=0, bbox_abs=(100,200,300,400)),
    #        DetectionEntity(label_text=label_map[1], label_id=1, bbox_abs=(300,100,400,200))]
    # dts = [DetectionEntity(label_text=label_map[0], label_id=0, bbox_abs=(105, 210, 305, 405),score=0.95),
    #        DetectionEntity(label_text=label_map[1], label_id=1, bbox_abs=(300, 100, 400, 200),score=0.85)]
    # #res = evaluateImg(dts_all=dts,gts_all=gts,aRng=COCOParams.areaRng[0])
    # evalImgs = [evaluateImg(imgKey=None,
    #                         dts_all=dts,
    #                         gts_all=gts,
    #                         catId=catId,
    #                         aRng=areaRng)
    #                  for catId in list(label_map.keys())
    #                  for areaRng in COCOParams.areaRng
    #                  ]
    # res_acc = accumulate_singleimg(evalImg_result=evalImgs, catIds=list(label_map.keys()))
    # summarize(acc_result = res_acc, iouThr=0.5)
    # summarize(acc_result=res_acc, iouThr=0.75)
    # summarize(acc_result=res_acc, iouThr=None)


    gt_obj = TFRecords.parse(tfrecord_src='/Users/apatsekin/projects/datasets/synapse/20190717_sdmv_ammo_gunparts_kix/val100.record')
    #gt_obj = gt_obj[1:4]

    COCOExport.export(gt_obj,out_json_path='/Users/apatsekin/projects/datasets/synapse/20190717_sdmv_ammo_gunparts_kix/val100_coco.json')
    #quit()
    det_obj = ProdDetections.parse(predictions_dir='/Users/apatsekin/projects/datasets/synapse/20190717_sdmv_ammo_gunparts_kix/val100_detections')
    from itertools import filterfalse

    # for img_key in det_obj:
    #     dets = []
    #     for det in det_obj[img_key].detections:
    #         if det.score > 0.15:
    #             dets.append(det)
    #     dets.append(DetectionEntity(label_text='slide',
    #                                 bbox_abs=(300,250,350,300),
    #                                 score=0.9,
    #                                 label_id=7))
    #     det_obj[img_key].detections = dets

    res_obj = gt_obj + det_obj


    # evalImgs = [evaluateImg(imgKey=imgKey,
    #                         dts_all=res_obj[imgKey].detections,
    #                         gts_all=res_obj[imgKey].ground_truth,
    #                         catId=catId,
    #                         aRng=areaRng)
    #             for catId in list(map_txt.values())
    #             for areaRng in COCOParams.areaRng
    #             for imgKey in res_obj
    #             ]
    #res_obj = res_obj[:2]


    res_obj.process_labelmap('/Users/apatsekin/projects/datasets/synapse/20190717_sdmv_ammo_gunparts_kix/label_map.pbtxt')

    drawer = DrawDetections(bbox_line_height=1, threshold=0.1)
    coco_exp = COCODetectionsExport(coco_dataset='/Users/apatsekin/projects/datasets/synapse/20190717_sdmv_ammo_gunparts_kix/val100_coco.json')
    coco_exp.export(src=res_obj,out_json_path='/Users/apatsekin/projects/datasets/synapse/20190717_sdmv_ammo_gunparts_kix/val100_coco_dets.json')
    #quit()
    for img_key in res_obj:
        img_bbox = drawer.draw_imageleveldetections(img_dets=res_obj[img_key])
        cv2.imshow('test', img_bbox)
        cv2.waitKey(1)


    # res_acc = accumulate(det_col=res_obj,
    #                      catIds=list(res_obj.label_map.values())
    #                      )
    # summarize(acc_result=res_acc, iouThr=0.5)
    # summarize(acc_result=res_acc, iouThr=0.75)
    # summarize(acc_result=res_acc, iouThr=None)
    res_obj.calculate_metrics()
    from pprint import pprint
    pprint(res_obj.detection_metrics)
    pprint(res_obj.get_counts())
    #print(res_acc)
