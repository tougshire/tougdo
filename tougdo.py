from datetime import date, datetime,timedelta
import tkinter as tk
import re
import os
from pathlib import Path, WindowsPath
import configparser
from tkcalendar import DateEntry
from tkinter import filedialog as fd, messagebox


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

# adds an item from the edit widgets. Deletes it first if the item already exists
def item_add_update():

    global items

    entry = edit_entry_var.get().strip()

    if entry:

        item = {}

        if edit_iscomplete_var.get() == 'x':

            item['is_completed'] = 'x'
            item['completion_date'] = date.today().isoformat()
        
        else:
            item['is_completed'] = ''
            item['completion_date'] = ''

        item['priority'] = ''
        priority = edit_priority_var.get()
        if priority > '' and priority in letters:
            item['priority'] = priority

        item['creation_date'] = ''
        creationdate = edit_creationdate_var.get()
        iso_creationdate = get_iso_date( creationdate )
        if re.match( date_iso_pattern, iso_creationdate):
            item['creation_date'] = iso_creationdate

        item['due'] = ''
        due = edit_due_var.get()    
        iso_due = get_iso_date( due )
        if re.match( date_iso_pattern, iso_due):
            item['due'] = iso_due

        item['text'] = edit_entry_var.get()

        for i, find_item in enumerate( items ):
            if find_item['line_text'] == edit_linetext_var.get():
                deleted_item = items.pop( i )
                break

        item['line_text'] = item_to_text( item )

        items.append(item)
        
        items_sort()
        file_save()
        main_refresh()
        main_find_item( item['line_text'] )
        main_text_widget.focus_set()

        edit_linetext_var.set('')

def item_new():

    edit_entry_widget.focus_set()
    edit_entry_var.set('')
    edit_linetext_var.set('')

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

def item_edit( delete='' ):
    
    global items

    line_text, line_start, line_end = get_line_text_from_main()

    #find the item who's line_text matches the line in the main widget at the cursor
    for i, item in enumerate( items ):
        if item['line_text'] == line_text:
            if delete == 'DELETE':
                found_item = items.pop(i)
                main_refresh()
            else:
                found_item = items[i]
            break

    try:
        edit_iscomplete_var.set( found_item['is_completed'] )
        edit_completiondate_var.set( found_item['completion_date'] )
        edit_priority_var.set( found_item['priority'] )
        edit_creationdate_var.set( found_item['creation_date'] )
        edit_due_var.set( found_item['due'] )
        edit_entry_var.set( found_item['text'] )

        edit_linetext_var.set( line_text )

        edit_entry_widget.focus_set()

        file_save()

    except UnboundLocalError:
        messagebox.showerror("There was an error finding the item.  You may have to refresh or restart the app")

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
        elif iso_date == 'next week':
            nextweek = date.today() + timedelta( days=7)
            iso_date = nextweek.isoformat()
        elif iso_date == 'next month':
            nextmonth = date.today() + timedelta( weeks=4 )
            while not nextmonth.day == date.today().day:
                nextmonth = nextmonth + timedelta( days=1 )
                iso_date = nextmonth.isoformat()
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

    pattern = 'due:((' +  date_iso_pattern  + ')|today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next week|next month)'
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

def filter_clear():

    filter_priority_var.set('')
    filter_text_var.set('')
    filter_contextprojects_var.set('')
    main_refresh()

def main_handle_keys( e ):

    if e.keysym == 'Tab':
        if e.state & 0x1: #shift key pressed
            e.widget.tk_focusPrev().focus()
#            filter_text_widget.focus_set()
        else:
            e.widget.tk_focusNext().focus()
#            edit_entry_widget.focus_set()
        return "break"

    if e.state & 0x4: #control key pressed
        if e.keysym == 'c':
            item_set_complete()
            return "break"
        if e.keysym == 'd':
            item_edit()
            edit_due_widget.focus_set()
            edit_due_widget.select_range( 0, tk.END )
            return "break"
        if e.keysym == 'e':
            item_edit()
            return "break"
        if e.keysym == 'p':
            item_edit()
            edit_priority_widget.focus_set()
            edit_priority_widget.select_range( 0, tk.END )
            return "break"
        if e.keysym == 'x':
            item_edit('DELETE')
            return "break"


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

def main_find_item( line_text ):

    pos = main_text_widget.search( line_text, "1.0", stopindex=tk.END  )
    if pos:
        main_text_widget.focus_set()
        main_text_widget.mark_set(tk.INSERT, pos)
        main_text_widget.see(pos)

def main_refresh():

    global items

    pos = main_text_widget.index(tk.INSERT)
    filter_text = filter_text_var.get()
    filter_priority = filter_priority_var.get()
    filter_contextprojects_string = filter_contextprojects_var.get().lower()
  
    main_text = ''

    if items:

        previous_due = items[0]['due']
        for item in items:

            show = 1

            if show:
                if filter_text_var.get():
                    if not filter_text.lower() in item['text'].lower():
                        show = 0

            if show:
                if filter_priority:
                    if not item['priority'].lower() in filter_priority.lower():
                        show = 0

            if show:
                if filter_contextprojects_string:
                    #starting with 'test @one +two @three +three'
                    #item_context_projects should be [ '@one', '+two' '@three', '+three' ]
                    item_contexts_projects = re.findall( '(?:@|\+)\w+', item['text'] )

                    #starting with 'test @one, +two; three'
                    #filter_context_projects should be [ 'test', @one', '+two', 'three' ]
                    filter_contexts_projects = re.split('\s*,\s*|\s*;\s*|\s+', filter_contextprojects_string)


                    #starting with [ 'test', '@one', '+two', 'three' ]
                    #filter_contexts will be [ '@test', '@one', '@three' ] and filter_projects will be [ '+test', '+two', '+three' ]
                    filter_projects = []
                    filter_contexts = []
                    for filter_part in filter_contexts_projects:
                        if filter_part[0:1] == '@':
                            filter_contexts.append( filter_part )
                        if filter_part[0:1] == '+':
                            filter_projects.append( filter_part )
                        elif re.match('[A-Za-z]', filter_part[0:1]):
                            filter_contexts.append( '@' + filter_part )
                            filter_projects.append( '+' + filter_part )

                    anymatch = 0
                    for filter_context in filter_contexts:
                        if filter_context in item_contexts_projects:
                            anymatch = 1    
                    for filter_project in filter_projects:
                        if filter_project in item_contexts_projects:
                            anymatch = 1    

                    show = anymatch

            if show:
                if previous_due != item['due']:
                    main_text = main_text + '\n'
                    previous_due = item['due']

                main_text = main_text + item['line_text'] + '\n'

    main_text_widget.delete( "1.0", tk.END )
    main_text_widget.insert( "1.0", main_text )
    main_text_widget.mark_set( tk.INSERT, pos )



