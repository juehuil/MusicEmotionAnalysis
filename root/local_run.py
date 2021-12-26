# run server locally

# import variable app from root/app.py file
from app import app
from root.helpers import *

if __name__ == '__main__':
    app.debug = True
    app.run()
