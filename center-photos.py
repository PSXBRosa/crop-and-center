import os
import math
import argparse
import threading

from Logger import Logger
from Picture import Picture

parser = argparse.ArgumentParser()
parser.add_argument("--folder", type=str, default=os.getcwd(), help="Folder to batch resize")
parser.add_argument("--size", type=str, default="512x512", help="Size to resize into, \"wxh\" ")
parser.add_argument("--generate", type=bool, default=False, help="If true, it'll generate new images containing the cropped down, zoomed in and aligned faces")
parser.add_argument("--ignore", type=bool, default=True, help="If true, it'll skip over non-image files and not raise errors")
parser.add_argument("--dumpfolder", type=str, default=".\output", help="Path to the output folder, if there isn't one with that name it'll be created")
flags = parser.parse_args()
script_dir_path = os.path.dirname(os.path.realpath(__file__))

def main(log):
    
    working_directory = flags.folder
    out_dir = os.path.join(working_directory, flags.dumpfolder)
    try:
        os.mkdir(out_dir)
    except FileExistsError:
        pass
    
    for path in os.listdir(working_directory):
        log.set_file(path)
        if not os.path.isfile(path):
            continue

        abs_path = os.path.join(working_directory, path)
        try:
            curr = Picture(abs_path)
        except AssertionError:
            if not flags.ignore:
                raise TypeError(f"The program was unable to read the following file: {path}, if you'd wish to keep the program running when there are non-image files\
                                  in the folder, it's advised to set --ignore to true.")
            continue

        # extracts and type casts each dimention in the prompt
        w,h = (int(dim) for dim in flags.size.split("x"))

        # if at least one original dimention is smaller than its target
        if any((curr.w < w, curr.h < h)):
            # gets the value that maximizes the resizing scale
            scale = max(w/curr.w, h/curr.h)
            # resizes the image
            w1, h1 = int(scale*curr.w), int(scale*curr.h)
            curr.resize(w1,h1)
        
        ############## NOTE ################################
        # STEP 1 > FINDS FACE
        # STEP 2 > CREATES NEW FACE IMAGE IF FLAGGED
        # STEP 3 > CROPS THE BIGGEST SQUARE AROUND THE FACE
        # STEP 4 > RESIZES CROPPED IMAGE TO DESIRED SIZE
        ####################################################

        # Step 1
        log.set_oper("Finding faces")
        face_data = curr.find_face()
        for i, (eyes, fcx, fcy, fw, fh) in enumerate(face_data):
            log.set_oper("Creating zoomed in images")
            # Step 2
            if flags.generate:
                face_pic = curr.copy()
                
                # finds best rotation angle
                (eye1x, eye1y), (eye2x, eye2y) = eyes[:2] # if for some reason there are three or more eyes in a given face
                alpha = math.atan(abs((eye1y - fcy)/(fcx - eye1x))) # since all the angles inside the triangle should be less than 180deg, the tans are never negative 
                beta  = math.atan(abs((eye2y - fcy)/(fcx - eye2x)))
                rotating_angle = (math.pi - alpha + beta)/2

                # crops, rotates and saves
                face_pic.crop((fcx, fcy), fh, fw) # FIXME # Better than cropping and then rotating, it's to rotate and then crop (by applying the rotation matrix to the cropping window)
                face_pic.rotate((fcx, fcy), rotating_angle) # FIXME # Generating weird sized images.
                face_pic.save(os.path.join(out_dir, f"{path}[close-up-face-idx-{i}].jpg"))

            # Steps 3 and 4
            log.set_oper("Cropping and resizing images")
            cp = curr.copy()
            crop_dim = min(fcx, fcy, cp.w-fcx, cp.h-fcy)
            cp.crop((fcx, fcy), crop_dim*2, crop_dim*2)
            cp.resize(w, h)
            cp.save(os.path.join(out_dir, f"{path}[centered-face-idx-{i}].jpg"))

    log.set_oper("All done!")
    log.done = True

if __name__=="__main__":
    log = Logger()
    log.start()
    t = threading.Thread(target=main, args=[log])
    t.start()