#!/usr/bin/env python3
import rosbag
import os
import sys
from pathlib import Path
import cv2
import numpy as np
import argparse
import shutil

def read_images_from_bag(bag, topic, output_folder, is_compressed=False, step = 10, is_show=False):
    print(f"Read images from topic {topic} is compressed {is_compressed} step {step} output folder {output_folder}")
    count = 0
    c = 0
    for topic, msg, t in bag.read_messages(topics=[topic]):
        if is_compressed:
            # print(type(msg.data))
            if count % step == 0:
                image_buf = np.asarray(bytearray(msg.data), dtype="uint8")
                image = cv2.imdecode(image_buf, cv2.IMREAD_COLOR)
                if is_show:
                    cv2.imshow(topic, image)
                    cv2.waitKey(1)
                image_gray =  cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
                cv2.imwrite(output_folder+f"img_{count}.jpg", image_gray, [cv2.IMWRITE_JPEG_QUALITY, 90])
                # with open(output_folder+f"img_{c}.jpg", 'wb') as filehandle:
                    # filehandle.write(msg.data)
                c += 1
            count += 1
    print(f" {c} images written", c)
    return count

if __name__ == "__main__":
    #print(sys.argv[0])
    parser = argparse.ArgumentParser(description='Calib bag')
    parser.add_argument('bagname', metavar='bagname', type=str,help="Bag path")
    parser.add_argument('-l', "--left", nargs='?', const=True, default=False, type=bool)
    parser.add_argument('-r', "--right", nargs='?', const=True, default=False, type=bool)
    parser.add_argument('-v', "--show", nargs='?', const=True, default=False, type=bool)
    parser.add_argument('-p', "--plot", nargs='?', const=True, default=False, type=bool)
    parser.add_argument('-s','--step', type=int, default=5, help='step for images')
    args = parser.parse_args()

    bag_path = sys.argv[1]
    dir_path = os.path.basename(os.path.realpath(bag_path))

    print("Read bag from", bag_path)
    output_folder_l = "/tmp/" + dir_path + "/output_left_images/"
    output_folder_r = "/tmp/" + dir_path + "/output_right_images/"
    print("Output images will store at", output_folder_l, "and", output_folder_r, f"enable {args.left} {args.right}")
    try:
        shutil.rmtree(output_folder_l)
        shutil.rmtree(output_folder_r)
    except:
        pass
    Path(output_folder_l).mkdir(parents=True, exist_ok=True)
    Path(output_folder_r).mkdir(parents=True, exist_ok=True)
    bag = rosbag.Bag(bag_path)

    if args.left or ( not args.left and not args.right):
        read_images_from_bag(bag, "/stereo/left/image_compressed", output_folder_l, is_compressed=True, is_show=args.plot, step = args.step)
        os.system(f'rosrun camera_model Calibration --camera-name left --input {output_folder_l} -p img -e jpg -w 12 -h 8 --size 80 --camera-model myfisheye --opencv false --view-results {args.show}')
    
    if args.right or ( not args.left and not args.right):
        read_images_from_bag(bag, "/stereo/right/image_compressed", output_folder_r, is_compressed=True, is_show=args.plot, step = args.step)
        os.system(f'rosrun camera_model Calibration --camera-name right --input {output_folder_r} -p img -e jpg -w 12 -h 8 --size 80 --camera-model myfisheye --opencv false --view-results {args.show}')
