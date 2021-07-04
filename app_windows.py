"""Flask app to run under windows os. It converts word doc to pdf."""

import os
import threading
import time
import uuid
from typing import List

import pythoncom
from docx2pdf import convert
from flask import Flask, request, abort, jsonify, send_from_directory

UPLOAD_DIRECTORY = "./docs"
# LIBRE_OFFICE = r"/Applications/LibreOffice.app/Contents/MacOS/soffice"
LIBRE_OFFICE = os.environ.get("LIBRE_OFFICE_PATH", "C:\PROGRA~1\LibreOffice\program\soffice")

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

api = Flask(__name__)


@api.route("/files")
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)


@api.route("/files/<path:path>")
def get_file(path):
    """Download a file."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


@api.route("/files", methods=["POST"])
def convert():
    """Convert a word doc to pdf."""
    # check if a file is attached in the request
    pythoncom.CoInitialize()
    request_file_keys: List[str] = list(request.files.keys())
    if len(request_file_keys) == 0 or len(request_file_keys) > 1:
        abort(400, "Exact one file must be sent")
    filename: str = request_file_keys[0]

    # validate if the file ends with a valid word format
    if not filename.endswith(".docx") and not filename.endswith(".doc"):
        abort(400, "file ending should be docx or doc")

    # get file and split the sub dir
    uploaded_file = request.files[filename]
    if "/" in filename:
        filename = filename.split("/")[-1]

    # adjust the filename to give it a unique name. To do that calculate a hash value of a uuid
    file_ending: str = filename.split(".")[-1]
    hash_uuid: str = str(hash(uuid.uuid4()))[:10]
    filename: str = f"{filename.split('.')[0]}_{hash_uuid}.{file_ending}"

    # save the file
    try:
        uploaded_file.save(os.path.join(UPLOAD_DIRECTORY, filename))
    except Exception:
        abort(400, "File save went wrong")

    # generate pdf name
    pdf_name: str = f"{filename.split('.')[0]}.pdf"

    # convert word doc to pdf
    try:
        convert(os.path.join(UPLOAD_DIRECTORY, filename), f"{UPLOAD_DIRECTORY}/{pdf_name}")
    except Exception:
        abort(400, "Conversion failed")

    # remove pdf async
    background_remove(f"{UPLOAD_DIRECTORY}/{pdf_name}")

    # remove word doc from server
    if os.path.exists(os.path.join(UPLOAD_DIRECTORY, filename)):
        os.remove(os.path.join(UPLOAD_DIRECTORY, filename))

    # send pdf
    return send_from_directory(UPLOAD_DIRECTORY, pdf_name, as_attachment=True), 201


def background_remove(path: str) -> None:
    """Start a thread that removes a file based on a path."""
    thread = threading.Thread(target=remove_file, args=(path,))
    thread.start()


def remove_file(path: str) -> None:
    """Remove a file if it exists after 15s."""
    time.sleep(15)
    if os.path.exists(path):
        os.remove(path)


if __name__ == "__main__" and os.environ.get("DEVELOPMENT", "true") == "true":
    api.run(debug=True, port=5000)
