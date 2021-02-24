# dfview
terminal DataFrame view tool
This is a DataFrame view tool in Terminal based on curses.

Usage:
import dfview as dv
dv.view(DataFrame)

Key presses in the view:

'Within a screen (right hand):',

  'j: move left a column',
  
  'k: move down a row',
  
  'l: move right a column',
  
  'i: move up a row',
  
  'h: move to the first column of this screen',
  
  ';: move to the last column of this screen',
  
  '8: move to the first row of this screen',
  
  ',: move to the bottom row of this screen',
  
  'u: show row number on the bottom line',
  
  'o: show column name on the bottome line',
  
  'm: move between the bottom text line and table area',
  
  ']: expand cell width',
  
  '[: shrink cell width',
  
  'Beyond a Screen (left hand):',
  
  's: move left a screen',
  
  'f: move right a screen',
  
  'd: move down a screen',
  
  'e: move up a screen',
  
  'g: move to the last column',
  
  'a: move to the first column',
  
  '3: move to the first row',
  
  'c: move to the last row',
  
  'On the bottom line (right hand):',
  
  'j: move left a letter',
  
  'l: move right a letter',
  
  'k: move to the end of the text',
  
  'i: move to the beginning of the text',

  'Others:',

  'y: show help & come back',

  'Q: quit'
  
  ![Alt text](https://github.com/gwangcode/dfview/blob/main/dfview_sample.png)
