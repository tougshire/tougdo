from datetime import date, datetime,timedelta
import tkinter as tk
import re
import os
from pathlib import Path, WindowsPath
import configparser
from tkcalendar import DateEntry
from tkinter import filedialog as fd

def edit_set_priority(e):

    if re.match('[A-Za-z]$', e.keysym):
        edit_priority_var.set( e.keysym.upper())
        return "break"
    elif e.keysym == 'space':
        edit_priority_var.set('')
        return "break"
    elif len( e.keysym ) == 1:
        return "break"
    # this matches keysyms like 'period', 'bracketleft', 'greater', etc...
    # keys like 'Return', 'Tab' 'F4', 'Escape' are generally capitalized, so won't trigger return "break"
    elif re.match('[a-z]',e.keysym[0:1]):
        return "break"

def item_add():

    global items

    entry = edit_entry.get().strip()

    if entry:

        item = {}

        if edit_iscomplete_var.get() == 'x':

            item['is_completed'] = 'x'
            item['completion_date'] = date.today().isoformat()
        
        else:
            item['is_completed'] = ''
            item['completion_date'] = ''

        item['priority'] = ''
        priority_var = edit_priority_var.get()
        if priority_var > '' and priority_var in letters:
            item['priority'] = priority_var

        item['creation_date'] = ''
        creationdate_var = edit_creationdate_var.get()
        iso_creationdate_var = get_iso_date( creationdate_var )
        if re.match( date_iso_pattern, iso_creationdate_var):
            item['creation_date'] = iso_creationdate_var

        item['due'] = ''
        due_var = edit_due_var.get()    
        iso_due_var = get_iso_date( due_var )
        if re.match( date_iso_pattern, iso_due_var):
            item['due'] = iso_due_var

        item['text'] = entry

        item['line_text'] = item_to_text( item )

        items.append(item)
        items_sort()
        file_save()
        main_refresh()

def item_delete_by_text():
    
    global items

    line_text, line_start, line_end = get_line_text_from_main()

    for i, item in enumerate( items ):
        if item['line_text'] == line_text:
            deleted_item = items.pop( i )
            break
    
    edit_iscomplete_var.set( 'x' if deleted_item['is_completed'] else '' )
    edit_completiondate_var.set( deleted_item['completion_date'] )
    edit_priority_var.set( deleted_item['priority'] )
    edit_creationdate_var.set( deleted_item['creation_date'] )
    edit_due_var.set( deleted_item['due'] )
    edit_entry_var.set( deleted_item['text'] )

    edit_entry.focus_set()

    file_save()

    return "break"

def item_set_complete():

    global items
    
    line_text, line_start, line_end = get_line_text_from_main()

    for i, item in enumerate( items ):
        if item['line_text'] == line_text:
            items[i]['is_completed'] = 'x' if items[i]['is_completed'] == '' else ''
            items[i]['line_text'] = item_to_text(item)
            break

    items_sort()
    file_save()
    main_refresh()

def item_to_text( item ):

    working_text = ''

    if item['is_completed']:

        working_text = working_text + 'x '
        working_text = working_text + item['completion_date'] + ' '

        working_text = working_text + item['text'] + ' '

        if item['priority']:
            working_text = working_text + 'pri:' + item['priority'] + ' '

        if item['creation_date']:
            working_text = working_text + 'created:' + item['creation_date'] + ' '

        if item['due']:
            working_text = working_text + 'due:' + item['due'] + ' '

    else: # if not completed

        if item['priority']:
            working_text = working_text + '(' + item['priority'] + ') '

        if item['due']:
            working_text = working_text + 'due:' + item['due'] + ' '

        working_text = working_text + item['text'] + ' '

        if item['creation_date']:
            working_text = working_text + 'created:' + item['creation_date'] + ' '

    return working_text

def items_sort():

    global items

    items = sorted( items, key=lambda i: ( i['is_completed'], i['due'], i['priority'] ) )

def get_iso_date(datestr):

        weekday_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        iso_date = datestr.lower()
        if iso_date == 'today':
            iso_date = date.today().isoformat()
        elif iso_date == 'tomorrow':
            iso_date = (date.today() + timedelta(days=1)).isoformat()
        elif iso_date in weekday_names:
            weekday_number = weekday_names.index(iso_date)
            for d in range(1,8):
                nextday = date.today() + timedelta(days = d)                     
                if nextday.weekday() == weekday_number:
                    iso_date = nextday.isoformat()

        return iso_date

