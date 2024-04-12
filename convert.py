import argparse
from pypdf import PdfReader
import os
import cv2

from rich.progress import (
    Progress,
    SpinnerColumn,
    TimeElapsedColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    MofNCompleteColumn,
)
from rich.console import Console

IMAGES_PATH = "./images/"

# Create directory
if not os.path.exists(IMAGES_PATH):
    os.makedirs(IMAGES_PATH)

# Set input options
parser = argparse.ArgumentParser(
    description="Convert a PDF to a MP4 (The images needs to be all the same dimensions)"
)
parser.add_argument("input", help="Path to input PDF")
parser.add_argument("output", type=str, help="Output file path and name")
parser.add_argument("fps", type=int, help="fps of the output video", default=60)
args = parser.parse_args()

# Create rich library object
console = Console()

# Open input file
reader = PdfReader(args.input)

total_pages = len(reader.pages)
count = 0

# Extracting images from pdf
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    MofNCompleteColumn(),
    TimeElapsedColumn(),
) as progress:
    task = progress.add_task("[blue]Extracting images from pdf[/]", total=total_pages)

    for page in reader.pages:
        for image in page.images:
            with open(IMAGES_PATH + str(count) + "_image.png", "wb") as fp:
                fp.write(image.data)
                count += 1
                progress.update(task, advance=1)


# Create video
images = [img for img in os.listdir(IMAGES_PATH)]
frame = cv2.imread(os.path.join(IMAGES_PATH, images[0]))
height, width, layers = frame.shape

four_cc = cv2.VideoWriter_fourcc(*"mp4v")

video = cv2.VideoWriter(args.output, four_cc, args.fps, (width, height))

if not video.isOpened():
    console.print("[red]Error: Failed to open output video file.[/]")
    exit()

# Appending images to video
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    MofNCompleteColumn(),
    TimeElapsedColumn(),
) as progress:
    task = progress.add_task("[blue]Appending images to video [/]", total=total_pages)

    for image in images:
        img_path = os.path.join(IMAGES_PATH, image)
        img = cv2.imread(img_path)
        if img is not None:
            video.write(img)
        else:
            print(f"Warning: Failed to read image file: {img_path}")
        progress.update(task, advance=1)

# Clear output and save video
os.system("rm -rf ./images/*")
cv2.destroyAllWindows()
video.release()
