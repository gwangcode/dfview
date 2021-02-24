#! /Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import curses as cur, pandas as pd

def get_chr_width(chr):
  """Return the screen column width for unicode ordinal o."""
  widths = (
  (126,    1), (159,    0), (687,     1), (710,   0), (711,   1), 
  (727,    0), (733,    1), (879,     0), (1154,  1), (1161,  0), 
  (4347,   1), (4447,   2), (7467,    1), (7521,  0), (8369,  1), 
  (8426,   0), (9000,   1), (9002,    2), (11021, 1), (12350, 2), 
  (12351,  1), (12438,  2), (12442,   0), (19893, 2), (19967, 1),
  (55203,  2), (63743,  1), (64106,   2), (65039, 1), (65059, 0),
  (65131,  2), (65279,  1), (65376,   2), (65500, 1), (65510, 2),
  (120831, 1), (262141, 2), (1114109, 1),)
  x=ord(chr)
  if x == 0xe or x == 0xf:
      return 0
  for num, wid in widths:
      if x <= num:
          return wid
  return 1


def slice_str(Str, Width):
  s=''
  if str_width(Str)<=Width: return Str+(Width-str_width(Str))*' '
    
  else:
    for i in range(1,len(Str)+1):
      s=[Str[:i], Str[1:]]
      if str_width(s[0])>Width:
        s=[Str[:i-1],Str[i-1:]]
        if str_width(s[0])<=Width: s[0]+=(Width-str_width(s[0]))*' '  
        return s[0]

def str_width(Str):
  n=0
  if Str:
    for i in Str: n+=get_chr_width(i)
  return n

class text_sec:
  text=''
  row=0
  col=0
  altcharset=False 
  blink=False 
  bold=False 
  dim=False 
  invisible=False 
  normal=True 
  protect=False 
  reverse=False 
  standout=False 
  underline=False 
  horizontal=False 
  left=False 
  low=False 
  right=False 
  top=False 
  vertical=False 
  chartext=False 
  fcolor=0
  bcolor=231

  def __init__(self, 
    text='',
    altcharset=False,
    blink=False ,
    bold=False ,
    dim=False ,
    invisible=False ,
    normal=True ,
    protect=False, 
    reverse=False ,
    standout=False ,
    underline=False ,
    horizontal=False ,
    left=False ,
    low=False ,
    right=False, 
    top=False ,
    vertical=False ,
    chartext=False ,
    fcolor=-1,
    bcolor=231
    ):
    self.text=text
    self.altcharset=altcharset
    self.blink=blink
    self.bold=bold
    self.dim=dim
    self.invisible=invisible
    self.normal=normal
    self.protect=protect
    self.reverse=reverse
    self.standout=standout
    self.underline=underline
    self.horizontal=horizontal
    self.left=left
    self.low=low
    self.right=right
    self.top=top
    self.vertical=vertical
    self.chartext=chartext
    self.fcolor=fcolor
    self.bcolor=bcolor

  def mode(self):
    r=0
    if self.altcharset: r+=cur.A_ALTCHARSET #
    elif self.blink: r+=cur.A_BLINK
    elif self.bold: r+=cur.A_BOLD ##
    elif self.dim: r+=cur.A_DIM 
    elif self.invisible: r+=cur.A_INVIS #
    elif self.normal: r+=cur.A_NORMAL ##
    elif self.protect: r+=cur.A_PROTECT #
    elif self.reverse: r+=cur.A_REVERSE
    elif self.standout: r+=cur.A_STANDOUT
    elif self.underline: r+=cur.A_UNDERLINE ##
    elif self.horizontal: r+=cur.A_HORIZONTAL #
    elif self.left: r+=cur.A_LEFT #
    elif self.low: r+=cur.A_LOW #
    elif self.right: r+=cur.A_RIGHT #
    elif self.top: r+=cur.A_TOP #
    elif self.vertical: r+=cur.A_VERTICAL #
    elif self.chartext: r+=cur.A_CHARTEXT #
    else: r+=cur.A_NORMAL
    return r 

class coord:
  row=0
  col=0

pos=coord()