def get_line_text_from_main():

    current_pos = main_text_widget.index(tk.INSERT)
    split_pos = current_pos.split('.')
    line_start = '{}.{}'.format(split_pos[0], '0')
    line_end = '{}.{}'.format(split_pos[0], tk.END)
    item_line = main_text_widget.get(line_start, line_end)

    return [item_line, line_start, line_end]

def parse_completion(item_text):

    item_text = item_text.strip()
    completion_marker = ''
    completion_date = ''

    #if the item is complete, it has an 'x ' a the beginning.  the completion date is optional but if it exists, it follows the 'x '
    pattern = '^(?P<marker>x\s)\s*(?P<date>' + date_iso_pattern + ')*'
    
    match=re.search( pattern, item_text, flags=re.I )

    if match:

        item_text = re.sub( pattern, '', item_text, flags=re.I)
        completion_marker = 'x' if match['marker'] else ''
        completion_date = match['date'] if match['date'] else ''

    return[ completion_marker, completion_date, item_text.strip() ]

def parse_creation(item_text):

    item_text = item_text.strip()
    creation_date = ''

    # for uncompleted tasks, created date can be at the beginning or following the priority
    pattern = '^((?P<prior>\([A-Z]\))\s+)*(?P<target>' + date_iso_pattern + ')'
    match = re.search( pattern, item_text, flags=re.I )
    if match:
        # replace the whole match with the part of the match which came before the target
        prior = match['prior'] if match['prior'] else ''        
        item_text = re.sub( pattern, prior, item_text, flags=re.I)
        creation_date = match['target']

    # for completed tasks, created date can follow the completed date
    pattern = '^(?P<prior>x\s'   + date_iso_pattern +  '\s+)(?P<target>' + date_iso_pattern + ')'
    match = re.search( pattern, item_text )
    if match:
        item_text = re.sub( pattern, match['prior'], item_text, flags=re.I )
        creation_date = match['target']

    # match key value format used in main_text_widget
    pattern = 'created:(' + date_iso_pattern +  ')'
    match = re.search( pattern, item_text, flags=re.I )
    if match:
        item_text = re.sub( pattern, '', item_text, flags=re.I )
        #will take priority over txt_match
        creation_date = match[1]

    item_text = item_text.strip()

    return[creation_date, item_text]

def parse_due(item_text):

    pattern = 'due:((' +  date_iso_pattern  + ')|today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
    match = re.search(pattern, item_text, flags=re.I)
    duedate = ''

    if match:
        duedate = get_iso_date(match[1])

        item_text = re.sub(match[0], '', item_text, re.I)

    return[ duedate, item_text ]

def parse_priority(item_text):

    item_text = item_text.strip()
    priority = ''

    parenth_pattern = '^\(([A-Z])\)'
    regmatch=re.search(parenth_pattern, item_text, flags=re.I)

    if regmatch:
        priority = regmatch[1]
        item_text = re.sub( parenth_pattern, '', item_text )

    key_pattern = 'pri:([A-Z])\\b'
    regmatch=re.search( key_pattern, item_text, flags=re.I )

    if regmatch:
        priority = regmatch[1].upper().strip()
        item_text = re.sub( regmatch[0], '', item_text )

    item_text = item_text.strip()

    return[priority, item_text]

def parse_item( item ):

    parsed_item = {}
    if item:
        item_text = item

        parsed_item['is_completed'], parsed_item['completion_date'], item_text = parse_completion(item_text)
        parsed_item['priority'], item_text = parse_priority(item_text)
        parsed_item['creation_date'], item_text = parse_creation(item_text)
        parsed_item['due'], item_text = parse_due(item_text)
        parsed_item['text'] = item_text.strip()

    return parsed_item

def file_get_items():

    global items

    f = open(todo_txt_file , "r")
    data = f.read()
    f.close()
    file_items = data.split('\n')
    items=[]

    for file_item in file_items:

        if file_item:
            item = parse_item( file_item )
            item['line_text'] = item_to_text( item )
    
            items.append( item )

    items = sorted( items, key=lambda i: ( i['is_completed'], i['due'], i['priority'] ) )

