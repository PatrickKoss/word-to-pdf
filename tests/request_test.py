"""Simple request test to server to show how to send files."""

import requests

# test file upload to windows implementation
# with open('test_windows.docx', 'rb') as f:
#     response = requests.post('http://localhost:5000/files', files={'test_windows.docx': f})
# with open('test_windows.pdf', 'wb') as f:
#     f.write(response.content)

# test file upload to linux/mac implementation
with open('test_linux.docx', 'rb') as f:
    response = requests.post('http://localhost:5000/files', files={'test_linux.docx': f})
with open('test_linux.pdf', 'wb') as f:
    f.write(response.content)
