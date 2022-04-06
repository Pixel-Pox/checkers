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

By default you play as White pieces against level 3 Black.
You can ask for help with arguments by typing in: 
```shell
python main.py -h
```

Arguments for black/white level are -b, -w and take in integers from 1 to 7: 
```shell
python main.py -b 4
python main.py -w 2
```

If you want to play as black
```shell
python main.py -p BLACK
```

Or if you want the AI to play against AI
```shell
python main.py -p None -b 5 -w 5
```

You play by selecting a piece on each player's turn and then selecting an available legal move (marked with blue dot). 

Good luck and have fun :) 


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