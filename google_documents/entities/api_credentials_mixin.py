"""
Module for the ApiCredentialsMixin class
"""
from google_documents.entity_managers.file import GoogleDriveDocumentManager


class ApiCredentialsMixin:
    """
    Adds credentials operations to the class
    """

    _custom_api_credentials = None

    def set_api_credentials(self, api_credentials):
        """
        Allows to set custom API credentials
        """
        self._custom_api_credentials = api_credentials

    @property
    def _default_api_credentials(self):
        return self.objects().get_default_api_credentials()

    @property
    def _api_credentials(self):
        return self._custom_api_credentials or self._default_api_credentials

    @classmethod
    def objects(cls):
        """
        Returns Manager for the Class with credentials
        """
        return GoogleDriveDocumentManager(cls)
