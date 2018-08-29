from google_documents.entities.manager import GoogleDriveDocumentManager


class ApiServiceMixin:
    _custom_api_service = None

    def set_api_service(self, api_service):
        self._custom_api_service = api_service

    @property
    def _default_api_service(self):
        return self.objects().get_default_api_service()

    @property
    def _api_service(self):
        return self._custom_api_service or self._default_api_service

    @classmethod
    def objects(cls):
        return GoogleDriveDocumentManager(cls)
