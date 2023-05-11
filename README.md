# Chess in Python

The idea behind this project is to create a Chess AI. <br>

### Implementation

* The first implementation was very rough and I didn't take the time to do it efficiently. The board was a list of list containing either pieces or empty cases. Pieces were objects of the different classes I implemented, and empty cases were the string "_". 
* After the first try of doing the MinMax algorithm, I decided to totally change the way the information of pieces and positions were contained. I decided to put all the pieces in one dictionnary, each piece referenced with a key which is unique. Then, those key were put in a numpy array to have positions of corresponding pieces. Also, instead of keeping on copying the entire board when I wanted to calculate few moves in advance, I created a function `undo_move` so that you only use on instance of the board and the dictionnary all the time. Directly, computation was much more efficient (for two layers : 13s -> 2s).