class TableGrid:
  __screen=None # screen object
  __ColorPair=[0]

  ObjDF=None # able to set up cell style
  DF=None
  Bar=text_sec() # set up bar style
  Cross=text_sec() # set up cross color (bcolor, fcolor) and the select mode (fcolor)
  Index=text_sec() # set up index style, None: do not print index
  Header=text_sec() # set up header style
  
  __IndexStatus=None

  __df=None

  # top left cornor
  __OffsetRow=0 
  __OffsetCol=0 

  # current cell relative to table
  __TableRow=0
  __TableCol=0

  # cell_width
  __CellWidth=None

  # screen size
  __ScreenHeight=0
  __ScreenWidth=0

  # On screen table size
  __MaxRow=0
  __MaxCol=0
  __ResidueWidth=0

  __cursor_row=0
  __new_line=True

  def __init__(self, Screen, DataFrame=None, ObjDF=None, Bar=None): 
    self.__screen=Screen # Screen obj
    if ObjDF is not None: self.ObjDF=ObjDF
    elif DataFrame is not None: self.DF=DataFrame
    if Bar is not None: self.Bar=Bar
    
    cur.curs_set(0)
    
  # set color pair
  def __set_color_pair(self, ForeColor, BackColor): # if color pairs >256 (255 is the maxt color number), the color pair is ineffective 
    CurColor=(ForeColor, BackColor)
    if CurColor[0]<0: return 0
    if CurColor in self.__ColorPair: return self.__ColorPair.index(CurColor)
    else:
      if len(self.__ColorPair)<=256: 
        self.__ColorPair.append(CurColor)
        return len(self.__ColorPair)-1

  # return attribute for addstr    
  def __set_attr(self, StrMode, ForeColor, BackColor):
    self.__CurStrMode=StrMode
    if ForeColor<0: return StrMode+cur.color_pair(0)
    else:
      CurColor=self.__set_color_pair(ForeColor,BackColor)
      ForeColor, BackColor=self.__ColorPair[CurColor]
      cur.init_pair(CurColor,ForeColor,BackColor)  
      return StrMode+cur.color_pair(CurColor)

  def set_offset(self, OffsetRow=None, OffsetCol=None):
    '''
    returns y: lines, x: cols
    '''
    if OffsetRow is not None: self.__OffsetRow=OffsetRow
    if OffsetCol is not None: self.__OffsetCol=OffsetCol

  # set coordinates
  def set_pos(self, TableRow=None, TableCol=None, CellWidth=None):
    '''
    TableRow: Row relative to Table
    TableCol: Col relatvie to Table
    '''

    if TableRow is None: TableRow=self.__TableRow
    if TableCol is None: TableCol=self.__TableCol
    if CellWidth is None: CellWidth=self.__CellWidth

    ScreenHeight, ScreenWidth=self.__screen.getmaxyx()
    self.__ScreenHeight=ScreenHeight
    self.__ScreenWidth=ScreenWidth
    MaxRow=ScreenHeight-2
    
    if CellWidth is None: 
      CellWidth=ScreenWidth-2
      MaxCol=1
      ResidueWidth=0
      self.__IndexStatus=self.Index
      self.Index=None

    else:
      self.Index=self.__IndexStatus
      MaxCol=ScreenWidth//(CellWidth+1)-1
      ResidueWidth=ScreenWidth%(CellWidth+1)

    if TableCol-self.__OffsetCol>MaxCol-1: self.__OffsetCol=TableCol-MaxCol+1
    if TableCol<self.__OffsetCol: self.__OffsetCol=TableCol

    if TableRow-self.__OffsetRow>MaxRow-1: self.__OffsetRow=TableRow-MaxRow+1
    if TableRow<self.__OffsetRow: self.__OffsetRow=TableRow
    
    self.__TableCol=TableCol
    self.__TableRow=TableRow
    self.__CellWidth=CellWidth
    self.__MaxRow=MaxRow
    self.__MaxCol=MaxCol
    self.__ResidueWidth=ResidueWidth

    return MaxRow, MaxCol, self.__OffsetRow, self.__OffsetCol, ScreenHeight, ScreenWidth

  def __make_obj_cell(self, x):
    ts=text_sec()
    ts.text=x
    ts.col=pos.col
    ts.row=pos.row
    pos.row+=1
    return ts

  def __make_obj_col(self, x):
    r=x.map(self.__make_obj_cell)
    pos.col+=1
    pos.row=self.__OffsetRow
    return r
    

  def make_obj_df(self, DataFrame):
    r=DataFrame.apply(self.__make_obj_col, axis=0)
    return r

  def __print_cell(self, text_sec, Header=False, Index=False):
    ScreenWidth=self.__ScreenWidth
    CellWidth=self.__CellWidth
    
    if Header:
      StrMode=self.Header.mode()
      ForeColor=self.Header.fcolor
      BackColor=self.Header.bcolor

      BarStrMode=self.Bar.mode()
      BarForeColor=self.Bar.fcolor
      BarBackColor=self.Header.bcolor

    else:
      StrMode=text_sec.mode()
      ForeColor=text_sec.fcolor
      BackColor=text_sec.bcolor

      BarStrMode=self.Bar.mode()
      BarForeColor=self.Bar.fcolor
      BarBackColor=self.Bar.bcolor
     
      if not Index and (self.__TableCol==text_sec.col or self.__TableRow==text_sec.row): 
        ForeColor=self.Cross.fcolor
        BackColor=self.Cross.bcolor

      else: BackColor=text_sec.bcolor

      if self.__TableCol==text_sec.col and self.__TableRow==text_sec.row and not Index: 
        ForeColor=self.Cross.fcolor
        StrMode=self.Cross.mode()

      if self.__TableRow==text_sec.row or (Index and self.__TableRow==text_sec.text): BarBackColor=self.Cross.bcolor
      else: BarBackColor=self.Bar.bcolor

    try:
      if self.__new_line:
        if Header: 
          self.__screen.move(0, 0)   
          if self.Index is not None:
            self.__screen.addstr(slice_str('Index', CellWidth), self.__set_attr(StrMode, ForeColor, BackColor)) 
            self.__screen.addstr('|', self.__set_attr(BarStrMode, BarForeColor, BarBackColor))
        else: self.__screen.move(self.__cursor_row+1, 0) 
            
        self.__new_line=False 
      
      CursorY, CursorX=self.__screen.getyx() # cursor pos
      dw=ScreenWidth-CursorX
      dw=min(dw, CellWidth)
      
      if Header: Txt=slice_str(text_sec, dw) 
      else: Txt=slice_str(str(text_sec.text), dw)
      
      self.__screen.addstr(Txt, self.__set_attr(StrMode, ForeColor, BackColor))
      CursorY2, CursorX2=self.__screen.getyx() # cursor pos
      if CursorY==CursorY2: self.__screen.addstr('|', self.__set_attr(BarStrMode, BarForeColor, BarBackColor))
      
    except: 
      self.__screen.move(CursorY, ScreenWidth-1)
  
  # add line onto screen
  def __print_line(self, LineSeries):
    '''
    TotCol=MaxCol+ResidueCol
    '''
    
    PrintLine=LineSeries[0].row-self.__OffsetRow
    if PrintLine+1>self.__cursor_row: 
      self.__cursor_row=PrintLine
      self.__new_line=True
      
      # print index
      if self.Index is not None:
        self.Index.text=LineSeries.name
        self.__print_cell(self.Index, Index=True)
      
    else: self.__new_line=False

    LineSeries.map(self.__print_cell)
    
  # print header
  def __print_header(self):
    '''
    TotCol=MaxCol+ResidueCol
    '''
    
    self.__cursor_row=0
    self.__new_line=True
    
    self.__df.columns.map(lambda x: self.__print_cell(x, True))
    
  # get current cell value & type
  def __get_cell_value_type(self):
    Row=self.__TableRow-self.__OffsetRow
    Col=self.__TableCol-self.__OffsetCol
    colname=self.__df.columns[Col]
    value=self.__df.iloc[Row, Col].text
    dtype=type(value)
    return value, dtype, Row, colname

  # print bottom line
  def print_bottom_line(self, BeginTextPos=0, PrintColRow=0):
    '''
    PrintColRow=0: print value, 1: print col name, 2: print row number
    '''
    value, dtype, row, col=self.__get_cell_value_type()
    if len(col)>64: strcol=str(col)[:64]+'...'
    else: strcol=str(col)

    if len(str(row))>64: strrow=str(row)[:64]
    else: strrow=str(row)
    prompt='{'+str(dtype)+'} ['+strrow+', '+strcol+'] : '
    lprompt=len(prompt)
    try:
      self.__screen.addstr(self.__ScreenHeight-1, 0, prompt)
      cursor_x=self.__screen.getyx()[1]
      dw=self.__ScreenWidth-cursor_x
      if PrintColRow==1: value=col
      elif PrintColRow==2: value=row
      s=slice_str(str(value)[BeginTextPos:], dw)
      self.__screen.addstr(s)
      self.__screen.move(self.__ScreenHeight-1, 0)
    except: self.__screen.move(self.__ScreenHeight-1, self.__ScreenWidth-1)
    return value, dtype, row, col, self.__ScreenWidth-lprompt

  # print on screen
  def print(self):
    MaxRow=self.__MaxRow
    MaxCol=self.__MaxCol
    ResidueWidth=self.__ResidueWidth
    self.__screen.clear()
    self.__screen.move(0,0)
    
    EndCol=MaxCol+int(bool(ResidueWidth))
    pos.row=self.__OffsetRow
    pos.col=self.__OffsetCol
    if self.DF is not None: 
      df=self.DF.iloc[self.__OffsetRow:self.__OffsetRow+MaxRow, self.__OffsetCol:self.__OffsetCol+EndCol] # slice dataframe to the screen size
      self.__df=self.make_obj_df(df)
    else: self.__df=self.ObjDF.iloc[self.__OffsetRow:self.__OffsetRow+MaxRow, self.__OffsetCol:self.__OffsetCol+EndCol] # slice dataframe to the screen size
    
    self.__print_header()
    self.__df.apply(self.__print_line, axis=1)
    