def file_get_paths():

    config_files = [
        Path.cwd() / 'config' / 'tougdo.conf',
        Path.cwd() / 'config' / 'tougdo.config',
        Path.home() / '.tougdo' / 'tougdo.conf',
        Path.home() / '.tougdo' / 'tougdo.config',
    ]

    conf_parser = configparser.ConfigParser()
    conf_parser.read(config_files)

    try:
        todo_txt_file = conf_parser['todo.txt']['todo.txt_file']
    except KeyError:
        todo_txt_file = Path.home() / 'todo.txt'

    f = open(todo_txt_file, 'r')

    try:
        backup_path = conf_parser['todo.txt']['backup_path']
    except KeyError:
        backup_path = Path.home() 

    f = open( Path(backup_path) / 'todo_backup_test', 'w')

    return [ todo_txt_file, backup_path ]

def file_save():

    global items

    main_text = ''

    for item in items:
        main_text = main_text + item['line_text'] + '\n'

    f = open( todo_txt_file , "w")
    f.write( main_text )
    f.close()
    for backnum in range(5,1,-1):
        older_backup_name = 'todo_back_{}.txt'.format( backnum )
        newer_backup_name = 'todo_back_{}.txt'.format( backnum - 1)
        n = open(Path(backup_path) / newer_backup_name, 'a+')
        n.seek(0)
        contents = n.read()
        n.close()
        o = open(Path(backup_path) / older_backup_name, 'w')
        o.write(contents)
        o.close()
    backup_name = 'todo_back_1.txt'    
    b = open(Path(backup_path) / backup_name , "w")
    b.write(main_text)
    b.close()

def main_ignore_keys( e ):

    good_keys = [
        'Up',
        'Down',
        'Left',
        'Right',
    ]
    good_keys = good_keys + [ 'F{}'.format( n ) for n in range(1,25) ] # allowing for some unusual situation where there are more than 12 F keys

    if not e.state & 0x4: #control key pressed
        if not e.keysym in good_keys:
            return "break"

    return e.keysym

def main_refresh():

    global items

    pos = main_text_widget.index(tk.INSERT)

    main_text = ''

    if items:

        previous_due = items[0]['due']
        for item in items:
            if previous_due != item['due']:
                main_text = main_text + '\n'
                previous_due = item['due']

            main_text = main_text + item['line_text'] + '\n'

    main_text_widget.delete( "1.0", tk.END )
    main_text_widget.insert( "1.0", main_text )
    main_text_widget.mark_set( tk.INSERT, pos )


def edit_focus():
    widget = root.focus_get()
    if widget == main_text_widget:
        edit_entry.focus_set()
    else:
        main_text_widget.focus_set()

def search( direction='forward' ):

    pos = main_text_widget.index(tk.INSERT)    
    if not pos > "":
        pos = "1.0"

    if 'found' in main_text_widget.tag_names():
        if direction == 'reverse':
            if pos == "1.0":
                pos = tk.END
            else:
                pos = pos + " - 1 char"
        else:
            if pos == tk.END:
                pos = "1.0"
            else:
                pos = pos + " + 1 char"

        main_text_widget.mark_set(tk.INSERT, pos)

    main_text_widget.tag_delete('found')
    main_text_widget.tag_config('found', background='yellow')
    searchstring = search_var.get()
    if direction == 'reverse':
        pos = main_text_widget.search(searchstring, pos, stopindex='1.0', backwards=True, nocase=True,  )
    else:
        pos = main_text_widget.search(searchstring, pos, stopindex=tk.END, nocase=True,  )

    if pos == "":
        pos = main_text_widget.search(searchstring, "1.0", stopindex=tk.END, nocase=True )

    if pos:
        main_text_widget.tag_add('found', pos, '%s+%dc' % (pos, len(searchstring)))
        main_text_widget.focus_set()
        main_text_widget.mark_set(tk.INSERT, pos)
        main_text_widget.see(pos)

def main_return_key( direction='forward' ):

    if 'found' in main_text_widget.tag_names():
        search( direction )

    return "break"

todo_txt_file, backup_path = file_get_paths()


