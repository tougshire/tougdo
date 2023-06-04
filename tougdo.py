from datetime import date, datetime,timedelta
import tkinter as tk
import re
import os
from pathlib import Path, PurePath
import configparser
from tkinter import filedialog, messagebox

def edit_reset_widgets():

    edit_linetext_var.set('')
    edit_entry_var.set('')
    edit_iscomplete_var.set('')
    edit_priority_var.set('')
    edit_due_var.set('')

    edit_entry_widget.configure( state='normal')
    edit_iscomplete_widget.configure( state='normal')
    edit_due_widget.configure( state='normal')
    edit_priority_widget.configure( state='normal')

    return "break"

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

def edit_new():

    edit_entry_widget.focus_set()
    edit_entry_var.set('')
    edit_linetext_var.set('')

def get_iso_date(datestr):

        weekday_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        datestr = datestr.lower().strip()

        iso_date = re.match( DATE_ISO_PATTERN, datestr )
        if iso_date:
            return iso_date.group(0)

        if datestr == 'today':
            return date.today().isoformat()

        if datestr == 'tomorrow':
            return (date.today() + timedelta(days=1)).isoformat()

        if datestr == 'next week':
            nextweek = date.today() + timedelta( days=7)
            return nextweek.isoformat()

        if datestr == 'next month':
            nextmonth = date.today() + timedelta( weeks=4 )
            while not nextmonth.day == date.today().day:
                nextmonth = nextmonth + timedelta( days=1 )
                return nextmonth.isoformat()

        if datestr in weekday_names:
            weekday_number = weekday_names.index(datestr)
            for d in range(1,8):
                nextday = date.today() + timedelta(days = d)                     
                if nextday.weekday() == weekday_number:
                    return nextday.isoformat()

        if datestr[0:len('next')] == 'next':
            weekday_name = datestr[len('next') + 1:]
            if weekday_name in weekday_names:
                weekday_number = weekday_names.index(weekday_name)
                for d in range(1,8):
                    nextday = date.today() + timedelta(days = d)                     
                    if nextday.weekday() == weekday_number:
                        return ( nextday + timedelta( days=7 ) ).isoformat()

        return ''

def get_line_text_from_main():

    current_pos = main_text_widget.index(tk.INSERT)
    split_pos = current_pos.split('.')
    line_start = '{}.{}'.format(split_pos[0], '0')
    line_end = '{}.{}'.format(split_pos[0], tk.END)
    item_line = main_text_widget.get(line_start, line_end)

    return [item_line, line_start, line_end]

def parse_completion( item_text ):

    item_text = item_text.strip()
    completion_marker = ''
    completion_date = ''

    #if the item is complete, it has an 'x ' a the beginning.  the completion date is optional but if it exists, it follows the 'x '
    pattern = '^(?P<marker>x\s)\s*(?P<date>' + DATE_ISO_PATTERN + ')*'
    
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
    pattern = '^((?P<prior>\([A-Z]\))\s+)*(?P<target>' + DATE_ISO_PATTERN + ')'
    match = re.search( pattern, item_text, flags=re.I )
    if match:
        # replace the whole match with the part of the match which came before the target
        prior = match['prior'] if match['prior'] else ''        
        item_text = re.sub( pattern, prior, item_text, flags=re.I)
        creation_date = match['target']

    # for completed tasks, created date can follow the completed date
    pattern = '^(?P<prior>x\s'   + DATE_ISO_PATTERN +  '\s+)(?P<target>' + DATE_ISO_PATTERN + ')'
    match = re.search( pattern, item_text )
    if match:
        item_text = re.sub( pattern, match['prior'], item_text, flags=re.I )
        creation_date = match['target']

    # match key value format used in main_text_widget
    pattern = 'created:(' + DATE_ISO_PATTERN +  ')'
    match = re.search( pattern, item_text, flags=re.I )
    if match:
        item_text = re.sub( pattern, '', item_text, flags=re.I )
        #will take priority over txt_match
        creation_date = match[1]

    item_text = item_text.strip()

    return[creation_date, item_text]

def parse_due(item_text):

    pattern = 'due:((' +  DATE_ISO_PATTERN  + ')|today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next week|next month)'
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

def filter_clear():

    filter_priority_var.set('')
    filter_text_var.set('')
    filter_contexts_projects_var.set('')
    main_refresh()