class loop:
  scr=None
  quit=False

  def __init__(self): self.scr=cur.initscr()
  
  def run(self, BeginFunc=None, Func=None, EndFunc=None):
    
    # Initiate Screen
    cur.start_color()
    cur.use_default_colors()
    cur.noecho()
    cur.cbreak()
    self.scr.keypad(True)
    self.scr.clrtoeol()
  
    self.scr.nodelay(True)
    
    KeyInput=-1
    
    if BeginFunc: BeginFunc()
      
    while not self.quit:
      
      try: 
        KeyInput=self.scr.get_wch()
        self.scr.nodelay(True)
        self.scr.clear()
      except: 
        KeyInput=-1
        self.scr.nodelay(False)

      if Func: 
        
        Func(KeyInput)
      
        
    if EndFunc: EndFunc()
      
    # Quit Screen
    cur.nocbreak()
    self.scr.keypad(False)
    del self.scr
    cur.echo()
    cur.endwin() 

  def quit_screen(self):
    cur.nocbreak()
    self.scr.keypad(False)
    del self.scr
    cur.echo()
    cur.endwin() 

defaultBar=text_sec()
defaultCross=text_sec()
defaultIndex=text_sec()
defaultHeader=text_sec()

defaultBar.fcolor=12 # blue

defaultCross.fcolor=0
defaultCross.bcolor=255 # light grey
defaultCross.bold=True # select cell bold

