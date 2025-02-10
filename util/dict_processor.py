"""
This module provides a class for processing a list of dictionaries and transforming values according to a given structure.
"""


class DictProcessor:
    """Processes a list of dictionaries and transforms values according to the given structure."""

    def __init__(self, data: list):
        """
        Initializes with a list of dictionaries.

        Args:
            data (list): List of dictionaries to process.
        """
        self.data = data

    def process(self) -> list:
        """
        Processes a list of dictionaries and returns a list of formatted strings.

        Returns:
            list: List of processed strings.
        """
        processed_list = []

        for item in self.data:
            if len(item) == 1:
                # If there is only one key, add the value directly
                processed_list.append(list(item.values())[0])
            elif len(item) == 2:
                # If there are two keys, concatenate the values with a hyphen
                processed_list.append(
                    f"{list(item.values())[0]} - {list(item.values())[1]}")

        return processed_list

    def display(self) -> None:
        """
        Displays the processed list.
        """
        result = self.process()
        for item in result:
            print(item)


# Usage example:
if __name__ == "__main__":
    # Example data: list of dictionaries with 1 or 2 keys
    data = [
        {'Nome': '', 'Cargo': 'Engenheiro'},
        {'Nome': 'Pedro', 'Cargo': 'Analista'}
    ]

    # Create instance of the class with the data
    processor = DictProcessor(data)

    # Display the processed data
    processor.display()
