"""
This module provides the BaseUrl class to represent configuration data for the application.
"""

class BaseUrl:
    """This class represents the configuration data for the application."""

    def __init__(self, client: str | None, mode: str = 'prod') -> None:
        self.client = client
        self.mode = mode
        self.url = self._build_url()

    def _build_url(self) -> str:
        if self.mode == 'dev':
            return f"http://{self.client}.newhom.greendocs.net/"
        return f"https://{self.client}.greendocs.net/"

    def get_url(self) -> str:
        """
        Get the constructed URL.

        Returns:
            The constructed URL.
        """
        return self.url
