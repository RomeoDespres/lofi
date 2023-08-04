class LabelAlreadyExistsError(Exception):
    def __init__(self, label_name: str) -> None:
        self.label_name = label_name