def main_handle_keys( e ):

    if e.keysym == 'Tab':
        if e.state & 0x1: #shift key pressed
            e.widget.tk_focusPrev().focus()
        else:
            e.widget.tk_focusNext().focus()
        return "break"


    elif e.state & 0x4: #control key pressed
        if e.keysym == 'd':
            todolist.edit_item( get_line_text_from_main()[0] )
            edit_due_widget.focus_set()
            edit_due_widget.select_range( 0, tk.END )
            return "break"
        if e.keysym == 'D':
            todolist.delete_item( get_line_text_from_main()[0] )
        if e.keysym == 'e':
            todolist.edit_item( get_line_text_from_main()[0] )
            edit_entry_widget.focus_set()
            return "break"
        if e.keysym == 'p':
            todolist.edit_item( get_line_text_from_main()[0] )
            edit_priority_widget.focus_set()
            edit_priority_widget.select_range( 0, tk.END )
            return "break"
        if e.keysym == 'x':
            todolist.set_complete( get_line_text_from_main()[0] )
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

    pos = main_text_widget.index(tk.INSERT)
    filter_text = filter_text_var.get()
    filter_priority = filter_priority_var.get()
    filter_contexts_projects_string = filter_contexts_projects_var.get().lower()

    todolist.sort_items()

    main_text = ''
    items = todolist.get_items()

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
                    filter_priority = filter_priority.lower()
                    item['priority'] = item['priority'].lower()
                    if not item['priority'] in filter_priority:
                        show = 0
                    if show == 0:
                        matches = re.findall( '([a-z]{1})\s*\.+\s*([a-z]{1})', filter_priority )
                        for match in matches:
                            for p in range( ord( match[ 0 ] ) + 1, ord( match[ 1 ] )):
                                if item['priority'] == chr(p):
                                    show = 1
                                    break;

            if show:
                if filter_contexts_projects_string:
                    #starting with 'test @one +two @three +three'
                    #item_context_projects should be [ '@one', '+two' '@three', '+three' ]
                    item_contexts = re.findall( '(?:@)\w+', item['text'] )
                    item_projects = re.findall( '(?:\+)\w+', item['text'] )
                    item_contexts_projects = item_contexts + item_projects

                    #starting with 'test @one, +two; three'
                    #filter_context_projects should be [ 'test', @one', '+two', 'three' ]
                    filter_contexts_projects = re.split('\s*,\s*|\s*;\s*|\s+', filter_contexts_projects_string)

                    #starting with [ 'test', '@one', '+two', 'three' ]
                    #filter_contexts will be [ '@test', '@one', '@three' ] and filter_projects will be [ '+test', '+two', '+three' ]
                    filter_projects = []
                    filter_contexts = []
                    match_no_context = False
                    match_no_project = False
                    for filter_part in filter_contexts_projects:
                        if filter_part[0:1] == '@':
                            filter_contexts.append( filter_part )
                        if filter_part[0:1] == '+':
                            filter_projects.append( filter_part )
                        elif re.match('[A-Za-z]', filter_part[0:1]):
                            filter_contexts.append( '@' + filter_part )
                            filter_projects.append( '+' + filter_part )
                        elif filter_part == '-@':
                            match_no_context = True
                        elif filter_part == '-+':
                            match_no_project = True
                        
                    anymatch = 0
                    
                    if anymatch == 0:   # I just do this first one to keep all of the tests in line
                        if match_no_context and not item_contexts:
                            anymatch = 1
                    if anymatch == 0:
                        if match_no_project and not item_projects:
                            anymatch = 1                    
                    if anymatch == 0:
                        for filter_context in filter_contexts:
                            if filter_context in item_contexts_projects:
                                anymatch = 1    
                    if anymatch == 0:
                        for filter_project in filter_projects:
                            if filter_project in item_contexts_projects:
                                anymatch = 1    

                    show = anymatch

            if show:
                if filter_completed_var.get() and item['is_completed'] == 'x':
                    show = 0

            if show:
                if previous_due != item['due']:
                    main_text = main_text + '\n'
                    previous_due = item['due']

                main_text = main_text + item['line_text'] + '\n'

    main_text_widget.delete( "1.0", tk.END )
    main_text_widget.insert( "1.0", main_text )
    main_text_widget.mark_set( tk.INSERT, pos )

