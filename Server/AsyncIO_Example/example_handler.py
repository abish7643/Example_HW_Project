import asyncio
import json
import logging
import datetime
from mqtt_handler import MQTTHandler
from version import get_version


class ExampleHandler:
    """
    ExampleHandler class handles ------------------- and publishing the data to the MQTT broker.
    Also Handles MQTT Connection and Reconnection, MQTT Message Handling.
    """

    def __init__(self, config):
        self.config = config
        self.PrevMQTTPublishTime = datetime.datetime.now()
        self.mqtt_state = False

        self.local_broker_info = self.config.get("MQTT", {})
        self.local_mqtt_handler = MQTTHandler(self)
        self.local_mqtt_handler.update_broker(self.local_broker_info['HOST'], self.local_broker_info['PORT'])
        self.local_mqtt_handler.update_credentials(self.local_broker_info.get("USERNAME"),
                                                   self.local_broker_info.get("PASSWORD"))
        self.local_mqtt_handler.add_topic(self.local_broker_info.get("QUERY_TOPIC"))
        self.local_mqtt_handler.add_topic(self.local_broker_info.get("ALL_TOPIC"))
        self.local_mqtt_handler.add_topic(self.local_broker_info.get("EDIT_TOPIC"))
        self.local_mqtt_handler.add_topic(self.local_broker_info.get("SENSOR_TOPIC"))

        self.version = get_version()

    async def update_detection_settings(self, settings):
        """
        Update the config from the decoded settings data.

        :param settings: Raw Settings Data as Decoded as Dict
        """
        _config = dict(self.config.get("EXAMPLE", {}))

        _config["MODE"] = settings.get("MODE", _config["MODE"])
        _config["INTERVAL"] = settings.get("INTERVAL", _config["INTERVAL"])

        # If Configuration Changed -> Update
        if self.config["EXAMPLE"] != _config:
            logging.info(f"[Example] Settings Changed: {json.dumps(_config)}")

            self.config["EXAMPLE"] = _config
            self.write_config()

    def load_settings(self):
        """
        Load Settings to Variables.
        The Variables should be used during runtime instead of the Global Config.
        """
        _config = self.config.get("EXAMPLE", {})

        self.mode = _config["MODE"]
        self.interval = _config["INTERVAL"]

    async def process_message(self, message, topic):
        logging.info(f"[MQTT] Received Message on {topic}")

        try:
            _mqtt_config = self.config.get("MQTT", {})
            if topic == _mqtt_config.get("QUERY_TOPIC", ""):
                _message_json = json.loads(message.decode("utf-8"))
                if _message_json.get("type", "") != "settings":
                    return False

                logging.info("[MQTT] Publishing Settings")
                return True
            elif topic == _mqtt_config.get("ALL_TOPIC", ""):
                logging.info("[MQTT] All Topic -> Not Implemented")
                return True
            elif topic == _mqtt_config.get("EDIT_TOPIC", ""):
                logging.info("[MQTT] Edit Topic -> {}".format(message))

                return True
            return False
        except Exception as e:
            logging.error(f"[MQTT] Error in on_message: {e}")
            return False

    async def publish_heartbeat(self):
        logging.info("[MQTT] Heartbeat Routine")
        hb_iterator = 0
        while True:
            _interval = self.config.get("MQTT", {}).get("HB_INTERVAL", 5)
            _mqtt_topic = self.config.get("MQTT", {}).get("PB_TOPIC", "device/isotopedetection")
            try:
                if (datetime.datetime.now() - self.PrevMQTTPublishTime).total_seconds() >= _interval:
                    _mqtt_data = {
                        "type": "status",
                        "data": {},
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    await self.local_mqtt_handler.publish(_mqtt_topic, json.dumps(_mqtt_data))
                    logging.info("[MQTT] Heartbeat Sent {}".format(hb_iterator))
                    hb_iterator += 1
            except Exception as e:
                logging.error(f"[MQTT] Error in publish_heartbeat: {e}")
            await asyncio.sleep(_interval)

    async def dummy_process(self):
        logging.info("[Example] Dummy Routine")
        hb_iterator = 0
        while True:
            logging.info("[Example] Dummy Process {}".format(hb_iterator))
            hb_iterator += 1
            await asyncio.sleep(1)

    def write_config(self):
        try:
            _config = self.config

            # Write to File
            with open("config.json", "w") as _file:
                json.dump(_config, _file, indent=4)

            self.config = _config

        except Exception as e:
            logging.error(f"[CONFIG] Error in write_config: {e}")
            return False
