# Python Android: Netrunner

This project is a bare-bone Python implementation of the discontinued card game Android: Netrunner, focusing on core mechanics and simplified gameplay. Currently in development.


## Installation

1. Clone this repository:
git clone https://github.com/CHNSOC/pynetrunner.git
cd pynetrunner

2. (Optional) Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

3. Install the required packages (Currently All Built-in):
pip install -r requirements.txt

## Running the Game

To start the game, run:
python main.py

Follow the on-screen prompts to play the game.

## How to Play

1. The game alternates between the Corporation (Corp) and the Runner.
2. Each turn, the active player receives clicks (action points) and can perform various actions:
   - Draw cards
   - Gain credits
   - Install cards
   - Make runs (Runner only)
   - Score agendas (Corp only)
   - Play events/operations

3. Use the displayed shortcut keys to perform actions (e.g., 'A' to draw a card).
4. The game continues until one player wins by scoring 7 agenda points or if the Corp runs out of cards.

## Acknowledgements

This project is based on the Android: Netrunner card game created by Richard Garfield and published by Fantasy Flight Games.

## Disclaimer

This is a fan-made project and is not affiliated with or endorsed by the creators or publishers of Android: Netrunner.