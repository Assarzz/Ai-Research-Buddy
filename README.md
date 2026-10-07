# Ai Research Buddy

To run Flask-website: Simply run the 'SetupAndRun' file! It should install everything
required to run the website, and then start the website and open it in your browser!

You can use it to also run & open the website after you have installed everything too.


## Manual setup

To install python dependencies, run `pip install .` (you can also run it using python virtual environments to avoid global package download, to do that run `python -m venv NAME_OF_VIRTUAL_ENVIORNMENT`, and then run `./NAME_OF_VIRTUAL_ENVIORNMENT/Scripts/activate` on windows and `./NAME_OF_VIRTUAL_ENVIORNMENT/bin/activate` on linux or mac (if you are on a BSD based os the linux version should work))

In the root directory of the project, run `python -m flask --app webhost.main run --port PORT`, but replace PORT with the port you want to host the website on
