# DumpAI

## Prologue

The idea behind this project was to create a Chess AI. However, I have never done such a thing before, and creating it from scratch will be very hard. That is why I decided to implement simpler stuff first. This project gathers all the subprojects I work on my free time that are related to Artificial Intelligence. <br>

## Chess - Initial Project

The idea is simple : create an AI that plays chess. However, before reaching this goal, the first step will be to implement the game myself.

### Implementation

* The first implementation was very rough and I didn't take the time to do it efficiently. The board was a list of list containing either pieces or empty cases. Pieces were objects of the different classes I implemented, and empty cases were the string "_". 
* After the first try of doing the MinMax algorithm, I decided to totally change the way the information of pieces and positions were contained. I decided to put all the pieces in one dictionnary, each piece referenced with a key which was unique. Then, those key were put in a numpy array to have positions of corresponding pieces. Also, instead of keeping on copying the entire board when I wanted to calculate few moves in advance, I created a function `undo_move` so that you only use on instance of the board and the dictionnary all the time. Directly, computation was much more efficient (for two layers : 13s -> 2s).

## Pogostuck

I wanted to try to create an AI that plays a game. One game I played a lot is Pogostuck, so the goal of this subproject is to create a version of Pogostuck in Python (simple), then to implement an AI which plays the game.