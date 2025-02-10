"""
This module provides classes to configure and provide access to authentication and server details.
"""

import os
from dotenv import load_dotenv
from .encoded import CredentialEncoder
from .base import BaseUrl

load_dotenv()


class ServiceConfig:
    """
    Class to configure and provide access to authentication and server details.
    """

    def __init__(self) -> None:
        """
        Initialize the class by loading environment variables 
        and setting up authentication and server details.
        """
        self.env_user = os.getenv("USER")            # Usuário
        self.env_password = os.getenv("PASSWORD")    # Senha
        self.env_client = os.getenv("CLIENT")        # Servidor
        self.env_id = os.getenv("ENV_ID")            # ID do ambiente
        self.env_content_type = os.getenv("CONTENT_TYPE")
        self.env_field_name = os.getenv("METADATA_NAME")
        self.env_mode = os.getenv("MODE")
        
        self.auth = CredentialEncoder(self.env_user, self.env_password)
        self.server = BaseUrl(self.env_client, mode=self.env_mode)

    def get_auth(self) -> str:
        """
        Get the encoded authentication credentials.

        Returns:
            Base64 encoded credentials.
        """
        return self.auth.get_encoded_credentials()

    def get_server(self) -> str:
        """
        Get the server URL.

        Returns:
            Server URL.
        """
        return self.server.get_url()

    def get_environment_id(self) -> str:
        """
        Get the environment ID.

        Returns:
            Environment ID.
        """
        return self.env_id

    def get_content_type(self) -> str:
        """
        Retrieve the content type associated with the environment.

        This method returns the content type of the current environment,
        which indicates the type of content that the environment is handling.

        Returns:
            str: The content type of the environment.
        """
        return self.env_content_type

    def get_field_name(self) -> str:
        """
        Get the field name.

        Returns:
            Field name.
        """
        return self.env_field_name

    # def get_metadata(self) -> dict:
    #     """
    #     Get the metadata details.

    #     Returns:
    #         dict: Metadata details.
    #     """
    #     return {
    #         "user": self.env_user,
    #         "password": self.env_password,
    #         "client": self.env_client,
    #         "environment_id": self.env_id,
    #         "content_type": self.env_content_type
    #     }
