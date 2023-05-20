from datetime import date, timedelta
import tkinter as tk
import re
import os
from pathlib import Path, WindowsPath
import configparser
from tkcalendar import DateEntry
from tkinter import filedialog as fd

class TougDateEntry(DateEntry):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.bind('<space>', self.space_press)
        self._calendar.bind('<Right>', self.right_press)
        self._calendar.bind('<Left>', self.left_press)
        self._calendar.bind('<space>', self.space_press)
  
    def _validate_date(self):

        #prior to the default validation, convert some convenience terms into dates
        weekday_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        relday_names = ['yesterday', 'today', 'tomorrow']        
        got = self.get().lower().strip()
        if got in weekday_names:
            got_weekday_number = weekday_names.index(got)
            for d in range(1,8):
                nextday = date.today() + timedelta(days = d)                     
                if nextday.weekday() == got_weekday_number:
                    self.set_date(nextday)
        elif got in relday_names:
            self.date = self.set_date( date.today() + timedelta( days = relday_names.index(got) - 1 ) )

        return super()._validate_date()

    def space_press(self, *args):
        if 'disabled' not in self.state():
            self.drop_down()
            self.state(['pressed'])
            return "break"


    def right_press(self, *args):
        if 'disabled' not in self.state() and 'pressed' in self.state():
            self.set_date(self.get_date() + timedelta(days=1))
            self._calendar.selection_set(self.get_date())

    def left_press(self, *args):
        if 'disabled' not in self.state() and 'pressed' in self.state():
            self.set_date(self.get_date() - timedelta(days=1))
            self._calendar.selection_set(self.get_date())
    
def dateentry_on_space_press(e):
    date_entry = e.widget
    """Trigger self.drop_down on spacebar keypress and set widget state to ['pressed', 'active']."""
    if 'disabled' not in date_entry.state():
        date_entry.state(['pressed'])
        date_entry.drop_down()

def set_priority(e):
    print(e.keysym)
    if re.match('[A-Za-z]$', e.keysym):
        priority.set('({})'.format(e.keysym.upper()))

def parse_completion(item_text):

    pattern = '^\s*x\s+'
    rematch=re.search(pattern, item_text, flags=re.I)

    if rematch:
        item_text = re.sub(pattern, '', item_text, flags=re.I)
        return['x ', item_text]

    return['', item_text]


def parse_pri(item_text):

    pattern = '^\s*(?:x*\s+)*(\(([A-Z])\))'

    rematch=re.search(pattern, item_text, flags=re.I)

    if rematch:
        pri = rematch[1].upper().strip()
        
        item_text = re.sub('\\(' + rematch[2] + '\\)', '', item_text, flags=re.I)

        return[pri, item_text]

    return['', item_text]

def parse_creation(item_text):

    rematch=''

    # match how it would be saved in todo.txt
    txt_pattern = '^\s*(?:(?:x\s+)*(?:\([A-Z]\))\s+)*(\d\d\d\d-\d\d-\d\d)'
    txt_match=re.search(txt_pattern, item_text, flags=re.I)
    if txt_match:
        item_text = re.sub(txt_match[1], '', item_text, flags=re.I)
        rematch = txt_match[1]

    # match how it would be displayed in this app
    app_pattern = 'created:(\d\d\d\d-\d\d-\d\d)'
    app_match=re.search(app_pattern, item_text, flags=re.I)
    if app_match:
        item_text = re.sub(app_match[0], '', item_text, flags=re.I)
        #will take priority over txt_match
        rematch = app_match[1]

    return[rematch, item_text]

def parse_due(item_text):

    pattern = 'due:((\d\d\d\d-\d\d-\d\d)|today|tomorrow|monday)'
    rematch=re.search(pattern, item_text, flags=re.I)

    if rematch:
        duedate = rematch[0]
        if duedate.lower() == 'due:today':
            duedate = 'due:' + date.today().isoformat()
        if duedate.lower() == 'due:tomorrow':
            duedate = 'due:' + (date.today() + timedelta(days=1)).isoformat()
        weekday_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        due_weekday_names = ['due:' + weekday_name for weekday_name in weekday_names]
        if duedate.lower() in due_weekday_names:
            due_weekday_number = due_weekday_names.index(duedate.lower())
            for d in range(1,8):
                nextday = date.today() + timedelta(days = d)                     
                if nextday.weekday() == due_weekday_number:
                    duedate = 'due:' + nextday.isoformat()
        item_text = re.sub(rematch[0], '', item_text, re.I)
        return [duedate, item_text]

    return['', item_text]

