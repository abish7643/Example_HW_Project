import logging
import aiofiles
import aiofiles.os
import json


async def copy_file(src=None, dst=None):
    if not src or not dst:
        return

    try:
        # create file objects for the source and destination
        handle_src = await aiofiles.open(src, mode='r')
        handle_dst = await aiofiles.open(dst, mode='w')

        # get the number of bytes for the source
        stat_src = await aiofiles.os.stat(src)
        n_bytes = stat_src.st_size

        # get the file descriptors for the source and destination files
        fd_src = handle_src.fileno()
        fd_dst = handle_dst.fileno()

        # copy the file
        await aiofiles.os.sendfile(fd_dst, fd_src, 0, n_bytes)
    except Exception as e:
        logging.error(f"[COPY] Error copying file: {e}")


async def read_config(config_file="config.json"):
    """
    Reads the configuration from the config file.
    :param config_file:
    :return:
    """
    try:
        async with aiofiles.open(config_file, mode="r") as file:
            _config = await file.read()
            _config = json.loads(_config)
        return _config
    except FileNotFoundError:
        logging.error(f"[CONFIG] Error: '{config_file}' not found.")

        # Copy the default config file
        await copy_file(src="default.json", dst="config.json")

        return await read_config(config_file)
    except json.JSONDecodeError as e:
        logging.error(f"[CONFIG] Error decoding JSON: {e}")

        # Copy the default config file
        await copy_file(src="default.json", dst="config.json")

        return None
    except Exception as e:
        logging.error(f"[CONFIG] Error reading config: {e}")
        return None
