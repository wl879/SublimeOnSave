# encoding: UTF-8
import sublime, sublime_plugin

def create(mode = 'right', size = 0, win = None, max = 3, col = -1):
    if not win:
        win = sublime.active_window()
    layout = win.layout()
    cells  = layout['cells']
    cols   = layout['cols']
    rows   = layout['rows']
    num    = len( cells )
    if mode == 'bottom':
        if len( rows ) <= max:
            if col == -1:
                col = len(cols) - 2
            cells.append( [col, 999, 0, 0] )
        else:
            return get(mode, win, col)
    else:
        if len( cols ) <= max:
            if mode == 'left':
                for cell in cells:
                    cell[0] += 1
                cells.append( [0, 0, 0, 0] )
            else:
                cells.append( [999, 999, 0, 0] )
        else:
            return get(mode, win, col)

    col_num, row_num = checkGroupCells(cells, cols, rows)
    if row_num > len(rows) -1:
        addGroupSize( rows, size )
    if col_num > len(cols) -1:
        addGroupSize( cols, size )
    win.set_layout(layout)
    return len(cells) - 1

def get(mode = 'right', win = None, col = None):
    if not win:
        win = sublime.active_window()
    layout = win.layout()
    cells  = layout['cells']
    col_num = col or len(layout['cols'] ) - 2
    row_num = len(layout['rows'] ) - 2
    for gid in range(0, len(cells)):
        cell = cells[gid]
        if mode == 'bottom':
            if cell[0] == col_num and cell[1] == row_num:
                return gid
        elif mode == 'left':
            if cell[0] == 0 and cell[1] ==0:
                return gid
        else:
            if cell[0] == col_num and cell[1] ==0:
                return gid
    return len(cells) - 1

def move(form, to, win = None ):
    if not win:
        win = sublime.active_window()
    win.focus_group( to )
    views = win.views_in_group( form )[:]
    for i in range(len(views)-1, -1, -1):
        setGroup(views[i], to)

def delete(gid, win = None):
    if not win:
        win = sublime.active_window()
    layout = win.layout()
    cells  = layout['cells']
    cols   = layout['cols']
    rows   = layout['rows']
    num    = len( cells )
    if num > 1:
        the_cell = cells[ gid ]
        del cells[ gid ]
        col_num, row_num = checkGroupCells(cells, cols, rows)
        if col_num < len(cols) -1:
            delGroupSize( cols, the_cell[0] )
        if row_num < len(rows) -1:
            delGroupSize( rows, the_cell[1] - 1 )
        win.set_layout(layout)
        win.settings().set('last_automatic_layout', cells)

def isempty(gid, win = None):
    if not win:
        win = sublime.active_window()
    views = win.views_in_group( gid )
    if len(views):
        return False
    return True

def addGroupSize(data, size = 0):
    if not size:
        size = 1 / len(data)
    if len(data) <= 2:
        data.insert( 1, 1 - size)
    else:
        offset = size / (len(data) - 1)
        for i in range(1, len(data) -1 ):
            data[i] -= offset
        data.insert( -1, 1 - size )
    return data

def delGroupSize(data, index = 0):
    del data[ index + 1 ]
    if len(data) < 2:
        data.append(1.0)
    data[0] = 0.0
    data[-1] = 1.0

def checkGroupCells( cells, cols, rows ):
    col_num = 0
    row_num = 0
    cache   = []

    # check colume
    total   = len(cells)
    index   = 0
    while total > 0:
        col_cells = getGroupCols(cells, index)
        if col_cells:
            for cell in col_cells: 
                cell[0] = col_num
                cell[2] = col_num + 1
            cache.append(col_cells)
            col_num += 1
            row_num = max( row_num, len(col_cells) )
            total -= len( col_cells )
        index += 1

    # check row
    for col_cells in cache:
        row_len   = len(col_cells)

        for i in range(row_len-1, -1, -1):
            cell = col_cells[i]
            if i == row_len - 1:
                cell[3] = row_num
            else:
                next_cell = col_cells[ i+1 ]
                if cell[3] >= next_cell[3]:
                    cell[3] = next_cell[3] - 1
                next_cell[1] = cell[3]
            if i == 0:
                cell[1] = 0

    return (col_num, row_num)

def getGroupCols( cells, col_index ):
    cols = []
    for item in cells:
        if col_index == item[0]:
            cols.append(item)
    if len(cols):
        cols = sorted(cols, key=lambda x:x[1])
        return cols

def setGroup(view, gid):
    win = view.window()
    sublime.set_timeout(lambda:  win.set_view_index(view, gid, 0), 100)