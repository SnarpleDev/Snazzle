# Snazzle
A better frontend for Scratch, built by the community, for the community

Snazzle is my attempt at a better Scratch website. It aims to be feature-rich and easy and quick to use, incorporating many things that the Scratch community has been wanting for years.

Basically, this is a Scratch website just for <s>MagicCrayon9342</s> power users.

> If you're more than a casual user of the Scratch website for whatever reason, then you'll like Snazzle.
> It's like a giant vat of coffee brewed with ingredients from the Scratch community.
-- Snazzle's website

## Running your own instance locally
Since Snazzle is very much still in development, this won't be representative of the final product's build steps.

But for now, this is how you do it:
1. Clone the repo
2. (optional but recommended) Create a Python virtual environment. We recommend Python 3.11 or later.
3. Run `pip3 install -r requirements.txt`.
   > If you are on an Arch based linux distro, you will have to run "sudo pacman -S python-flask
4. If you are using Replit or another website blocked from Scratch's API, change the variable "useDB" at the top of scratchdb.py to True.
5. Once deps are installed, run `python3 main.py`. This will set up a Flask server at `localhost:3000`. If you find any bugs, please report them.
   > If you're on Windows, run `py main.py` instead.
6. Go to `localhost:3000` in your favourite browser and play around with it!

## Hosting on Replit
Some features currently won't work properly due to usage of Scratch's API.