defaultIndex.bcolor=250 # dark grey
defaultIndex.fcolor=52 # dark red

defaultHeader.fcolor=0
defaultHeader.bcolor=250 # dark grey
defaultHeader.bold=True # Header bold


HelpInfo={'Help Info:':
  [
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
  ' ',
  'Beyond a Screen (left hand):',
  's: move left a screen',
  'f: move right a screen',
  'd: move down a screen',
  'e: move up a screen',
  'g: move to the last column',
  'a: move to the first column',
  '3: move to the first row',
  'c: move to the last row',
  ' ',
  'On the bottom line (right hand):',
  'j: move left a letter',
  'l: move right a letter',
  'k: move to the end of the text',
  'i: move to the beginning of the text',
  ' ',
  'Others:',
  'y: show help & come back',
  'Q: quit'
  ]
}

class __handle_key_pv:
  Row=0
  Col=0
  CellWidth=None
  CellValue=None
  CellType=None
  CellRowNo=None
  CellColName=None
  BottomLineLength=None
  MaxRow=None
  MaxCol=None
  OffsetRow=None
  OffsetCol=None
  ScreenHeight=None
  ScreenWidth=None
  dfRows=None
  dfCols=None
  BeginTxtPos=None
  PrintColRow=0
  Quit=False

class __set_mode:
  Mode=0