# some utility variables
# produces a list of one empty string followed by each letter surrounded by parentheses
letters = [''] + [ chr(chr_num) for chr_num in range(65,91) ]
date_iso_pattern = '\d{4}-\d\d-\d\d'

root = tk.Tk()
root.title('Tougshore To Do List')
font=('Calibri 35')

# Set up frames
main_frame = tk.Frame( root )
main_frame.pack( expand=1, fill="both" )

message_frame = tk.Frame( root )
message_frame.pack()


edit_frame = tk.Frame( root )
edit_frame.pack()

search_frame = tk.Frame( root )
search_frame.pack()

main_text_widget = tk.Text( main_frame,  width=400, undo=True )
main_text_widget.pack(pady=20, expand='yes')
main_text_widget.bind('<KeyPress>', lambda e: main_ignore_keys(e))
main_text_widget.unbind('<Control-d')
main_text_widget.bind('<Control-d>', lambda x: item_delete_by_text())
main_text_widget.bind('<Return>', lambda x: main_return_key())
main_text_widget.bind('<Control-Return>', lambda x: main_return_key('reverse'))
main_text_widget.bind('<Tab>', lambda x: "break")

message_var = tk.StringVar()
message_entry = tk.Entry(message_frame, width=80, textvariable=message_var)
message_entry.pack(side="right")
message_entry.pack_forget()

edit_entry_label = tk.Label( edit_frame, text='entry' )
edit_entry_label.pack(side="left")
edit_entry_var = tk.StringVar()
edit_entry = tk.Entry( edit_frame, textvariable=edit_entry_var, width=40 )
edit_entry.pack( side='left' )

edit_priority_label = tk.Label( edit_frame, text='priority' )
edit_priority_label.pack( side='left' )
edit_priority_var = tk.StringVar()
edit_priority = tk.Entry( edit_frame, textvariable=edit_priority_var, width=2 )
edit_priority.pack( side='left' )
edit_priority.bind('<KeyPress>', lambda e: edit_set_priority(e))

edit_due_label = tk.Label( edit_frame, text='due' )
edit_due_label.pack( side='left' )
edit_due_var = tk.StringVar()
edit_due = tk.Entry( edit_frame, textvariable=edit_due_var )
edit_due.pack( side='left' )

edit_iscomplete_label = tk.Label( edit_frame, text='is complete' )
edit_iscomplete_label.pack( side='left' )
edit_iscomplete_var = tk.StringVar()
edit_iscomplete = tk.Checkbutton( edit_frame, variable=edit_iscomplete_var, onvalue='x', offvalue='')
edit_iscomplete.pack( side='left' )

edit_completiondate_label = tk.Label( edit_frame, text='completion date' )
edit_completiondate_label.pack( side='left' )
edit_completiondate_var = tk.StringVar()
edit_completiondate = tk.Entry( edit_frame, textvariable=edit_completiondate_var )
edit_completiondate.pack( side='left' )
edit_completiondate_label.pack_forget()
edit_completiondate.pack_forget()

edit_creationdate_label = tk.Label( edit_frame, text='creation date' )
edit_creationdate_label.pack( side='left' )
edit_creationdate_var = tk.StringVar()
edit_creationdate = tk.Entry( edit_frame, textvariable=edit_creationdate_var )
edit_creationdate.pack( side='left' )
edit_creationdate_label.pack_forget()
edit_creationdate.pack_forget()

edit_apply = tk.Button( edit_frame, text='apply', command=item_add )
edit_apply.pack(side='left')
edit_apply.bind('<Return>', lambda x: item_add())

search_var = tk.StringVar()
search_entry = tk.Entry(search_frame, textvariable=search_var)
search_entry.pack(side="right")
search_entry_label = tk.Label(search_frame,text="search")
search_entry_label.pack(side="right")
search_entry.bind('<Return>', lambda x: search())

root.bind('<Control-s>', lambda x: file_save())
root.bind('<Control-r>', lambda x: main_refresh())
root.bind('<Control-n>', lambda x: edit_entry.focus_set())
root.bind('<Control-x>', lambda x: item_set_complete())
root.unbind('<Control-d')
root.bind('<Control-f>', lambda x: search_entry.focus_set())
root.bind('<Control-e>', lambda x: edit_focus())

items = []

file_get_items()

main_refresh()

main_text_widget.focus_set()

root.mainloop()