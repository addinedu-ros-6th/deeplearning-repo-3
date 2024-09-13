from Intelligence_Vehicle_Service.Processor.Processor import Processor

class ProcessorFactory:
    def __init__(self) -> None:
        self.processors = {}

    def register_processor(self, key, processor):
        self.processors[key] = processor

    def get_processor(self, name) -> Processor:
        processor = self.processors.get(name)
        if not processor:
            raise ValueError(f"Invalid processor name: {name}")
        return processor()