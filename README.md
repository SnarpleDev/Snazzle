# About this branch
This is a branch dedicated to a rework of the subforum browsing system.

Do not make any commits on `main` that conflict with commits on this branch. If a commit conflicts, it will be reverted.

## Running your own instance locally
Since Snazzle is very much still in development, this won't be representative of the final product's build steps.

But for now, this is how you do it:
1. Clone the repo
2. (optional but recommended) Create a Python virtual environment. We recommend Python 3.11 or later.
3. Run `pip3 install -r requirements.txt`. (This should work on all platforms.)
4. Once deps are installed, run `python3 main.py`. This will set up a Flask server at `127.0.0.1:3000`. If you find any bugs, please report them.
   > If you're on Windows, run `py main.py` instead.
5. Go to `127.0.0.1:3000` in your favourite browser and play around with it!
