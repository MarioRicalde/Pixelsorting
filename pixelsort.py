from PIL import Image
import argparse
import os
import random
import sys
import time
import socket

import arrow
import psutil
import requests

import interval
import sorter
import sorting
import util
import reading


def clear():
    return os.system('cls' if os.name == 'nt' else 'clear')


def has_internet(host="8.8.8.8", port=53, timeout=3):
    """
    host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        print(ex)
        return False


def main():
    clear()

    print("Pixel sorting based on web hosted images.\nThe output image is uploaded to put.re/imgur after being sorted.\n"+(35*'--') +
          "\nTo see any past runs, args used, and the result\nopen 'output.txt'\n"+(35*'--')+"\nThanks for using this program!\nPress any key to continue...")
    input()
    clear()

    internet = has_internet()

    if internet:
        url_input = input(
            "Please input the URL of the image or the default image #:\n(this might take a while depending the image resolution)\n")
        url, url_given, url_random, random_url = reading.read_image_input(
            url_input, internet)
        input_img = Image.open(requests.get(url, stream=True).raw)
    else:
        print("Internet not connected! Local image must be used.")
        image_input = input(
            "Please input the location of the local file (default image in images folder):\n")
        image_path, url_given, url_random, random_url = reading.read_image_input(
            image_input, internet)
        input_img = Image.open(image_path)
        url = image_path

    width, height = input_img.size
    resolution_msg = "Resolution: "+str(width)+"x"+str(height)
    image_msg = (("[WARNING] No image url given, using " + ("random" if url_random else "chosen") + " default image " +
                  (random_url if url_random else str(url_input))) if not url_given else "Using given image ")
    clear()

    # preset input
    print(image_msg+"\n"+resolution_msg)
    preset_q = input("\nDo you wish to apply a preset? (y/n)\n")
    clear()
    if preset_q in ['y', 'yes', '1']:
        print("Preset options:\n-1|main -- Main args (r 50, c 250, a 45, random, intensity)\n-2|full random -- Randomness in every arg!\n-3|snap-sort -- Run from it, dread it, destiny still arrives.")
        preset_input = input("\nChoice: ").lower()
        preset_options = ['main', 'full random', 'snap-sort']
        if preset_input in preset_options:
            preset_choices = {
                'main': '1',
                'full random': '2',
                'snap-sort': '3'
            }
            preset_input = preset_choices[preset_input]
        if preset_input in ['1', '2', '3']:
            preset_input = {
                '1': 'main',
                '2': 'full random',
                '3': 'snap-sort'
            }[preset_input]
        # if presets are applied, they take over args
        arg_parse_input, int_func_input, sort_func_input, preset_true, int_rand, sort_rand, shuffled, snapped = reading.read_preset(
            preset_input)
    else:
        preset_true = False
    clear()

    # int func, sort func
    if not preset_true:
        # int func input
        print(image_msg+"\n"+resolution_msg)
        print("\nWhat interval function are you using?\nOptions (default is random):\n-1|random\n-2|threshold\n-3|edges\n-4|waves\n-5|snap\n-6|shuffle-total\n-7|shuffle-axis\n-8|file\n-9|file-edges\n-10|none\n-11|random select")
        int_func_input = input("\nChoice: ").lower()
        int_func_options = ["random", "threshold", "edges", "waves", "snap",
                            "shuffle-total", "shuffle-axis", "file", "file-edges", "none"]
        if int_func_input in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
            int_func_input = {
                '1': 'random',
                '2': 'threshold',
                '3': 'edges',
                '4': 'waves',
                '5': 'snap',
                '6': 'shuffle-total',
                '7': 'shuffle-axis',
                '8': 'file',
                '9': 'file-edges',
                '10': 'none'
            }[int_func_input]
            int_rand = False
        elif int_func_input in ['11', 'random select']:
            int_func_input = int_func_options[random.randint(0, 3)]
            int_rand = True
        shuffled = True if int_func_input in [
            'shuffle-total', 'shuffle-axis'] else False
        snapped = True if int_func_input in ['snap'] else False

        int_msg = ("Interval function: " if not int_rand else "Interval function (randomly selected): ") + \
            int_func_input if int_func_input in int_func_options else "Interval function: random (default)"
        clear()

        # sort func input
        print(image_msg+"\n"+int_msg+"\n"+resolution_msg)
        print("\nWhat sorting function are you using?\nOptions (default is lightness):\n-1|lightness\n-2|hue\n-3|intensity\n-4|minimum\n-5|saturation\n-6|random select")
        sort_func_input = input("\nChoice: ").lower()
        sort_func_options = ["lightness", "hue",
                             "intensity", "minimum", "saturation"]
        if sort_func_input in ['1', '2', '3', '4', '5']:
            sort_func_input = {
                '1': 'lightness',
                '2': 'hue',
                '3': 'intensity',
                '4': 'minimum',
                '5': 'saturation'
            }[sort_func_input]
            sort_rand = False
        elif sort_func_input in ['6', 'random select']:
            sort_func_input = sort_func_options[random.randint(0, 4)]
            sort_rand = True
        else:
            sort_rand = False
        sort_rand is False if sort_func_input in ['1', '2', '3', '4', '5', "lightness", "hue", "intensity", "minimum", "saturation"] else (
            sort_rand is True if sort_func_input in ['6', 'random select'] else False)
        sort_msg = ("Sorting function: " if not sort_rand else "Sorting function (randomly selected): ") + \
            sort_func_input if sort_func_input in sort_func_options else "Sorting function: lightness (default)"
        clear()

    # int func msg, sort func msg
    if preset_true:
        int_msg = ("Interval function: " if not int_rand else "Interval function (randomly selected): ") + int_func_input if int_func_input in [
            "random", "threshold", "edges", "waves", "file", "file-edges", "none"] else "Interval function: random (default)"

        sort_msg = ("Sorting function: " if not sort_rand else "Sorting function (randomly selected): ") + sort_func_input if sort_func_input in [
            "lightness", "hue", "intensity", "minimum", "saturation"] else "Sorting function: lightness (default)"

    # hosting site
    if internet:
        site_input = input(
            "Upload site:\n-1|put.re (recommended)\n-2|imgur.com\n")
        if site_input in ["1", "2"]:
            site_input = {
                "1": "put.re",
                "2": "imgur"
            }
        site_input = reading.read_site(site_input)
        site_msg = ("Image host site: " + site_input)
        output_image_path = "image.png"
    else:
        print("Internet not connected! Image will be saved locally.")
        file_name = input(
            "Name of output file (leave empty for randomized name):\n(do not include the file extension, .png will always be used.)\n")
        output_image_path = (util.id_generator()+".png") if file_name in [
            '', ' '] else file_name
        site_msg = ("Internet not connected, saving locally as " +
                    output_image_path)
        site_input = "This isn't needed, but will break if not present."
    clear()

    # args
    if not preset_true:
        needs_help = input("Do you need help with args? (y/n)\n")
        clear()
        if needs_help in ['y', 'yes', '1']:
            print(image_msg+"\n"+resolution_msg+"\n"+int_msg+"\n"+sort_msg+"\n"+site_msg +
                  "\n\nWhat args will you be adding?\n" +
                  '{:21}'.format("Parameter") + '{:>6}'.format("| Flag |") + '{:>12}'.format("Description") + "\n" +
                  '{:21}'.format("---------------------") + '{:>6}'.format("|------|") + '{:>12}'.format("------------") + "\n" +
                  '{:21}'.format("Randomness") + '{:>6}'.format("| -r   |") + "What percentage of intervals not to sort. 0 by default." + "\n" +
                  '{:21}'.format("Char. length") + '{:>6}'.format("| -c   |") + "Characteristic length for the random width generator.\n" + 29 * ' ' + "Used in mode random." + "\n" +
                  '{:21}'.format("Angle") + '{:>6}'.format("| -a   |") + "Angle at which you're pixel sorting in degrees. 0 (horizontal) by default." + "\n" +
                  '{:21}'.format("Threshold (lower)") + '{:>6}'.format("| -t   |") + "How dark must a pixel be to be considered as a 'border' for sorting?\n" + 29 * ' ' + "Takes values from 0-1. 0.25 by default. Used in edges and threshold modes." + "\n" +
                  '{:21}'.format("Threshold (upper)") + '{:>6}'.format("| -u   |") + "How bright must a pixel be to be considered as a 'border' for sorting?\n"+29*' '+"Takes values from 0-1. 0.8 by default. Used in threshold mode.")
        else:
            print(image_msg+"\n"+resolution_msg+"\n"+int_msg+"\n"+sort_msg+"\n"+site_msg +
                  "\n\nWhat args will you be adding?\n" +
                  '{:21}'.format("Parameter") + '{:>6}'.format("| Flag |") + "\n" +
                  '{:21}'.format("---------------------") + '{:>6}'.format("|------|") + "\n" +
                  '{:21}'.format("Randomness") + '{:>6}'.format("| -r   |") + "\n" +
                  '{:21}'.format("Char. length") + '{:>6}'.format("| -c   |") + "\n" +
                  '{:21}'.format("Angle") + '{:>6}'.format("| -a   |") + "\n" +
                  '{:21}'.format("Threshold (lower)") + '{:>6}'.format("| -t   |") + "\n" +
                  '{:21}'.format("Threshold (upper)") + '{:>6}'.format("| -u   |"))
        arg_parse_input = input("\n\nArgs: ")
        clear()

    # args
    p = argparse.ArgumentParser(description="pixel mangle an image")
    p.add_argument("-t", "--bottom_threshold", type=float,
                   help="Pixels darker than this are not sorted, between 0 and 1", default=0.25)
    p.add_argument("-u", "--upper_threshold", type=float,
                   help="Pixels darker than this are not sorted, between 0 and 1", default=0.8)
    p.add_argument("-c", "--clength", type=int,
                   help="Characteristic length of random intervals", default=50)
    p.add_argument("-a", "--angle", type=float,
                   help="Rotate the image by an angle (in degrees) before sorting", default=0)
    p.add_argument("-r", "--randomness", type=float,
                   help="What percentage of intervals are NOT sorted", default=15)

    # add a space in front of arg parse unless there is one or none was entered
    arg_parse_input = None if (arg_parse_input in [
                               '', ' '] or arg_parse_input[0] == ' ') else (' ' + arg_parse_input)

    if arg_parse_input is not None:
        args_in = arg_parse_input.split(' -')
        args_in[:] = ['-'+x for x in args_in]
        args_in.pop(0)
    else:
        print("No args given")
        args_in = ""

    __args = p.parse_args(args_in)

    interval_function = reading.read_interval_function(int_func_input)
    sorting_function = reading.read_sorting_function(sort_func_input)
    angle = __args.angle
    randomness = __args.randomness

    # remove old image files that didn't get deleted before
    if os.path.isfile(output_image_path):
        print("Detected old files...")
        os.remove(output_image_path)
        print("Removed old files!")
        clear()

    print(image_msg+"\n"+resolution_msg+"\n"+("Preset: " +
                                              preset_input if preset_true else "No preset applied")+"\n"+int_msg+"\n"+sort_msg+"\n"+site_msg)

    # even if they were never given, at some point they need to be assigned to default values properly
    if int_func_input in ['', ' ']:
        int_func_input = 'random'
    if sort_func_input in ['', ' ']:
        sort_func_input = 'lightness'

    if int_func_input in ["threshold", "edges", "file-edges"]:
        print("Lower threshold: ", __args.bottom_threshold)
    if int_func_input == "threshold":
        print("Upper threshold: ", __args.upper_threshold)
    if int_func_input in ["random", "waves"]:
        print("Characteristic length: ", __args.clength)
    print("Randomness: ", __args.randomness, "%")
    print("Angle: ", __args.angle, "°")
    print("------------------------------")

    print("Opening image...")

    print("Converting to RGBA...")
    input_img.convert('RGBA')

    print("Rotating image...")
    input_img = input_img.rotate(angle, expand=True)

    print("Getting data...")
    data = input_img.load()

    print("Getting pixels...")
    pixels = []
    append = pixels.append
    size1 = input_img.size[1]
    size0 = input_img.size[0]

    for y in range(size1):
        append([])
        for x in range(size0):
            pixels[y].append(data[x, y])

    if shuffled or snapped:
        if snapped:
            print("Determining intervals...")
            intervals = interval.random(pixels, __args, url)
            sorted_pixels = sorter.sort_image(
                pixels, intervals, randomness, sorting_function)
            print("Run from it. Dread it. Destiny still arrives.")
            thanos_img = Image.new('RGBA', input_img.size)
            size1 = thanos_img.size[1]
            size0 = thanos_img.size[0]
            for y in range(size1):
                for x in range(size0):
                    thanos_img.putpixel((x, y), sorted_pixels[y][x])
            thanos_img.save("thanos_img.png")
            print("Remembering those that sacrificed it all...")

            sorted_pixels = interval_function(intervals, __args, url)
        else:
            print("Determining intervals...")
            sorted_pixels = interval_function(pixels, __args, url)
    else:
        print("Determining intervals")
        intervals = interval_function(pixels, __args, url)
        print("Sorting pixels...")
        sorted_pixels = sorter.sort_image(
            pixels, intervals, randomness, sorting_function)

    print("Placing pixels in output image...")
    output_img = Image.new('RGBA', input_img.size)
    size1 = output_img.size[1]
    size0 = output_img.size[0]
    for y in range(size1):
        for x in range(size0):
            output_img.putpixel((x, y), sorted_pixels[y][x])

    if angle is not 0:
        print("Rotating output image back to original orientation...")
        output_img = output_img.rotate(360-angle, expand=True)

        print("Crop image to apropriate size...")
        output_img = util.crop_to(output_img, url, internet)

    print("Saving image...")
    output_img.save(output_image_path)

    if internet:
        # choose upload site
        date_time = str(arrow.utcnow().format('MM-DD-YYYY HH:mm'))
        # upload sites
        if site_input is "imgur":
            import pyimgur
            CLIENT_ID = "d7155a81c1e37bd"
            PATH = output_image_path

            out_msg = "\nStarting image url: "+url+("\nInt func: " if not int_rand else "\nInt func (randomly chosen): ")+int_func_input+(
                "\nSort func: " if not sort_rand else "\nSort func (randomly chosen): ")+sort_func_input+"\nArgs: "+(arg_parse_input if arg_parse_input is not None else "No args")+"\nSorted on: "+date_time
            im = pyimgur.Imgur(CLIENT_ID)
            uploaded_image = im.upload_image(
                PATH, title="Pixel sorted", description=out_msg)
            link = uploaded_image.link
            print("Image uploaded!")
        else:
            import json
            print("Uploading...")
            r = requests.post('https://api.put.re/upload',
                              files={'file': ('image.png', open('image.png', 'rb'))})
            output = json.loads(r.text)
            link = output["data"]["link"]
            print("Image uploaded!")

        # delete old file, seeing as its uploaded
        print("Removing local file...")
        os.remove(output_image_path)

        # output to 'output.txt'
        print("Saving config to 'output.txt'...")
        with open("output.txt", "a") as f:
            f.write("\nStarting image url: "+url+"\n"+resolution_msg+("\nInt func: " if not int_rand else "\nInt func (randomly chosen): ")+int_func_input+("\nSort func: " if not sort_rand else "\nSort func (randomly chosen): ") +
                    sort_func_input+"\nArgs: "+(arg_parse_input if arg_parse_input is not None else "No args")+"\nSorted on: "+date_time+"\n\nSorted image: "+link+"\n"+(35*'-'))

        print("Done!")
        print("Link to image: " + link)
    else:
        print("Not saving config to 'output.txt', as there is no internet.")
        print("Done!")
    output_img.show()


if __name__ == "__main__":
    main()
