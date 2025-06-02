import asyncio
import logging
from utils import read_config
from example_handler import ExampleHandler


async def main():
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()

    # Read configuration from the config file
    config = await read_config("config.json")
    if not config:
        return

    # Check if Key Exists
    try:
        _log_level = config.get("LOG_LEVEL", "DEBUG")

        if _log_level == "WARNING":
            logging.basicConfig(level=logging.WARNING)
        elif _log_level == "INFO":
            logging.basicConfig(level=logging.INFO)
        elif _log_level == "DEBUG":
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.WARNING)

    except Exception as e:
        logging.critical(f"Error Reading LOG_LEVEL from config: {e}")
        logging.basicConfig(level=logging.DEBUG)
        return

    example_handler = ExampleHandler(config)

    await asyncio.gather(
        example_handler.local_mqtt_handler.routine(),
        example_handler.publish_heartbeat(),
        example_handler.dummy_process()
    )

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
