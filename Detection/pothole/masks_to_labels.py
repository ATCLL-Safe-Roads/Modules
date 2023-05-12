import os
import numpy as np
from PIL import Image

# Define the path to the folder containing the PNG mask files
MASKS = './data/train/masks'

# Define the path to the folder where you want to save the TXT annotation files
LABELS = './data/train/labels'

# Define the class label for the object
class_label = '0'

# Iterate through all the PNG mask files in the mask folder
for mask_file in os.listdir(MASKS):
    if mask_file.endswith('.png'):
        # Load the mask image
        mask = Image.open(os.path.join(MASKS, mask_file)).convert('L')

        # Create a black and white version of the mask (only 0s and 255s)
        mask_bw = mask.point(lambda x: 0 if x < 128 else 255, '1')

        # Get the coordinates of the non-zero pixels in the mask
        nonzero_coords = np.transpose(np.nonzero(np.array(mask_bw)))

        # If the mask does not contain any objects, skip it
        if len(nonzero_coords) == 0:
            continue

        # Group the coordinates of the non-zero pixels by object ID
        object_coords = {}
        visited_coords = set()
        object_id = 1
        for i, (y, x) in enumerate(nonzero_coords):
            if (x, y) not in visited_coords:
                queue = [(x, y)]
                visited_coords.add((x, y))
                while queue:
                    x1, y1 = queue.pop(0)
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        x2, y2 = x1 + dx, y1 + dy
                        if 0 <= x2 < mask_bw.width and 0 <= y2 < mask_bw.height and (x2, y2) not in visited_coords:
                            visited_coords.add((x2, y2))
                            if mask_bw.getpixel((x2, y2)) > 0:
                                queue.append((x2, y2))
                    if object_id not in object_coords:
                        object_coords[object_id] = []
                    object_coords[object_id].append((x1, y1))
                object_id += 1

        # Collect the bounding box coordinates for each object in the mask
        bbox_coords = []
        for object_id in object_coords:
            coords = np.array(object_coords[object_id])
            x_min, y_min = np.min(coords, axis=0)
            x_max, y_max = np.max(coords, axis=0)
            bbox = [x_min, y_min, x_max, y_max]
            bbox_coords.append(bbox)

        # Convert the list of bounding box coordinates to YOLO format
        bbox_yolo = []
        for bbox in bbox_coords:
            x_center = (bbox[0] + bbox[2]) / (2 * mask_bw.width)
            y_center = (bbox[1] + bbox[3]) / (2 * mask_bw.height)
            width = (bbox[2] - bbox[0]) / mask_bw.width
            height = (bbox[3] - bbox[1]) / mask_bw.height
            if width < 0.01 or height < 0.01:
                continue
            bbox_yolo.append(f"{class_label} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        # Create the TXT annotation file path
        annotation_file = os.path.splitext(mask_file)[0] + '.txt'
        annotation_path = os.path.join(LABELS, annotation_file)

        # Write the bounding box annotations to the TXT file in YOLO format
        with open(annotation_path, 'w') as f:
            f.write('\n'.join(bbox_yolo))