def complete():
    current_pos = textarea.index(tk.INSERT)
    split_pos = current_pos.split('.')
    line_start = '{}.{}'.format(split_pos[0], '0')
    get_end = '{}.{}'.format(split_pos[0], '2')
    get_text = textarea.get(line_start, get_end )

    if(get_text == 'x '):
        delete()
    else:
        textarea.insert(line_start,'x ')

def delete():
    current_pos = textarea.index(tk.INSERT)
    split_pos = current_pos.split('.')
    line_start = '{}.{}'.format(split_pos[0], '0')
    line_end = '{}.{}'.format(split_pos[0], tk.END)
    item_text = textarea.get(line_start, line_end)
    parsed_item = {}
    parsed_item['completed'], item_text = parse_completion(item_text)

    parsed_item['pri'], item_text = parse_pri(item_text)
    if parsed_item['pri']:
        priority.set(parsed_item['pri'])

    parsed_item['creation'], item_text = parse_creation(item_text)
    if parsed_item['creation']:

        parsed_item['creation'] = ' created:' + parsed_item['creation'] + ' '

    parsed_item['due'], item_text = parse_due(item_text)
    if parsed_item['due']:
        duelabel, dueisoformat = parsed_item['due'].split(':')
        add_due.set_date(dueisoformat)

    add_entry.insert(0, item_text)
    textarea.delete(line_start, line_end)
    add_entry.focus_set()

def add():
    if not add_entry.get() > '':
        add_entry.focus_set()
        return

    task = ''
    if priority.get() > '':
        task = task + priority.get() + ' '
    task = task + add_entry.get()
    if add_due.get():
        task = task + 'due:' + add_due.get_date().isoformat()
    textarea.insert("1.0", task + "\n")
    add_entry.delete(0, tk.END)
    save()

def refresh():

    pos = textarea.index(tk.INSERT)
    f = open(todo_txt_file , "r")
    data = f.read()
    f.close()
    items = data.split('\n')
    parsed_items=[]

    for item in items:
        if item:
            item_text = item
            parsed_item = {}

            parsed_item['completed'], item_text = parse_completion(item_text)

            parsed_item['pri'], item_text = parse_pri(item_text)
            if parsed_item['pri']:
                parsed_item['pri'] = parsed_item['pri'] + ' '

            parsed_item['creation'], item_text = parse_creation(item_text)
            if parsed_item['creation']:

                parsed_item['creation'] = ' created:' + parsed_item['creation'] + ' '


            parsed_item['due'], item_text = parse_due(item_text)
            if parsed_item['due']:
                parsed_item['due'] = parsed_item['due'] + ' '

            parsed_item['text'] = item_text

            parsed_items.append(parsed_item)


    parsed_items = sorted(parsed_items, key=lambda i: ( i['completed'], i['due'], i['pri'] ) )

    data=''

    previous_due = ''
    for parsed_item in parsed_items:
        if previous_due != parsed_item['due'].strip():
            data = data + '\n'
            previous_due = parsed_item['due'].strip()

        data = data + '{}{}{}{}{}\n'.format( parsed_item['completed'], parsed_item['pri'], parsed_item['due'], parsed_item['text'].strip(), parsed_item['creation'] ) 

    textarea.delete("1.0", "end")
    textarea.insert('1.0',data)
    textarea.mark_set(tk.INSERT, pos)

