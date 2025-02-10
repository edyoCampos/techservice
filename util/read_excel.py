"""
This module provides the ExcelReader class to read an Excel file 
and return its content as a list of dictionaries.
"""

import os
import pandas as pd


class ExcelReader:
    """A class to read an Excel file and return its content as a list of dictionaries."""

    def __init__(self, excel_file_path: str):
        """
        Initializes the ExcelReader with the path to the Excel file.

        Args:
            excel_file_path (str): The path to the Excel file to be read.
        """
        self.file_path = excel_file_path

    def file_exists(self) -> bool:
        """
        Check if the Excel file exists.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.exists(self.file_path)

    def read_to_dict(self) -> list:
        """
        Reads the Excel file and returns the content as a list of dictionaries.

        Each dictionary corresponds to a row in the Excel file, where the keys
        are the column names and the values are the cell values.

        Returns:
            list: A list of dictionaries representing the data in the Excel file.
        """
        if not self.file_exists():
            print(f"File not found: {self.file_path}")
            return []

        try:
            # Read the Excel file into a DataFrame
            df = pd.read_excel(self.file_path)

            # Replace NaN values with empty strings
            df = df.fillna("")

            # Convert the DataFrame to a list of dictionaries (array of objects)
            records = df.to_dict(orient='records')

            return records

        except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            print(f"Error reading the Excel file: {e}")
            return []

    def get_file_path(self) -> str:
        """
        Get the file path.

        Returns:
            The file path.
        """
        return self.file_path


# # Example usage:
# if __name__ == "__main__":
#     file_path = 'path_to_your_excel_file.xlsx'  # Replace with your actual file path

#     # Create an ExcelReader instance
#     excel_reader = ExcelReader(file_path)

#     # Check if the file exists
#     if excel_reader.file_exists():
#         # Read data from Excel and get it as a list of dictionaries
#         data = excel_reader.read_to_dict()

#         # Output the data (array of objects)
#         print(data)
#     else:
#         print("The Excel file does not exist.")
