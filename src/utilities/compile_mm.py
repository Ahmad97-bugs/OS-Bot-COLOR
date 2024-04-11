from cvbot.io import read_img, save_img
from cvbot.images import Image
from cvbot.match import mse
import numpy as np
from pathlib import Path
import os

__PATH = Path(__file__).parent.parent
IMAGES = __PATH.joinpath("images")
BOT_IMAGES = IMAGES.joinpath("bot")
reg = (26, 21, 104, 92)


def process(img):
    """
    Image -> Image
    Remove noise from nex minimap image
    and return a clean image
    """
    global reg
    cimg = img.crop(reg)
    mask = np.logical_and(cimg.img[:, :, 1] < 30, cimg.img[:, :, 0] > 150)
    cimg.img[mask] = np.array((200, 200, 200), dtype=cimg.img.dtype)
    maskb = np.logical_and(cimg.img[:, :, 2] > 80, cimg.img[:, :, 0] < 150)
    cimg.img[maskb] = np.array((200, 200, 200), dtype=cimg.img.dtype)
    cimg.img[cimg.img > 200] = 200
    cimg.show()
    return cimg


def compile():
    images_path = os.path.join(BOT_IMAGES, 'minimap')
    fmap = read_img(f'{images_path}/image0.png')
    fmap.name = "full_map"
    # Using our processing function, process the first image
    fmap = process(fmap)
    lpos = 0, 0

    # We're going to measure how long it will take to compile the whole map
    for i in range(0, 7):
        # Load first two images
        imga = process(read_img(f"{images_path}/image{i}.png"))
        imgb = process(read_img(f"{images_path}/image{i+1}.png"))

        # Create and black image similar size to cropped minimap
        # with extra 2 horizontal and vertical padding
        timg = Image(np.zeros((96, 108, 3), dtype=imga.img.dtype))
        # Draw the first image into the middle of the black image
        # This will look as image a but with black padding around it
        atimg = timg.draw_img(imga, (2, 2))
        atimg.name = "at"

        # Here we will compare the padded atimg with the second image
        # where we draw it to varying parts ranging from x 0 y 0
        # upto x 4 y 4, we will compare each drawn position
        best = (None, None)
        for j in range(5):
            for k in range(5):
                # Draw second image into the black image
                btimg = timg.draw_img(imgb, (j, k))
                # Add black padding around
                btimg.img[:2, :, :] = 0
                btimg.img[:, :2, :] = 0
                btimg.img[-2:, :, :] = 0
                btimg.img[:, -2:, :] = 0
                # Image name
                btimg.name = "bt"

                # Compare using mean squared error, if the error is low
                # this will return a number indicating the difference between the two
                res = mse(atimg, btimg)

                # we're looking for the lowest difference and not a specific number
                if best[0] is None or res < best[0]:
                    # Save the location of the best match(-2 because of the padding)
                    best = (res, (j - 2, k - 2))

        # This is the position of where to draw the current
        # second image in the full map image
        lx, ly = best[1][0] + lpos[0], best[1][1] + lpos[1]
        # lpos tracks the current position of the image we're comparing to
        # so we can keep drawing without losing track of where to draw
        lpos = 0 if lx < 0 else lx, 0 if ly < 0 else ly
        fmap = fmap.draw_img(imgb, (lx, ly))
        fmap.show()
        print(i)

    fmap.show()
    save_img(fmap, f"{images_path}/fmap.png")


if __name__ == "__main__":
    compile()
