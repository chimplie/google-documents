# Google Documents

Work with Google Documents simply without any boring stuff regarding Credentials Account etc.

Read from the Google Sheet just in 3 lines:

```python
from google_documents.entities import GoogleDriveSpreadsheet
sh = GoogleDriveSpreadsheet.get(id="YOUR_SPREADSHEET_ID")
sh.read(range_name="Sheet 1!A1:B4")
```

Export Google Document to word in 3 lines as well:

```python
from google_documents.entities import GoogleDriveDocument
doc = GoogleDriveDocument.get(id="YOUR_DOCUMENT_ID")
doc.export("my_file.docx")
```

## Installation

1. Install the module via pip:

```bash
pip install google-documents
```

1. Issue service account file via [Google Cloud Console](https://console.cloud.google.com/)

1. Put the path to your file in the GOOGLE_DOCUMENT_SERVICE_JSON environment varialbe:

```bash
export GOOGLE_DOCUMENT_SERVICE_JSON=PATH_TO_YOUR_SERVICE_ACCOUNT_FILE
```

That's it. Now you can start using this package

