"""Flask app to run under linux distribution and mac os. It converts word doc to pdf."""

import os
import subprocess
import threading
import time
import uuid
from typing import List

from flask import Flask, request, abort, send_from_directory

UPLOAD_DIRECTORY = "./docs"
# mac path of libre office soffice
# LIBRE_OFFICE = r"/Applications/LibreOffice.app/Contents/MacOS/soffice"

# windows path of libre office soffice
LIBRE_OFFICE = os.environ.get("LIBRE_OFFICE_PATH", "C:\PROGRA~1\LibreOffice\program\soffice")

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

api = Flask(__name__)


@api.route("/files", methods=["POST"])
def convert():
    """Convert a word doc to pdf."""
    # check if a file is attached in the request
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

    # convert the file to pdf with libre office
    command: str = f"{LIBRE_OFFICE} --headless --convert-to pdf --outdir {UPLOAD_DIRECTORY} {UPLOAD_DIRECTORY}/{filename}"
    task = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    # check if an error appeared
    error: str = task.stderr.read().decode("utf-8")
    if error != "":
        abort(400, "Conversion failed")

    # generate pdf name
    pdf_name: str = f"{filename.split('.')[0]}.pdf"

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


# If DEVELOPMENT is set to true this will start a dev server. In production a real server should be used like gunicorn.
# Check out the Dockerfile to see how gunicorn is set up.
if __name__ == "__main__" and os.environ.get("DEVELOPMENT", "true") == "true":
    """Run api in debug mode."""
    api.run(debug=True, port=os.environ.get("PORT", 5000))
