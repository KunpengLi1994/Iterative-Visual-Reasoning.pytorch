from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import os.path as osp
from random import shuffle
import PIL.Image as Image
import PIL.ImageColor as ImageColor
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont


STANDARD_COLORS = [
    'AliceBlue', 'Chartreuse', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque',
    'BlanchedAlmond', 'BlueViolet', 'BurlyWood', 'CadetBlue', 'AntiqueWhite',
    'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan',
    'DarkCyan', 'DarkGoldenRod', 'DarkGrey', 'DarkKhaki', 'DarkOrange',
    'DarkOrchid', 'DarkSalmon', 'DarkSeaGreen', 'DarkTurquoise', 'DarkViolet',
    'DeepPink', 'DeepSkyBlue', 'DodgerBlue', 'FireBrick', 'FloralWhite',
    'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod',
    'Salmon', 'Tan', 'HoneyDew', 'HotPink', 'IndianRed', 'Ivory', 'Khaki',
    'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue',
    'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGray', 'LightGrey',
    'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue',
    'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 'Lime',
    'LimeGreen', 'Linen', 'Magenta', 'MediumAquaMarine', 'MediumOrchid',
    'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen',
    'MediumTurquoise', 'MediumVioletRed', 'MintCream', 'MistyRose', 'Moccasin',
    'NavajoWhite', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed',
    'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed',
    'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple',
    'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Green', 'SandyBrown',
    'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue',
    'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 'SteelBlue', 'GreenYellow',
    'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White',
    'WhiteSmoke', 'Yellow', 'YellowGreen'
]

NUM_COLORS = len(STANDARD_COLORS)
this_dir = osp.dirname(__file__)

try:
    FONT = ImageFont.truetype(osp.join(this_dir, '..', '..', 'data', 'helveticaneue.ttf'), 12)
except IOError:
    FONT = ImageFont.load_default()

try:
    FONT_BIG = ImageFont.truetype(osp.join(this_dir, '..', '..', 'data', 'helveticaneue.ttf'), 24)
except IOError:
    FONT_BIG = ImageFont.load_default()


def _draw_single_box(image, xmin, ymin, xmax, ymax, display_str, font, color='black', color_text='black', thickness=2):
    draw = ImageDraw.Draw(image)
    (left, right, top, bottom) = (xmin, xmax, ymin, ymax)
    draw.line([(left, top), (left, bottom), (right, bottom),
               (right, top), (left, top)], width=thickness, fill=color)
    text_bottom = bottom
    # Reverse list and print from bottom to top.
    text_width, text_height = font.getsize(display_str)
    margin = np.ceil(0.05 * text_height)
    draw.rectangle(
        [(left, text_bottom - text_height - 2 * margin), (left + text_width,
                                                          text_bottom)],
        fill=color)
    draw.text(
        (left + margin, text_bottom - text_height - margin),
        display_str,
        fill=color_text,
        font=font)

    return image


def draw_gt_boxes(image, gt_boxes):
    num_boxes = gt_boxes.shape[0]
    disp_image = Image.fromarray(np.uint8(image[0]))

    list_gt = range(num_boxes)
    shuffle(list_gt)
    for i in list_gt:
        this_class = int(gt_boxes[i, 4])
        disp_image = _draw_single_box(disp_image,
                                      gt_boxes[i, 0],
                                      gt_boxes[i, 1],
                                      gt_boxes[i, 2],
                                      gt_boxes[i, 3],
                                      '%s' % (cfg.CLASSES[this_class]),
                                      FONT,
                                      color=STANDARD_COLORS[this_class % NUM_COLORS])

    new_image = np.empty_like(image)
    new_image[0, :] = np.array(disp_image)
    return new_image


def draw_predicted_boxes(image, scores, gt_boxes, labels=None):
    disp_image = Image.fromarray(np.uint8(image[0]))
    num_boxes = gt_boxes.shape[0]
    preds = np.argmax(scores, axis=1)
    if labels is None:
        labels = gt_boxes[:, 4]

    list_gt = range(num_boxes)
    shuffle(list_gt)
    for i in list_gt:
        this_class = int(labels[i])
        pred_class = preds[i]
        this_conf = scores[i, this_class]
        pred_conf = scores[i, pred_class]
        this_text = '%s|%.2f' % (cfg.CLASSES[this_class], this_conf)
        if this_class != pred_class:
            this_text += '(%s|%.2f)' % (cfg.CLASSES[pred_class], pred_conf)
        elif this_class == 0:
            this_text = '(X)'
        disp_image = _draw_single_box(disp_image,
                                      gt_boxes[i, 0],
                                      gt_boxes[i, 1],
                                      gt_boxes[i, 2],
                                      gt_boxes[i, 3],
                                      this_text,
                                      FONT,
                                      color=STANDARD_COLORS[this_class % NUM_COLORS])

    new_image = np.empty_like(image)
    new_image[0, :] = np.array(disp_image)
    return new_image


