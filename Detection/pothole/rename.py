import os

IMAGES = './data/train/images'
MASKS = './data/train/masks'


def main():
    # Rename images
    for i, filename in enumerate(os.listdir(IMAGES)):
        os.rename(os.path.join(IMAGES, filename), os.path.join(IMAGES, str(i) + '.png'))

    # Rename masks
    for i, filename in enumerate(os.listdir(MASKS)):
        os.rename(os.path.join(MASKS, filename), os.path.join(MASKS, str(i) + '.png'))


if __name__ == '__main__':
    main()
