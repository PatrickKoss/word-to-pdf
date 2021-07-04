# Introduction 
Api for converting word docx to pdf.

# Getting Started
1. Install python 3.9. You can use Anaconda for it and you can [download it from their offical website](https://www.anaconda.com/products/individual). Then create a new environment by `conda create -n myenv python=3.9`.
2. (optional if the base interpreter is set) `conda activate myenv`
3. Use `pip install -r requirements/requirements_linux.txt` or `pip install -r requirements/requirements_windows.txt` to install all libraries.

# Getting Started with Docker
1. Install docker and docker-compose
2. Start the server under http://localhost:5000 
````
$ docker-compose up --build -d
````

# Usage
Convert .doc or .docx files to .pdf. 
The word document needs to be in the files of a request and the conversion is in the response content.    
The endpoint for that is /files.   
An example can be found [/tests/request_test.py](./tests/request_test.py)