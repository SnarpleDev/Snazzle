# Snazzle

A better frontend for Scratch, built by the community, for the community

Snazzle is my attempt at a better Scratch website. It aims to be feature-rich and easy and quick to use, incorporating many things that the Scratch community has been wanting for years.

Basically, this is a Scratch website just for ~~MagicCrayon9342~~ power users.

> If you're more than a casual user of the Scratch website for whatever reason, then you'll like Snazzle.
> It's like a giant vat of coffee brewed with ingredients from the Scratch community.
-- Snazzle's website

## Contributing

Format your code with [Black](https://github.com/psf/black) and make a pull request. If there is a feature branch for what you are changing, make the PR to that brach instead of main.

## Running your own instance locally

Since Snazzle is very much still in development, this won't be representative of the final product's build steps.

But for now, this is how you do it:

1. Clone the repo
2. (optional but recommended) Create a Python virtual environment. We recommend Python 3.11 or later.
3. Run `pip3 install -r requirements.txt`.
   > If you are on an Arch based linux distro, you will have to run `sudo pacman -S python-flask`
4. If you are using Replit or another website blocked from Scratch's API, change the variable "REPLIT_MODE" at the top of `main.py` to True.
5. Once deps are installed, run `flask run`. This will set up a Flask server at `localhost:5000`. If you find any bugs, please report them.
6. Go to `localhost:5000` in your favourite browser and play around with it!

## Hosting on Replit

Some features currently won't work properly due to usage of Scratch's API. With this in mind, [there's a version on replit that works around these limitations.](https://snazzle-repl.redstonescratch.repl.co/) However, because of these limitations, there are the following disadvantages to using the repl:

1. No projects or studios on the front page
2. All profile pictures are the default one
3. May be slower
