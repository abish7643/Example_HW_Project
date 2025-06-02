from asyncio import sleep
from aiomqtt import Client
import aiomqtt.exceptions
import logging


class MQTTHandler:
    def __init__(self, sensor_manager):
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.topics = []
        self.sensor_manager = sensor_manager
        self.client = None
        self.connected = False
        self.immediate_reconnect = False
        self.telemetry = True

    async def routine(self):
        """
        Main Routine for the MQTT Client
        Handles the Connection and Reconnection to the MQTT Broker

        :return:
        """
        try:
            if self.telemetry:
                logging.info(f"[MQTT] Connecting to {self.host}:{self.port}")
                async with Client(self.host, self.port,
                                  username=self.username, password=self.password) as self.client:
                    self.connected = True
                    for topic in self.topics:
                        await self.client.subscribe(topic)
                    async for message in self.client.messages:
                        await self.sensor_manager.process_message(message.payload, message.topic.value)
            else:
                await sleep(4)
                await self.routine()
        except aiomqtt.MqttError:
            self.connected = False
            logging.error(f"[MQTT] Connection Error")
            if not self.immediate_reconnect:
                await sleep(4)
            self.immediate_reconnect = False
            await self.routine()
        except Exception as e:
            self.connected = False
            logging.error(f"[MQTT] Error: {e}")
            await sleep(4)
            await self.routine()

    async def publish(self, topic, message):
        """
        Publish a message to the MQTT Broker

        :param topic:
        :param message:
        :return:
        """
        if not self.telemetry:
            return

        if not self.connected:
            return

        if self.client is not None:
            try:
                await self.client.publish(topic, message)
            except Exception as e:
                logging.error(f"[MQTT] Publish Error: {e}")

    def add_topic(self, topic):
        """
        Add a topic to the MQTT Client

        :param topic:
        :return:
        """
        if topic in self.topics:
            return

        self.topics.append(topic)

    def update_credentials(self, username, password):
        """
        Update the Credentials for the MQTT Broker.

        :param username:
        :param password:
        :return:
        """
        if username == "":
            username = None

        if password == "":
            password = None

        self.username = username
        self.password = password
        logging.info("[MQTT] Credentials Updated")

    def update_broker(self, host, port):
        """
        Update the Broker Information

        :param host:
        :param port:
        :return:
        """
        self.host = host
        self.port = port
        logging.info("[MQTT] Broker Updated")

    async def disconnect(self, immediate_reconnect=True):
        """
        Disconnect the MQTT Client

        :return:
        """
        if self.client is not None:
            self.immediate_reconnect = immediate_reconnect
            await self.client.__aexit__(None, None, None)
