# About

Mindbot is a Discord application that can allow user to run command related to Mindbug.

Current supported commands:

- /card X : display the card info named X. There is a tolerance with typo.
- /randomcard : display a random card
- /createmindbugcard : Create a Mindbug Card with a given Artwork.
- /createcreaturecard : Create a Creature Card with a given Artwork.

# Install

## Docker

Docker is the prefered way of installing Mindbot.

Go to your mindbot directory, then run `docker compose build`.
You now have a docker image of mindbot named `mindbot` and a mangodb image.

# Run

## Docker

You need a file named `token.txt` containing the app key (this is secret, do not share it).
Then you can run `docker compose up`.