def draw_predicted_boxes_attend(image, scores, gt_boxes, attend, weight=None):
    disp_image = Image.fromarray(np.uint8(image[0]))
    num_boxes = gt_boxes.shape[0]
    preds = np.argmax(scores, axis=1)
    labels = gt_boxes[:, 4]

    list_gt = range(num_boxes)
    shuffle(list_gt)
    for i in list_gt:
        this_class = int(labels[i])
        pred_class = preds[i]
        this_conf = scores[i, this_class]
        pred_conf = scores[i, pred_class]
        this_text = '%.2f&' % attend[i, 0]
        if weight is not None:
            this_text += '%.2f&' % (weight[i] * num_boxes)
        this_text += '%s|%.2f' % (cfg.CLASSES[this_class], this_conf)
        if this_class != pred_class:
            this_text += '(%s|%.2f)' % (cfg.CLASSES[pred_class], pred_conf)
        elif this_class == 0:
            this_text = '(X)'
        disp_image = _draw_single_box(disp_image,
                                      gt_boxes[i, 0],
                                      gt_boxes[i, 1],
                                      gt_boxes[i, 2],
                                      gt_boxes[i, 3],
                                      this_text,
                                      FONT,
                                      color=STANDARD_COLORS[this_class % NUM_COLORS])

    new_image = np.empty_like(image)
    new_image[0, :] = np.array(disp_image)
    return new_image


def draw_predicted_boxes_test(image, scores, gt_boxes, args):
    # print('image shape', image[0].shape)
    image = image[0]
    if args.caffe is not None:
        image += np.array([[[103.939, 116.779, 123.68]]])
    else:
        image = image[:, :, ::-1]  # RGB to BGR
        image *= np.array([[[0.229, 0.224, 0.225]]])  # multiply by stddev
        image += np.array([[[0.485, 0.456, 0.406]]])  # plus mean
        image *= 255.  # Convert range to [0,255]

    disp_image = Image.fromarray(np.uint8(image))
    num_boxes = gt_boxes.shape[0]
    # Avoid background class
    preds = np.argmax(scores[:, 1:], axis=1) + 1
    wrong = False
    list_gt = range(num_boxes)
    shuffle(list_gt)
    for i in list_gt:
        this_class = int(gt_boxes[i, 4])
        pred_class = preds[i]
        this_conf = scores[i, this_class]
        pred_conf = scores[i, pred_class]
        if this_class != pred_class:
            this_text = '%s|%.2f' % (args.CLASSES[this_class], this_conf)
            this_text += '(%s|%.2f)' % (args.CLASSES[pred_class], pred_conf)
            wrong = True
        else:
            # this_text = '(X)'
            this_text = '%s|%.2f' % (args.CLASSES[this_class], this_conf)
        disp_image = _draw_single_box(disp_image,
                                      gt_boxes[i, 0],
                                      gt_boxes[i, 1],
                                      gt_boxes[i, 2],
                                      gt_boxes[i, 3],
                                      this_text,
                                      FONT,
                                      color=STANDARD_COLORS[this_class % NUM_COLORS])

    new_image = np.array(disp_image)
    return new_image, wrong


def draw_memory(mem, scale=1.0):
    # Set the boundary
    mem_image = np.minimum(np.mean(np.absolute(mem.squeeze(axis=0)), axis=2) * (255. / scale), 255.)
    # Just visualization
    mem_image = np.tile(np.expand_dims(mem_image, axis=2), [1, 1, 3])

    return mem_image[np.newaxis]


def draw_weights(mem, scale=1.0):
    # Set the boundary
    mem_image = np.minimum(np.mean(np.absolute(mem.squeeze(axis=0)), axis=2) * (255. / scale), 255.)
    # Just visualization
    mem_image = np.tile(np.expand_dims(np.uint8(mem_image), axis=2), [1, 1, 3])

    return mem_image[np.newaxis]