def save():

    f = open(todo_txt_file, "w")

    data = textarea.get(1.0, tk.END)
    items = data.split('\n')
    data = ''
    for item in items:
        if item:

            item_text = item
            parsed_item = {}

            parsed_item['completed'], item_text = parse_completion(item_text)

            parsed_item['pri'], item_text = parse_pri(item_text)
            if parsed_item['pri']:
                parsed_item['pri'] = parsed_item['pri'] + ' '

            parsed_item['creation'], item_text = parse_creation(item_text)
            if parsed_item['creation']:
                parsed_item['creation'] = parsed_item['creation'] + ' '

            parsed_item['due'], item_text = parse_due(item_text)
            if parsed_item['due']:
                parsed_item['due'] = parsed_item['due'] + ' '

            data = data + '{}{}{}{}{}\n'.format( parsed_item['completed'], parsed_item['pri'], parsed_item['creation'], parsed_item['due'], item_text.strip() ) 

    f.write(data)
    f.close()

    refresh()

def search(textarea, searchbox):
    pos = textarea.index(tk.INSERT)
    if not pos > "":
        pos = "1.0"
    textarea.tag_config('found', background='yellow')
    searchstring = searchbox.get()
    pos = textarea.search(searchstring, pos, stopindex=tk.END )
    if pos == "":
        pos = textarea.search(searchstring, "1.0", stopindex=tk.END )

    if pos:
        textarea.tag_add('found', pos, '%s+%dc' % (pos, len(searchstring)))
        textarea.focus_set()
        textarea.mark_set(tk.INSERT, pos)


items = []

root = tk.Tk()
root.title('Tougshore To Do List')
font=('Calibri 35')

# Set up frames
textframe = tk.Frame(root)
textframe.pack()
buttonframe = tk.Frame(root)
buttonframe.pack()
searchframe = tk.Frame(root)
searchframe.pack()
entryframe = tk.Frame(root)
entryframe.pack()

# Set up widgets
textarea = tk.Text(textframe, width=400, undo=True)
textarea.pack(pady=20, expand='yes')

searchbox = tk.Entry(searchframe)
searchbox.pack(side="right")
searchboxlabel = tk.Label(searchframe,text="Search")
searchboxlabel.pack(side="right")

add_label = tk.Label(entryframe,text="add")
add_label.pack(side='left')

priority=tk.StringVar()
priority.set('(A)')
add_priority = tk.OptionMenu(entryframe, priority, '(A)','(B)','(C)','(D)','(E)','(F)','(G)','(H)','(I)','(J)','(K)','(L)','(M)','(N)','(O)','(P)','(Q)','(R)','(S)','(T)','(U)','(V)','(W)','(X)','(Y)','(Z)' )
add_priority.configure(takefocus=1)
add_priority.pack(side='left')

add_entry = tk.Entry(entryframe, width=100)
add_entry.pack(side='left')

add_due_label = tk.Label(entryframe,text="due:")
add_label.pack(side='left')
add_due = TougDateEntry(entryframe, date_pattern='yyyy-MM-dd')
add_due.delete(0, "end") 
add_due.pack(side='left')
add_due.bind('<Return>', lambda x: add())


add_button = tk.Button(entryframe,height=1,width=10,text='Add', command=lambda: add())
add_button.pack(side='left')

refresh_btn=tk.Button(buttonframe,height=1,width=10, text="Refresh",command=lambda: refresh())
refresh_btn.pack(side="right")
save_btn=tk.Button(buttonframe,height=1,width=10, text="Save",command=lambda: save())
save_btn.pack(side="right")

# Bind shortcuts
root.bind('<Control-e>', lambda x: textarea.focus_set())
root.bind('<Control-f>', lambda x: searchbox.focus_set())
root.bind('<Control-n>', lambda x: add_entry.focus_set())
root.bind('<Control-s>', lambda x: save())
root.bind('<Control-r>', lambda x: refresh())
root.bind('<Control-x>', lambda x: complete())
searchbox.bind('<Return>', lambda x: search(textarea, searchbox))
add_priority.bind('<KeyPress>', lambda e: set_priority(e))
add_entry.bind('<Return>', lambda x: add())
add_entry.bind('<Shift-Keypress-Tab>', add_priority.focus_set())
add_button.bind('<Return>', lambda x: add())
root.unbind('<Control-d>')
home = str(Path.home())

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

    
refresh()

root.mainloop()