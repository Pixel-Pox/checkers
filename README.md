# International draughts
Rules are created according to international (polish) rules of checkers.
https://en.wikipedia.org/wiki/International_draughts <- english version of the rules which has some wrong translations from the original source: 
https://pl.wikipedia.org/wiki/Warcaby_polskie

## Quick start
Install requirements with
```shell
pip install -r requirements.txt
```

Start the game with
```shell
python main.py
```

You play by selecting a piece on each player's turn and then selecting a available legal move (marked with blue dot). 


## Contributing
If you want to make changes to the code, feel free. 
Install the development libraries with
```shell
pip install -r requirements-dev.txt
```

Run all tests with
```shell
python -m pytest
```