def main_save_sel_range():

    start_pos = str( main_text_widget.tag_ranges('sel')[0] ).split('.')[0] + '.0'
    end_pos = str( int( str( main_text_widget.tag_ranges('sel')[1] ).split('.')[0] ) + 1 ) + '.0'
    main_text_widget.tag_add('selected', start_pos, end_pos )
    return [ start_pos, end_pos ]

def main_unset_selection():

    main_text_widget.tag_remove('selected', '1.0', tk.END )
    

def unset_and_reset():

    main_unset_selection()
    edit_reset_widgets()

class Config():

    def __init__( self ):

        config_dir = Path.home() / '.tougdo' 
        self.config_path = str(config_dir / 'tougdo.conf')

        self.config = configparser.ConfigParser()

        if not Path.exists( config_dir ):
            Path.mkdir( config_dir )

        config_file = open( self.config_path, 'a+')
        config_file.close()
        self.config.read( self.config_path )
 
    def reset_todo( self ):

        todo_found = False

        while not todo_found:

            todo_folder = filedialog.askdirectory( title='Select todo.txt Folder')
            todo_found = True
            self.config.setdefault( 'files', {} )
            self.config['files']['todo.txt'] = str( PurePath( todo_folder ) / 'todo.txt' )
            config_file = open( self.config_path, 'w' )
            self.config.write( config_file )
            config_file.close()

    def get_todo( self ):

        todo_found = False

        try:
            todo_txt = open( self.config['files']['todo.txt'], 'a+' )
            todo_found = True            
            todo_txt.close()

        except ( KeyError, PermissionError ):
            pass

        if not todo_found:
            
            self.reset_todo()

        return self.config['files']['todo.txt']

    def reset_backup( self ):

        backup_dir_found = False

        while not backup_dir_found:

            backup_folder = filedialog.askdirectory( title='Select backup Folder')
            open( Path( backup_folder ) / 'temp.txt', 'w' )
            backup_dir_found = True
            self.config.setdefault( 'files', {} )
            self.config['files']['backup_dir'] = str( PurePath( backup_folder ) )
            config_file = open( self.config_path, 'w' )
            self.config.write( config_file )
            config_file.close()

    def get_backup_path( self ):

        backup_found = False

        try:

            backup_dir_writeable = open( Path( self.config['files']['backup_dir'] ) / 'temp.txt', 'w' )
            backup_found = True            

        except ( KeyError, PermissionError ):
            pass

        if not backup_found:
            self.reset_backup()

        return self.config['files']['backup_dir']
    
