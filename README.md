# Ai Research Buddy
## OUTDATED DONT USE AUTOMATIC SETUP

To run Flask-website: Simply run the 'SetupAndRun' file! It should install everything
required to run the website, and then start the website and open it in your browser!

You can use it to also run & open the website after you have installed everything too.


## Manual setup

To install python dependencies, run `pip install .` (you can also run it using python virtual environments to avoid global package download, to do that run `python -m venv NAME_OF_VIRTUAL_ENVIORNMENT`, and then run `./NAME_OF_VIRTUAL_ENVIORNMENT/Scripts/activate` on windows and `./NAME_OF_VIRTUAL_ENVIORNMENT/bin/activate` on linux or mac (if you are on a BSD based os the linux version should work))

To run the project, you need to run the svelte frontend on any port, and then run the flask api on the ip:port specified in frontend/vite.config.js, under server: proxy: '/api'. (default is localhost port 5000)

## To run the svelte frontend:
1. Cd into /frontend
2. run `npm run dev` or `npm run build`, depending on if it is for development (`dev`) or for deployment (`build`).

## To run the flask api
1. Cd into the root directory
2. run `python -m flask --app api.main run --port PORT`, but replace PORT with the desired port to run the api on (with default frontend configs requires port 5000).
