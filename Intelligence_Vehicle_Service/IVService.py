from typing import Any
from flask import Flask, request, jsonify
from Processor.ProcessorFactory import *
from Processor.Processor import *
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient

class IVService:

    def __init__(self) -> None:
        self.processor_factory = ProcessorFactory()
        self.processor_factory.register_processor("lane", LaneProcessor)
        self.processor_factory.register_processor("obstacle", ObstacleProcessor)

        
    def handle_receive_data(self, from_client, data):
        key = data.get("key")
        print('\033[91m'+"Received data: from_client=" +'\033[92m'+f"{from_client}, key={key}," +'\033[97m'+ f"data={data}", '\033[0m')
        if key is None:
            print(f"Warning: Received data with no key from {from_client}")
            return

        try:
            self.processor = self.processor_factory.get_processor(key)
            self.processor.execute(data)

        except ValueError as e:
            print(f"Error processing data: {e}")






    