class TodoList():
    
    def __init__( self ):
        self.items = []

    #finds and item based on the items line
    def find_item( self, line_text=None, index=None  ):

        item = None
        i = None

        if index is not None:
            found_item = self.items[ index ]
            # if line_text is provided, double check to make sure the text matches
            if line_text is not None:
                if found_item['line_text'] == line_text:
                    item = found_item
                    i = index

        elif line_text is not None:
            for found_i, found_item in enumerate( self.items):
                if found_item['line_text'] == line_text:
                    item = found_item
                    i = found_i
                    break

        return [ item, i ]

    #finds and item based on the items line
    def find_items( self, tag_ranges ):

        pos_start = tag_ranges[0].string.split('.')[0] + '.0'
        pos_end = str( int( tag_ranges[1].string.split('.')[0] ) + 1 ) + '.0'

        line_texts = main_text_widget.get( pos_start, pos_end ).split('\n')

        items = []
        idxs = []

        for line_text in line_texts:
            if line_text is not None:
                for found_i, found_item in enumerate( self.items):
                    if found_item['line_text'] == line_text:
                        items.append( found_item )
                        idxs.append = found_i
          
        return [ items, idxs ]

    def edit_items( self ):

        ranges = main_save_sel_range()
        line_texts = main_text_widget.get(ranges[0], ranges[1]).split('\n')

        item = self.parse_item( line_texts[0] )
        edit_iscomplete_var.set( item['is_completed'] )
        edit_completiondate_var.set( item['completion_date'] )
        edit_priority_var.set( item['priority'] )
        edit_creationdate_var.set( item['creation_date'] )
        edit_due_var.set( item['due'] )
        edit_entry_var.set( item['text'] )
        
        line_texts.pop(0)

        for line_text in line_texts:
            try:
                item = self.parse_item( line_text )
                if item['is_completed'] != edit_iscomplete_var.get():
                    edit_iscomplete_var.set('')
                    #for completed, disable if they're not all the same
                    edit_iscomplete_widget.configure( state='disabled')
                if item['priority'] != edit_priority_var.get():
                    edit_priority_var.set('')
                if item['due'] != edit_due_var.get():
                    edit_due_var.set('')
                if item['text'] != edit_entry_var.get():
                    edit_entry_var.set('')
            except KeyError:
                pass

            edit_entry_widget.configure( state='disabled')

    def edit_item( self, line_text ):

        if  main_text_widget.tag_ranges('sel'):
            self.edit_items()
            return

        #find the item who's line_text matches the line in the main widget at the cursor

        item, i = self.find_item( line_text ) 

        if item:

            edit_iscomplete_var.set( item['is_completed'] )
            edit_completiondate_var.set( item['completion_date'] )
            edit_priority_var.set( item['priority'] )
            edit_creationdate_var.set( item['creation_date'] )
            edit_due_var.set( item['due'] )
            edit_entry_var.set( item['text'] )

            edit_linetext_var.set( line_text )

            edit_entry_widget.focus_set()

            self.sort_items()
            main_refresh()
            self.save()

        return "break"

    def add_update_item( self ):
        # adds an item from the edit widgets. Deletes it first if the item already exists

        # if selected items in main, leave and go to update_items()
        if main_text_widget.tag_ranges('selected'):
            self.update_items()
            return 'break'
        
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
            if priority > '' and priority in LETTERS:
                item['priority'] = priority

            item['creation_date'] = ''
            creationdate = edit_creationdate_var.get()
            iso_creationdate = get_iso_date( creationdate )
            if re.match( DATE_ISO_PATTERN, iso_creationdate):
                item['creation_date'] = iso_creationdate

            item['due'] = ''
            due = edit_due_var.get().strip()
            if due > '':
                item['due'] = get_iso_date( due )
                if item['due'] == '':
                    messagebox.showerror( 'Date Error', 'There was a problem with the due date.  The item has been added without a due date')

            item['text'] = edit_entry_var.get()

            for i, find_item in enumerate( self.items ):
                if find_item['line_text'] == edit_linetext_var.get():
                    self.items.pop( i )
                    break

            item['line_text'] = self.item_to_text( item )

            self.items.append(item)

            edit_linetext_var.set('')
            edit_entry_var.set('')
            edit_iscomplete_var.set('')

            self.sort_items() 
            main_refresh()
            self.save()

            main_find_item( item['line_text'] )

            main_text_widget.focus_set()

    def update_items( self ):

        ranges = main_save_sel_range()

        line_texts = main_text_widget.get(ranges[0], ranges[1]).split('\n')

        for line_text in line_texts:

            item, i = self.find_item( line_text )

            if(item):

                if edit_iscomplete_widget.cget('state') != 'disabled':
                    if edit_iscomplete_var.get() == 'x':
                        self.items[i]['is_completed'] = 'x'
                        self.items[i]['completion_date'] = date.today().isoformat()
                    else:
                        self.items[i]['is_completed'] = ''
                        self.items[i]['completion_date'] = ''

                priority = edit_priority_var.get()
                if priority > '' and priority in LETTERS:
                    self.items[i]['priority'] = priority

                due = edit_due_var.get().strip()
                if due > '':
                    self.items[i]['due'] = get_iso_date( due )
                    if item['due'] == '':
                        messagebox.showerror( 'Date Error', 'There was a problem with the due date.  The item has been added without a due date')

                self.items[i]['line_text'] = self.item_to_text( self.items[i] )

        edit_reset_widgets()
        main_unset_selection()

        self.sort_items()
        main_refresh()
        self.save()

        main_text_widget.focus_set()

    def delete_item( self, line_text = None, i = None ):

        item, i = self.find_item( line_text, i )
        if item:
            if messagebox.askokcancel('Delete?', 'Delete ' + item['text'] + '?'):
                self.items.pop( i )
                self.sort_items()
                main_refresh()
                self.save()
            else:
                messagebox.showinfo('Canceled', 'Item was not deleted')

    def set_complete( self, line_text ):
        
        item, i = self.find_item( line_text )

        if item:
            self.items[i]['is_completed'] = 'x' if self.items[i]['is_completed'] == '' else ''
            self.items[i]['line_text'] = self.item_to_text(item)

        self.sort_items()
        main_refresh()
        self.save() 


    def set_complete( self, line_text ):
        
        item, i = self.find_item( line_text )

        if item:
            self.items[i]['is_completed'] = 'x' if self.items[i]['is_completed'] == '' else ''
            self.items[i]['line_text'] = self.item_to_text(item)

        self.sort_items()
        main_refresh()
        self.save() 


    def item_to_text(self, item ):

        line_text = ''

        if item['is_completed']:

            line_text = line_text + 'x '
            line_text = line_text + item['completion_date'] + ' '

            line_text = line_text + item['text'] + ' '

            if item['priority']:
                line_text = line_text + 'pri:' + item['priority'] + ' '

            if item['creation_date']:
                line_text = line_text + 'created:' + item['creation_date'] + ' '

            if item['due']:
                line_text = line_text + 'due:' + item['due'] + ' '

        else: # if not completed

            if item['priority']:
                line_text = line_text + '(' + item['priority'] + ') '

            if item['due']:
                line_text = line_text + 'due:' + item['due'] + ' '

            line_text = line_text + item['text'] + ' '

            if item['creation_date']:
                line_text = line_text + 'created:' + item['creation_date'] + ' '

        line_text = line_text.strip()
        return line_text

    def parse_item( self, line_text ):

        item = {}

        if line_text:

            item['is_completed'], item['completion_date'], line_text = parse_completion(line_text)
            item['priority'], line_text = parse_priority(line_text)
            item['creation_date'], line_text = parse_creation(line_text)
            item['due'], line_text = parse_due(line_text)
            item['text'] = line_text.strip()

        return item

    def get_items( self ):

        return self.items
    
    def load_items( self ):

        items = []
        f = open( config.get_todo() , "r" )
        data = f.read()
        f.close()
        file_lines = data.split('\n')

        for file_line in file_lines:

            if file_line:
                item = self.parse_item( file_line )
                item['line_text'] = self.item_to_text( item )
        
                items.append( item )

        self.sort_items( items )

    def save( self ):

        main_text = ''

        self.sort_items()

        for item in self.items:
            main_text = main_text + item['line_text'] + '\n'

        f = open( config.get_todo() , "w")
        f.write( main_text )
        f.close()
        for backnum in range(5,1,-1):
            older_backup_name = 'todo_back_{}.txt'.format( backnum )
            newer_backup_name = 'todo_back_{}.txt'.format( backnum - 1)
            n = open( Path( config.get_backup_path() ) / newer_backup_name, 'a+')

            n.seek(0)
            contents = n.read()
            n.close()
            o = open( Path( config.get_backup_path() ) / older_backup_name, 'w')
            o.write(contents)
            o.close()
        backup_name = 'todo_back_1.txt'    
        b = open( Path( config.get_backup_path() ) / backup_name , "w")
        b.write( main_text )
        b.close()

    def sort_items( self, items=None, sort_by=['is_completed', 'due', 'priority'] ):

        if items is None:
            items = self.items

        self.items = sorted( items, key=lambda i: ( i[ sort_by[0] ], i[ sort_by[1] ], i[ sort_by[2] ] ) )

        return self.items