modePV=__set_mode()
keyPV=__handle_key_pv()
hkeyPV=__handle_key_pv()


def handle_key(Key, TableObjs=None, keyPVs=None, Loop=None):
  t, h=TableObjs
  tkeyPV, hkeyPV=keyPVs
  
  if t is not None and modePV.Mode!=2: 
    TableObj=t
    keyPV=tkeyPV
  elif h is not None or modePV.Mode==2: 
    TableObj=h
    keyPV=hkeyPV
  keyPV.MaxRow, keyPV.MaxCol, keyPV.OffsetRow, keyPV.OffsetCol, keyPV.ScreenHeight, keyPV.ScreenWidth=TableObj.set_pos(keyPV.Row, keyPV.Col, keyPV.CellWidth)
  TableObj.print()
  keyPV.CellValue, keyPV.CellType, keyPV.CellRowNo, keyPV.CellColName, keyPV.BottomLineLength=TableObj.print_bottom_line(keyPV.BeginTxtPos, keyPV.PrintColRow)
   
  if Key=='Q': # quit view
    Loop.quit=True

  elif Key=='m':
    keyPV.BeginTxtPos=0
    if modePV.Mode==0: 
      modePV.Mode=1
    elif modePV.Mode==1: 
      modePV.Mode=0

  elif Key=='y':
    if modePV.Mode!=2: 
      modePV.Mode=2
      TableObj=h
      keyPV=hkeyPV
    else: 
      modePV.Mode=0
      TableObj=t
      keyPV=tkeyPV

  if modePV.Mode in (0, 2):
  
    if Key=='j': # move left a cell
      keyPV.Col=max(0, keyPV.Col-1)
    
    elif Key=='k':
      keyPV.Row=min(keyPV.dfRows-1, keyPV.Row+1)

    elif Key=='l':
      keyPV.Col=min(keyPV.dfCols-1, keyPV.Col+1)

    elif Key=='i':
      keyPV.Row=max(0, keyPV.Row-1)

    elif Key=='h':
      keyPV.Col=keyPV.OffsetCol

    elif Key==';':
      keyPV.Col=min(keyPV.dfCols-1, keyPV.OffsetCol+keyPV.MaxCol-1)

    elif Key=='8':
      keyPV.Row=keyPV.OffsetRow
    
    elif Key==',':
      keyPV.Row=min(keyPV.dfRows-1, keyPV.OffsetRow+keyPV.MaxRow-1)

    elif Key=='u':
      keyPV.PrintColRow=2

    elif Key=='o':
      keyPV.PrintColRow=1

    elif Key=='s':
      keyPV.Col=max(0, keyPV.Col-keyPV.MaxCol)
      t.set_offset(OffsetCol=keyPV.Col)
    
    elif Key=='f':
      keyPV.Col=min(keyPV.dfCols-1, keyPV.Col+keyPV.MaxCol)
      t.set_offset(OffsetCol=keyPV.Col)
    
    elif Key=='d':
      keyPV.Row=min(keyPV.dfRows-1, keyPV.Row+keyPV.MaxRow)
      t.set_offset(OffsetRow=keyPV.Row)

    elif Key=='e':
      keyPV.Row=max(0, keyPV.Row-keyPV.MaxRow)
      t.set_offset(OffsetRow=keyPV.Row)
    
    elif Key=='g':
      keyPV.Col=keyPV.dfCols-1

    elif Key=='a':
      keyPV.Col=0

    elif Key=='3':
      keyPV.Row=0

    elif Key=='c':
      keyPV.Row=keyPV.dfRows-1

    elif Key==']':
      keyPV.CellWidth=min(keyPV.ScreenWidth-2, keyPV.CellWidth+1)

    elif Key=='[':
      keyPV.CellWidth=max(1, keyPV.CellWidth-1)
  
  elif modePV.Mode==1: # bottom line string

    TxtLen=len(str(keyPV.CellValue))
    if Key=='j':
      keyPV.BeginTxtPos=max(0, keyPV.BeginTxtPos-1)

    elif Key=='l':
      keyPV.BeginTxtPos=min(TxtLen-1, keyPV.BeginTxtPos+1)
    
    elif Key=='k':
      keyPV.BeginTxtPos=TxtLen-keyPV.BottomLineLength
    
    elif Key=='i':
      keyPV.BeginTxtPos=0

