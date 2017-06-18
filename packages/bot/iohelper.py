import os
import subprocess
import logging

__author__ = "anaeanet"


def create_folder(folder_name):

    logger = logging.getLogger("pelicanblogbot").getChild("packages.bot.iohelper.create_folder")
    result = False

    try:
        os.makedirs(folder_name)
        result = True
    except (OSError, IOError) as exception:
        import errno
        if exception.errno == errno.EEXIST:
            result = True
        else:
            logger.exception("Creation of folder '" + folder_name + "' failed")
    finally:
        return result


def write_to_file(file_name, write_mode, file_content):
    logger = logging.getLogger("pelicanblogbot").getChild("packages.bot.iohelper.write_to_file")
    result = False

    try:
        with open(file_name, write_mode) as post_file:
            post_file.write(file_content)
        result = True
    except (OSError, IOError) as e:
        logger.exception("Writing of file '" + file_name + "' failed: " + file_content)
    finally:
        return result


def transfer_file(source, target):
    return subprocess.call(["rsync", "-rtvhPq", "--delete", source, target]) == 0


def remove_file(path_to_file):
    server = None
    path = path_to_file

    if ":" in path:
        server, path = path.split(":", 1)

    if server is not None:
        removal_successful = subprocess.call(["ssh", server, "'rm -rf " + path + "'"]) == 0
    else:
        removal_successful = subprocess.call(["rm", "-rf", path]) == 0

    return removal_successful