# some utility variables
# produces a list of one empty string followed by each letter surrounded by parentheses
LETTERS = [''] + [ chr(chr_num) for chr_num in range(65,91) ]
DATE_ISO_PATTERN = '\d{4}-\d\d-\d\d'

config = Config()
todolist = TodoList()

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

    main_text_widget = tk.Text( main_frame,  width=300, undo=True )
    main_text_widget.pack(expand='yes')
    main_text_widget.bind('<KeyPress>', lambda e: main_handle_keys(e))
    main_text_widget.unbind('<Control-d')
    # main_text_widget.bind('<Control-d>', lambda x: item_delete_by_text())
    # main_text_widget.bind('<Control-e>', lambda x: item_edit())

    message_var = tk.StringVar()
    message_entry = tk.Entry(message_frame, width=80, textvariable=message_var)
    message_entry.pack(side="right")

    edit_entry_label = tk.Label( edit_frame, text='entry' )
    edit_entry_label.pack(side="left", padx=(10,0))
    edit_entry_var = tk.StringVar()
    edit_entry_widget = tk.Entry( edit_frame, textvariable=edit_entry_var, width=40 )
    edit_entry_widget.pack( side='left' )
    edit_entry_widget.bind('<Return>', lambda x: todolist.add_update_item() )

    edit_priority_label = tk.Label( edit_frame, text='priority' )
    edit_priority_label.pack( side='left', padx=(10,0) )
    edit_priority_var = tk.StringVar()
    edit_priority_widget = tk.Entry( edit_frame, textvariable=edit_priority_var, width=2 )
    edit_priority_widget.pack( side='left' )
    edit_priority_widget.bind('<KeyPress>', lambda e: edit_set_priority(e))

    edit_due_label = tk.Label( edit_frame, text='due' )
    edit_due_label.pack( side='left' , padx=(10,0))
    edit_due_var = tk.StringVar()
    edit_due_widget = tk.Entry( edit_frame, textvariable=edit_due_var )
    edit_due_widget.pack( side='left' )
    edit_due_widget.bind('<Return>', lambda x: todolist.add_update_item())

    edit_iscomplete_label = tk.Label( edit_frame, text='is complete' )
    edit_iscomplete_label.pack( side='left', padx=(10,0) )
    edit_iscomplete_var = tk.StringVar()
    edit_iscomplete_widget = tk.Checkbutton( edit_frame, variable=edit_iscomplete_var, onvalue='x', offvalue='')
    edit_iscomplete_widget.pack( side='left' )

    edit_completiondate_var = tk.StringVar()

    edit_creationdate_var = tk.StringVar()

    edit_linetext_var = tk.StringVar()

    edit_apply = tk.Button( edit_frame, text='apply', command=todolist.add_update_item )
    edit_apply.pack(side='left')
    edit_apply.bind('<Return>', lambda x: todolist.add_update_item())

    filter_text_label = tk.Label(search_frame,text="filter text")
    filter_text_label.pack(side="left", padx=(10,0) )
    filter_text_var = tk.StringVar()
    filter_text_widget = tk.Entry(search_frame, textvariable=filter_text_var)
    filter_text_widget.pack(side="left")
    filter_text_widget.bind('<Return>', lambda x: main_refresh())
    filter_text_widget.bind('<Control-f>', lambda x: filter_clear())
    filter_text_widget.bind('<KeyRelease>', lambda x: main_refresh())

    filter_priority_label = tk.Label(search_frame,text="filter priority")
    filter_priority_label.pack(side="left", padx=(10,0))
    filter_priority_var = tk.StringVar()
    filter_priority_widget = tk.Entry(search_frame, textvariable=filter_priority_var, width=5)
    filter_priority_widget.pack(side="left")
    filter_priority_widget.bind('<Return>', lambda x: main_refresh())
    filter_priority_widget.bind('<KeyRelease>', lambda x: main_refresh())

    filter_contexts_projects_label = tk.Label(search_frame,text="filter contexts & projects")
    filter_contexts_projects_label.pack(side="left", padx=(10,0))
    filter_contexts_projects_var = tk.StringVar()
    filter_contexts_projects = tk.Entry(search_frame, textvariable=filter_contexts_projects_var, width=15)
    filter_contexts_projects.pack(side="left")
    filter_contexts_projects.bind('<Return>', lambda x: main_refresh())
    filter_contexts_projects.bind('<KeyRelease>', lambda x: main_refresh())

    filter_completed_var = tk.IntVar()
    filter_completed_widget = tk.Checkbutton( search_frame, variable=filter_completed_var, text='hide completed', onvalue=1, offvalue=0, command=main_refresh )
    filter_completed_widget.pack( side='left' )

    filter_clear_button = tk.Button( search_frame, text='Clear Filters', command=filter_clear )
    filter_clear_button.pack(side="left")

    root.bind('<Control-s>', lambda x: todolist.save() )
    root.bind('<Control-r>', lambda x: main_refresh() )
    root.bind('<Control-n>', lambda x: edit_new() )
    root.unbind('<Control-d')
    root.bind('<Control-f>', lambda x: filter_text_widget.focus_set() )
    root.bind('<Control-m>', lambda x: main_text_widget.focus_set() )
    root.bind('<Escape>', lambda x: unset_and_reset() )

    todolist.load_items()

    main_refresh()

    main_text_widget.focus_set()

    root.mainloop()