todo_txt_file, backup_path = file_get_paths()

# some utility variables
# produces a list of one empty string followed by each letter surrounded by parentheses
letters = [''] + [ chr(chr_num) for chr_num in range(65,91) ]
date_iso_pattern = '\d{4}-\d\d-\d\d'

if __name__ == "__main__":

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
    main_text_widget.bind('<KeyPress>', lambda e: main_handle_keys(e))
    main_text_widget.unbind('<Control-d')
    # main_text_widget.bind('<Control-d>', lambda x: item_delete_by_text())
    # main_text_widget.bind('<Control-e>', lambda x: item_edit())

    message_var = tk.StringVar()
    message_entry = tk.Entry(message_frame, width=80, textvariable=message_var)
    message_entry.pack(side="right")
    message_entry.pack_forget()

    edit_entry_label = tk.Label( edit_frame, text='entry' )
    edit_entry_label.pack(side="left")
    edit_entry_var = tk.StringVar()
    edit_entry_widget = tk.Entry( edit_frame, textvariable=edit_entry_var, width=40 )
    edit_entry_widget.pack( side='left' )
    edit_entry_widget.bind('<Return>', lambda x: item_add_update())

    edit_priority_label = tk.Label( edit_frame, text='priority' )
    edit_priority_label.pack( side='left' )
    edit_priority_var = tk.StringVar()
    edit_priority_widget = tk.Entry( edit_frame, textvariable=edit_priority_var, width=2 )
    edit_priority_widget.pack( side='left' )
    edit_priority_widget.bind('<KeyPress>', lambda e: edit_set_priority(e))

    edit_due_label = tk.Label( edit_frame, text='due' )
    edit_due_label.pack( side='left' )
    edit_due_var = tk.StringVar()
    edit_due_widget = tk.Entry( edit_frame, textvariable=edit_due_var )
    edit_due_widget.pack( side='left' )
    edit_due_widget.bind('<Return>', lambda x: item_add_update())

    edit_iscomplete_label = tk.Label( edit_frame, text='is complete' )
    edit_iscomplete_label.pack( side='left' )
    edit_iscomplete_var = tk.StringVar()
    edit_iscomplete_widget = tk.Checkbutton( edit_frame, variable=edit_iscomplete_var, onvalue='x', offvalue='')
    edit_iscomplete_widget.pack( side='left' )

    edit_completiondate_var = tk.StringVar()

    edit_creationdate_var = tk.StringVar()

    edit_linetext_var = tk.StringVar()

    edit_apply = tk.Button( edit_frame, text='apply', command=item_add_update )
    edit_apply.pack(side='left')
    edit_apply.bind('<Return>', lambda x: item_add_update())

    filter_text_label = tk.Label(search_frame,text="filter text")
    filter_text_label.pack(side="left")
    filter_text_var = tk.StringVar()
    filter_text_widget = tk.Entry(search_frame, textvariable=filter_text_var)
    filter_text_widget.pack(side="left")
    filter_text_widget.bind('<Return>', lambda x: main_refresh())
    filter_text_widget.bind('<KeyRelease>', lambda x: main_refresh())

    filter_priority_label = tk.Label(search_frame,text="filter priority")
    filter_priority_label.pack(side="left")
    filter_priority_var = tk.StringVar()
    filter_priority_widget = tk.Entry(search_frame, textvariable=filter_priority_var, width=5)
    filter_priority_widget.pack(side="left")
    filter_priority_widget.bind('<Return>', lambda x: main_refresh())
    filter_priority_widget.bind('<KeyRelease>', lambda x: main_refresh())

    filter_contextprojects_label = tk.Label(search_frame,text="filter contexts & projects")
    filter_contextprojects_label.pack(side="left")
    filter_contextprojects_var = tk.StringVar()
    filter_contextprojects = tk.Entry(search_frame, textvariable=filter_contextprojects_var, width=5)
    filter_contextprojects.pack(side="left")
    filter_contextprojects.bind('<Return>', lambda x: main_refresh())
    filter_contextprojects.bind('<KeyRelease>', lambda x: main_refresh())

    filter_clear_button = tk.Button( search_frame, text='Clear Filters', command=filter_clear )
    filter_clear_button.pack(side="left")

    root.bind('<Control-s>', lambda x: file_save() )
    root.bind('<Control-r>', lambda x: main_refresh() )
    root.bind('<Control-n>', lambda x: item_new() )
    root.unbind('<Control-d')
    root.bind('<Control-f>', lambda x: filter_text_widget.focus_set() )
    root.bind('<Control-m>', lambda x: main_text_widget.focus_set() )

    items = []

    file_get_items()

    main_refresh()

    main_text_widget.focus_set()

    root.mainloop()