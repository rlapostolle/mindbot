# About

Mindbot is a Discord application that can allow user to run command related to Mindbug.

Current supported commands:

- /card X : display the card info named X. There is a tolerance with typo.
- /randomcard : display a random card

# Install

## Docker

Docker is the prefered way of installing Mindbot.

Go to your mindbot directory, then run `docker build -t mindbot .`.
You now have a docker image of mindbot named `mindbot`.

# Run

## Docker

You need a file named `token.txt` containing the app key (this is secret, do not share it).
Then you can run `docker run -d --mount "type=bind,src=/path/to/token.txt,target=/mindbot/token.txt,readonly" mindbot`