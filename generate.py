# import native libraries
import os
import random
import sys

# import third party libraries
from PIL import Image

# TODO:
#  - Move config to yaml file
#  - Create interface for marking off cells
#  - Support transparency in images (currently only support RGB mode)

# ! Variables you may want to edit:
#########################################
CELL_W = 190                                     # width of each square     image will be resized
CELL_H = 165                                     # height of each square    these affect the ultimate dimensions
INPUT_DIR = 'input'                              # directory for input files (relative to current directory)
OUTPUT_DIR = 'output'                            # directory for output files (relative to current directory)
OUTPUT_PREFIX = 'bingo-card'                     # prefix for output file names (produces <PREFIX>-#.png)
FREESPACE_IMG_NAME = 'freespace.png'             # name of freespace image file
CARDS_PER_OUTPUT = 2                             # number of bingo cards on each output image
CARD_GAP = 20                                    # space between adjacent cards

# ! Thar be dragons below
#########################################
CARD_SIZE = 5
CARD_W = CELL_W*CARD_SIZE
CARD_H = CELL_H*CARD_SIZE
CANVAS_W = CARDS_PER_OUTPUT*CARD_W + (CARDS_PER_OUTPUT-1)*CARD_GAP
CANVAS_H = CARD_H
CELLS_PER_CARD = CARD_SIZE * CARD_SIZE - 1
CELLS_PER_OUTPUT = CARDS_PER_OUTPUT * CELLS_PER_CARD
ITERATIONS = int(sys.argv[1]) if len(sys.argv) > 1 else 5

OUTPUT_INDEX = None

def get_input_images():
    """Returns a list of image files from INPUT_DIR
    """
    # Get input images
    print(f"Getting files from {INPUT_DIR}{os.path.sep}...")
    input_files = os.listdir(INPUT_DIR)

    # Exit if no freespace.png
    if FREESPACE_IMG_NAME not in input_files:
        print(f"No file named {FREESPACE_IMG_NAME} in {INPUT_DIR}{os.path.sep} directory, exiting...")
        os._exit(1)

    # Get non-freespace images
    input_images = [
        os.path.join(INPUT_DIR, f)
        for f
        in input_files
        if os.path.isfile(os.path.join(INPUT_DIR, f))
        and f != FREESPACE_IMG_NAME
        and f.split('.')[-1].lower() in ('jpg', 'jpeg', 'png')
    ]

    # Exit if insufficient images
    if len(input_images) < CELLS_PER_OUTPUT:
        print(f"Too few input images ({len(input_images)}/{CELLS_PER_OUTPUT}), exiting...")
        os._exit(1)
    
    return input_images

def get_output_filename():
    """Determine output file name by checking highest index of existing output files.
    If already used, will increment OUTPUT_INDEX by 1.
    """
    global OUTPUT_INDEX
    if OUTPUT_INDEX == None:
        output_images = [
            ''.join(f.split('.')[:-1]) for f
            in os.listdir(OUTPUT_DIR)
            if os.path.isfile(os.path.join(OUTPUT_DIR, f))
            and f.startswith(OUTPUT_PREFIX)
        ]
        OUTPUT_INDEX = max([int(f.split('-')[-1]) for f in output_images]) + 1 if len(output_images) > 0 else 1
    else:
        OUTPUT_INDEX += 1

    return os.path.join(OUTPUT_DIR, f'{OUTPUT_PREFIX}-{OUTPUT_INDEX}.png')

def make_card(canvas, x, y, images):
    """Generate a card using images and paste it into canvas at x, y.
    """
    for i in range(0, 5):
        for j in range(0, 5):
            # Determine image to use
            im = None
            if i == j == 2:
                # Paste free space and do not increment
                im = Image.open(os.path.join(INPUT_DIR, FREESPACE_IMG_NAME), mode='r')
            else:
                # Paste next image
                im = Image.open(next(images), mode='r')
            
            # Resize to fit canvas
            im = im.resize(size=(CELL_W, CELL_H))

            # Determine target paste box, paste, and close
            x0 = x + i * CELL_W
            y0 = y + j * CELL_H
            x1 = x0 + CELL_W
            y1 = y0 + CELL_H
            canvas.paste(im, [x0, y0, x1, y1])
            im.close()

def main():
    # Create directories if not existing
    for dir in (INPUT_DIR, OUTPUT_DIR):
        if not os.path.exists(dir):
            print("No folder {dir}. Creating...")
            os.mkdir(dir)
            if dir == INPUT_DIR:
                print("No files in input directory. Exiting...")
                os.exit(1)

    input_images = get_input_images()

    # Create n bingo cards:
    for i in range(0, ITERATIONS):
        print(f"Producing bingo card #{i+1}...")

        # Select unique images
        chosen_images = random.sample(input_images, CELLS_PER_OUTPUT)
        images = iter(chosen_images)

        # Create a canvas
        canvas = Image.new(mode='RGB', size=(CANVAS_W, CANVAS_H), color='white')

        # Create cards
        for i in range(0, CARDS_PER_OUTPUT):
            make_card(canvas, i*(CARD_W+CARD_GAP), 0, images)

        # Save file
        output_filename = get_output_filename()
        print(f"Saving {output_filename}")
        canvas.save(output_filename)
        canvas.close()

if __name__ == "__main__":
    main()