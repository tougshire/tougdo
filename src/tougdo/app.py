"""
A Python application for Todo.txt
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from pathlib import Path, PurePath
import configparser
from datetime import date, datetime,timedelta
import re

LETTERS = [''] + [ chr(chr_num) for chr_num in range(65,91) ]
DATE_ISO_PATTERN = '\d{4}-\d\d-\d\d'

def get_iso_date( datestr='' ):

        weekday_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        datestr = datestr.lower().strip()

        iso_date = re.match( DATE_ISO_PATTERN, datestr )
        if iso_date:
            return iso_date.group(0)

        if datestr == 'today' or datestr == '':
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

        self.window = toga.Window()
 

    async def reset_todo( self, window ):

        todo_folder = await window.select_folder_dialog('select_folder')
        
        if todo_folder is not None:
            self.config.setdefault( 'files', {} )
            self.config['files']['todo.txt'] = str(Path( todo_folder ) / 'todo.txt' )
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

        # if not todo_found:
            
        #     self.reset_todo()

        return self.config['files']['todo.txt']

    def reset_backup( self ):

        backup_dir_found = False

        while not backup_dir_found:

            backup_folder = toga.Window.select_folder_dialog( title='Select backup Folder')
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
        self.config = Config()

    def get_items( self, filter_description=None, filter_priority=None ):

        filtered_items = []

        if filter_description is not None or filter_priority is not None:
            print('tp236a914')
            for item in self.items:
                pass_item = True

                if pass_item: #this first test just keeps everything else lined up
                    if filter_description is not None:
                        if not filter_description.lower() in item['description'].lower():
                            pass_item = False

                if pass_item: 
                    if filter_priority is not None:
                        if not item['priority'].lower() in filter_priority:
                            pass_item = False

                if pass_item:
                    filtered_items.append( item )

            return filtered_items
  
        return self.items

    def load_items( self ):

        self.items = []
        f = open( self.config.get_todo() , "r" )
        data = f.read()
        f.close()
        file_lines = data.split('\n')

        for file_line in file_lines:

            if file_line:
                item = self.parse_item( file_line )
                item['line_text'] = self.item_to_text( item )
        
                self.items.append( item )

        self.sort_items()

    def save( self ):

        self.sort_items()

        main_text = ''
        items = self.items

        if items:

            for item in items:
                main_text = main_text + item['line_text'] + '\n'

        f = open( self.config.get_todo() , "w")
        f.write( main_text )
        
    def item_to_text(self, item ):

        line_text = ''

        if item['is_completed']:

            line_text = line_text + 'x '
            line_text = line_text + item['completion_date'] + ' '

            line_text = line_text + item['description'] + ' '

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

            line_text = line_text + item['description'] + ' '

            if item['creation_date']:
                line_text = line_text + 'created:' + item['creation_date'] + ' '

        line_text = line_text.strip()
        return line_text


    def parse_item( self, line_text ):

        item = {}

        if line_text:

            item['is_completed'], item['completion_date'], line_text = self.parse_completion(line_text)
            item['priority'], line_text = self.parse_priority(line_text)
            item['creation_date'], line_text = self.parse_creation(line_text)
            item['due'], line_text = self.parse_due(line_text)
            item['description'] = line_text.strip()

        return item

    def parse_completion( self, item_text ):

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

    def parse_creation(self, item_text):

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

    def parse_due( self, item_text ):

        pattern = 'due:((' +  DATE_ISO_PATTERN  + ')|today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next week|next month)'
        match = re.search(pattern, item_text, flags=re.I)
        duedate = ''

        if match:
            duedate = get_iso_date(match[1])
            item_text = re.sub(match[0], '', item_text, re.I)

        return[ duedate, item_text ]

    def parse_priority( self, item_text ):

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

    def sort_items( self, items=None, sort_by=['is_completed', 'due', 'priority'] ):

        if items is None:
            items = self.items

        self.items = sorted( items, key=lambda i: ( i[ sort_by[0] ], i[ sort_by[1] ], i[ sort_by[2] ],  ) )

        return self.items
    
    def set_complete( self, itemid ):

        if self.items[ itemid ]['is_completed'] == '':
            self.items[ itemid ]['is_completed'] = 'x'
            self.items[ itemid ]['completion_date'] == get_iso_date()            
        else:
            self.items[ itemid ]['is_completed'] = ''
            self.items[ itemid ]['completion_date'] == ''

        self.items[ itemid ]['line_text'] = self.item_to_text( self.items[ itemid ] )
        self.sort_items()

    def update_item( self, itemid, is_completed, description, due, priority ):
        
        itemid = int( itemid )

        if not 'creation_date' in self.items[ itemid ]:
            self.items[ itemid ]['creation_date'] = ''

        if is_completed:
            self.items[ itemid ][ 'is_completed' ] = 'x'
            if self.items[ itemid ]['completion_date'] == '':
                self.items[ itemid ]['completion_date'] == get_iso_date()
        else:
            self.items[ itemid ][ 'is_completed' ] = ''
            self.items[ itemid ]['completion_date'] = ''

        self.items[ itemid ]['description'] = description

        self.items[ itemid ]['priority'] = ''
        if priority > '' and priority in LETTERS:
            self.items[ itemid ]['priority'] = priority

        self.items[ itemid ]['due'] = due
        if due > '':
            self.items[ itemid ]['due'] = get_iso_date( due )

        self.items[ itemid ]['line_text'] = self.item_to_text( self.items[ itemid ] )

        self.sort_items()

    def add_item( self, is_completed, description, due, priority ):
        
        new_item = {}

        new_item['creation_date'] = get_iso_date()

        if is_completed:
            new_item[ 'is_completed' ] = 'x'
            if new_item['completion_date'] == '':
                new_item['completion_date'] == get_iso_date()
        else:
            new_item[ 'is_completed' ] = ''
            new_item['completion_date'] = ''

        new_item['description'] = description

        new_item['priority'] = ''
        if priority > '' and priority in LETTERS:
            new_item['priority'] = priority

        new_item['due'] = due
        if due > '':
            new_item['due'] = get_iso_date( due )

        new_item['line_text'] = self.item_to_text( new_item )

        self.items.append( new_item )

        self.sort_items()

class TougshireTodotxt(toga.App):

    def main_refresh( self ):

        filter_description = self.filter_description_widget.value if self.filter_description_widget.value > '' else None
        filter_priority = self.filter_priority_widget.value if self.filter_priority_widget.value > '' else None

        items = self.todolist.get_items( filter_description, filter_priority )

        new_data = []
                
        try:
            previous_due = items[0]['due']
        except IndexError:
            return

        for itemid, item in enumerate( items ):

            if previous_due != item['due']:
                new_data.append(("-", "", "", "",""))
                previous_due = item['due']

            new_data.append(
                (
                    item['is_completed'], 
                    item['priority'], 
                    item['due'], 
                    item['description'],
                    itemid
                )
            )

        self.item_table.data = new_data
        self.edit_description_widget.focus()
        self.item_table.focus()

    def find_item( self, complete, due, description, priority ):
        for itemid, item in enumerate( self.todolist.get_items() ):
            if item['is_completed'] == complete and item['due'] == due and item['description'] == description and item['priority'] == priority:
                return( itemid )

        return None

    def edit_new_item( self ):

            self.edit_is_completed_widget.value= ''
            self.edit_due_widget.value= ''
            self.edit_priority_widget.value= ''
            self.edit_description_widget.value= ''
            self.edit_itemid_widget.value= ''
            self.edit_addnew_widget.value = True
            self.edit_addnew_widget.enabled = False

    # copies the item into the edit box so it can be edited
    def edit_item( self ):
        if self.item_table.selection:
            row = self.item_table.selection

            self.edit_is_completed_widget.value = row.complete
            self.edit_due_widget.value = row.due
            self.edit_priority_widget.value = row.priority
            self.edit_description_widget.value = row.description

            self.edit_itemid_widget.value = self.find_item( row.complete, row.due, row.description, row.priority )

            self.edit_addnew_widget.value = False
            self.edit_addnew_widget.enabled = True

        else:
            self.edit_new_item()

    def callback_table_on_select( self, table, row ):
        self.edit_item( )

    def callback_filter_description( self, command ):
        self.main_refresh()
        self.filter_description_widget.focus()

    def callback_filter_priority( self, command ):
        self.main_refresh()
        self.filter_priority_widget.focus()

    def callback_apply_item( self, command ):

        if self.edit_addnew_widget.value:
            self.todolist.add_item( 
                is_completed=self.edit_is_completed_widget.value,
                description=self.edit_description_widget.value, 
                due=self.edit_due_widget.value, 
                priority=self.edit_priority_widget.value
            )

        else:
            if self.edit_itemid_widget.value > '': 
                self.todolist.update_item( 
                    itemid=self.edit_itemid_widget.value,
                    is_completed=self.edit_is_completed_widget.value,
                    description=self.edit_description_widget.value, 
                    due=self.edit_due_widget.value, 
                    priority=self.edit_priority_widget.value
                )

        self.main_refresh()

    def callback_save( self, command ):
        self.todolist.save()

    def callback_edit_item( self, command ):

        self.edit_item()
        self.edit_description_widget.focus()

    def callback_edit_new_item( self, command ):

        self.edit_new_item()
        self.edit_description_widget.focus()

    async def callback_configure_todo( self, command ):
        await self.config.reset_todo( self.main_window )

    def callback_set_complete( self, command ):
        self.todolist.set_complete( int(self.edit_itemid_widget.value) )
        self.main_refresh()

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.main_box = toga.Box(style=Pack(direction=COLUMN, width="1000", height=600, flex=1))

    
        edit_box = toga.Box(style=Pack(direction=ROW, width="1000", flex=1))

        edit_label_box = toga.Box(style=Pack(direction=COLUMN))
        edit_label_label = toga.Label('edit:', style=Pack(font_weight="bold"))
        edit_label_box.add( edit_label_label )
        edit_box.add( edit_label_box )

        edit_description_box = toga.Box(style=Pack(direction=COLUMN))
        edit_description_label = toga.Label('description')
        self.edit_description_widget = toga.TextInput()
        edit_description_box.add(edit_description_label)
        edit_description_box.add(self.edit_description_widget)
        edit_box.add(edit_description_box)

        edit_priority_box = toga.Box(style=Pack(direction=COLUMN))
        edit_priority_label = toga.Label('priority')
        self.edit_priority_widget = toga.TextInput(style=Pack(width=20))
        edit_priority_box.add(edit_priority_label)
        edit_priority_box.add(self.edit_priority_widget)
        edit_box.add(edit_priority_box)

        edit_due_box = toga.Box(style=Pack(direction=COLUMN))
        edit_due_label = toga.Label('due')
        self.edit_due_widget = toga.TextInput()
        edit_due_box.add(edit_due_label)
        edit_due_box.add(self.edit_due_widget)
        edit_box.add(edit_due_box)

        edit_is_completed_box = toga.Box(style=Pack(direction=COLUMN))
        edit_is_completed_label = toga.Label('completed')
        self.edit_is_completed_widget = toga.Switch('')
        edit_is_completed_box.add(edit_is_completed_label)
        edit_is_completed_box.add(self.edit_is_completed_widget)
        edit_box.add(edit_is_completed_box)

        edit_addnew_box = toga.Box(style=Pack(direction=COLUMN))
        edit_addnew_label = toga.Label('add new ')
        self.edit_addnew_widget = toga.Switch('')
        edit_addnew_box.add( edit_addnew_label )
        edit_addnew_box.add( self.edit_addnew_widget )
        edit_box.add( edit_addnew_box )        

        edit_apply_box = toga.Box(style=Pack(direction=COLUMN))
        edit_apply_label = toga.Label(' ')
        edit_apply_button = toga.Button('apply', on_press=self.callback_apply_item)
        edit_apply_box.add( edit_apply_label )
        edit_apply_box.add( edit_apply_button )
        edit_box.add( edit_apply_box )        

        self.edit_itemid_widget = toga.TextInput()

        self.main_box.add(edit_box)

        filter_box = toga.Box(style=Pack(direction=ROW, width="1000", flex=1))

        filter_label_box = toga.Box(style=Pack(direction=COLUMN))
        filter_label_label = toga.Label('filter:', style=Pack(font_weight="bold"))
        filter_label_box.add( filter_label_label )
        filter_box.add( filter_label_box )


        filter_description_box = toga.Box(style=Pack(direction=COLUMN))
        filter_description_label = toga.Label('description')
        self.filter_description_widget = toga.TextInput( on_change=self.callback_filter_description )
        filter_description_box.add(filter_description_label)
        filter_description_box.add(self.filter_description_widget)
        filter_box.add(filter_description_box)



        filter_priority_box = toga.Box(style=Pack(direction=COLUMN))
        filter_priority_label = toga.Label('priority')
        self.filter_priority_widget = toga.TextInput(style=Pack(width=30), on_change=self.callback_filter_priority )
        filter_priority_box.add(filter_priority_label)
        filter_priority_box.add(self.filter_priority_widget)
        filter_box.add(filter_priority_box)

        filter_due_box = toga.Box(style=Pack(direction=COLUMN))
        filter_due_label = toga.Label('due')
        self.filter_due_widget = toga.TextInput()
        filter_due_box.add(filter_due_label)
        filter_due_box.add(self.filter_due_widget)
        filter_box.add(filter_due_box)

        filter_is_completed_box = toga.Box(style=Pack(direction=COLUMN))
        filter_is_completed_label = toga.Label('completed')
        self.filter_is_completed_widget = toga.Switch('')
        filter_is_completed_box.add(filter_is_completed_label)
        filter_is_completed_box.add(self.filter_is_completed_widget)
        filter_box.add(filter_is_completed_box)

        filter_apply_box = toga.Box(style=Pack(direction=COLUMN))
        filter_apply_label = toga.Label(' ')
        filter_apply_button = toga.Button('apply', on_press=self.callback_apply_item)
        filter_apply_box.add( filter_apply_label )
        filter_apply_box.add( filter_apply_button )
        filter_box.add( filter_apply_box )        

        self.filter_itemid_widget = toga.TextInput()

        self.main_box.add(filter_box)

        self.item_table = toga.Table( ['Complete','Priority', 'Due', 'Description'], missing_value='', style=Pack(width='1000', height=500), on_select=self.callback_table_on_select)
        self.main_box.add( self.item_table )


        self.todolist = TodoList()
        self.config = Config()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()


        group_configure = toga.Group("Configure", order=2)

        command_configure_todo = toga.Command(
            self.callback_configure_todo,
            text = "Todo Folder",
            group=group_configure
        )

        command_edit_new_item = toga.Command(
            self.callback_edit_new_item,
            text = 'New',
            shortcut = toga.Key.MOD_1 + 'n',
        )
        command_edit_item = toga.Command(
            self.callback_edit_item,
            text = 'Edit',
            shortcut = toga.Key.MOD_1 + 'e',
        )
        command_update_item = toga.Command(
            self.callback_apply_item,
            text = 'Apply\u0332',
            shortcut = toga.Key.MOD_1 + 'y',
        )
        command_set_complete = toga.Command(
            self.callback_set_complete,
            text = 'Set Complete (x\u0332)',
            shortcut = toga.Key.MOD_1 + 'x',
        )
        command_save = toga.Command(
            self.callback_save,
            text = 'Save',
            shortcut = toga.Key.MOD_1 + 's',
            group=toga.Group.FILE
        )

        self.commands.add( command_edit_new_item )
        self.commands.add( command_edit_item )
        self.commands.add( command_update_item )
        self.commands.add( command_save)
        self.commands.add( command_configure_todo )
        self.commands.add( command_set_complete )

        self.todolist.load_items()

        self.main_refresh()


def main():
    return TougshireTodotxt()
