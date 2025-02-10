"""
Import the base64 library to encode credentials
"""

import base64


class CredentialEncoder:
    """
    Class to encode credentials in base64.
    """

    def __init__(self, username: str, password: str) -> None:
        """
        Initialize the class with a username and password.

        Args:
            username: Username.
            password: Password.
        """
        self.username = username
        self.password = password
        self.encoded_credentials = self.encode_credentials()

    def encode_credentials(self) -> str:
        """
        Encode credentials in base64.

        Returns:
            Base64 encoded credentials.
        """
        encoded_auth = base64.b64encode(
            f"{self.username}:{self.password}".encode("utf-8")).decode("utf-8")
        return f"Basic {encoded_auth}"

    def get_encoded_credentials(self) -> str:
        """
        Get the encoded credentials.

        Returns:
            The encoded credentials.
        """
        return self.encoded_credentials
