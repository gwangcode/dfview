# dfview
terminal DataFrame view tool
This is a DataFrame view tool in Terminal based on curses.

1. Usage:

  import dfview as dv

  dv.view(DataFrame)

2. Function Introduction:

  view(DataFrame=None, ObjDF=None, Bar=None, Cross=None, Index=None, Header=None, CellWidth=8):

    DataFrame: accepts DataFrame, which shows the DataFrame without any style.

    ObjDF: accepts the processed DataFrame by make_obj_df(DataFrame) that generates the ObjDF in which the data is replaced with text_sec object that can applied with styles (forecolor, backcolor, fold, italic, underline etc.).

    Bar: accepts text_sec object to set up the cell bar style.

    Cross: accepts text_sec object to set up the cross mark style.

    Index:

      None: Do not show index.

      text_sec object: sets up the index style.

    Header: accepts text_sec object to set up the header style.

    CellWidth: int, sets up the initial cell width, default is 8 (char width)
   
  
3. Control keys in the view:

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
  
  4. Example shows like the following:
  
  ![Alt text](https://github.com/gwangcode/dfview/blob/main/dfview_sample.png)