def view(DataFrame=None, ObjDF=None, Bar=None, Cross=None, Index=None, Header=None, CellWidth=8):
  '''
  main function to show data frame
  DataFrame: DataFrame object for showing
  ObjDF: processed object_DataFrame, processed by make_obj_df(DataFrame)
  Bar=text_sec(): None: use default Index style
                  text_sec object to set up bar style: fcolor, mode, bcolor
  Cross=text_sec(): None: use default cross style
                    text_sec object to set up cross style:
                    fcolor & bcolor: set up cross forecolor (word color) & back color (background color) for the entire cross
                    mode: set up the select word mode (bold, etc.)
  Index: False: do not show index
         None: use default index
         text_sec: set up index style: fcolor, bcolor, mode
  Header: None: use default header style
          text_sec: setup header style: fcolor, bcolor, mode
  CellWidth: cell width
             None: entire line is the cell width
             int: set up the cell width
    
  '''
  if Bar is None: Bar=defaultBar
  
  if Cross is None:  Cross=defaultCross
  
  if Index is None: Index=defaultIndex
  elif Index==False: Index=None

  if Header is None: Header=defaultHeader

  #try:
  if True:
    lp=loop()

    # initialize DataFrame:
    if ObjDF is not None: 
      t=TableGrid(lp.scr, ObjDF=ObjDF)
      keyPV.dfRows, keyPV.dfCols=ObjDF.shape # numbers of rows & cols of dataframe
    elif DataFrame is not None: 
      t=TableGrid(lp.scr, DataFrame=DataFrame)
      keyPV.dfRows, keyPV.dfCols=DataFrame.shape # numbers of rows & cols of dataframe
    else: modePV.Mode=2
    
    if modePV.Mode!=2:
      t.Index=Index
      t.Cross=Cross
      t.Bar=Bar
      t.Header=Header
      
      # initialize to the first cell
      # numbers of rows & cols in a screen
      keyPV.MaxRow, keyPV.MaxCol, keyPV.OffsetRow, keyPV.OffsetCol, keyPV.ScreenHeight, keyPV.ScreenWidth=t.set_pos(0, 0, keyPV.CellWidth)
      
      keyPV.Row=0 # table row
      keyPV.Col=0 # table col
      
      modePV.Mode=0 # 0: table focus, 1: bottom line focus 2: help focus
      
      keyPV.CellWidth=min(keyPV.ScreenWidth-1, CellWidth)

      ###################

    # initialize HelpInfo:
    hdf=pd.DataFrame(HelpInfo)
    h=TableGrid(lp.scr, hdf)
    h.Index=None
    h.set_pos(0,0)

    h.Cross=defaultCross
    h.Bar=defaultBar
    h.Header=defaultHeader
    
    hkeyPV.MaxRow, hkeyPV.MaxCol, hkeyPV.OffsetRow, hkeyPV.OffsetCol, hkeyPV.ScreenHeight, hkeyPV.ScreenWidth=h.set_pos(0, 0, hkeyPV.CellWidth)
    
    hkeyPV.CellRow=0 # table row
    hkeyPV.CellCol=0 # table col
    
    hkeyPV.dfRows, hkeyPV.dfCols=hdf.shape # numbers of rows & cols of dataframe
        
    ####################

    lp.run(Func=lambda key: handle_key(key, (t, h), (keyPV, hkeyPV), lp))
  
  '''
  except Exception as e:
    lp.quit_screen()
    print(e)

  '''