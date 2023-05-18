from datetime import date, timedelta
import tkinter as tk
import re
import os
from pathlib import Path, WindowsPath
import configparser

def delete():
    current_pos = textarea.index(tk.INSERT)
    split_pos = current_pos.split('.')
    line_start = '{}.{}'.format(split_pos[0], '0')
    line_end = '{}.{}'.format(split_pos[0], tk.END)
    get_text = textarea.get(line_start, line_end)
    editbox.insert(0, get_text)
    textarea.delete(line_start, line_end)
    editbox.focus_set()

def add():

    textarea.insert("1.0", editbox.get() + "\n")
    editbox.delete(0, tk.END)
    save()

def refresh(textarea):


    f = open(todo_txt_file , "r")
    data = f.read()
    f.close()
    items = data.split('\n')
    parsed_items=[]
    duepattern = 'due:((\d\d\d\d-\d\d-\d\d)|today|tomorrow|monday)'
    pripattern = '^\s*\([A-Z]\)'
    projpattern = '\+\w*'
    
    for item in items:
        if re.match(itempattern, item, flags=re.I):
            item_text = item
            parsed_item = {}
            parsed_item['pri'] = ''
            primatch=re.search(pripattern, item_text, flags=re.I)
            if primatch:
                parsed_item['pri'] = primatch[0].upper().strip()
                item_text = re.sub(pripattern, '', item_text, flags=re.I)

            parsed_item['due'] = ''
            duematch=re.search(duepattern, item_text, flags=re.I)
            if duematch:
                duedate = duematch[0]
                if duedate.lower() == 'due:today':
                    duedate = 'due:' + date.today().isoformat()
                if duedate.lower() == 'due:tomorrow':
                    duedate = 'due:' + (date.today() + timedelta(days=1)).isoformat()
                parsed_item['due'] = duedate
                item_text = re.sub(duepattern, '', item_text, flags=re.I)


            parsed_item['projs'] = []
            projmatch=re.search(projpattern, item_text)
            while projmatch:
                parsed_item['projs'].append(projmatch[0])
                item_text = re.sub(projpattern, '', item_text)
                projmatch=re.search(projpattern, item_text)

            parsed_item['text'] = item_text

            parsed_items.append(parsed_item)


    parsed_items = sorted(parsed_items, key=lambda i: ( i['due'], i['pri'] ) )

    data=''

    previous_due = ''
    for parsed_item in parsed_items:
        if previous_due != parsed_item['due'].strip():
            data = data + '\n'
            previous_due = parsed_item['due'].strip()

        data = data + parsed_item['pri'].strip() + ' ' + parsed_item['due'].strip() + ' ' + parsed_item['text'].strip()
        if parsed_item['projs']:
            parsed_item['projs'].sort()
            for proj in parsed_item['projs']:
                data = data + ' ' + proj

        data = data + '\n' 

    textarea.delete("1.0", "end")
    textarea.insert('1.0',data)

def save():

    f = open(todo_txt_file, "w")

    data = textarea.get(1.0, tk.END)
    items = data.split('\n')
    data = ''
    for i, item in enumerate(items):
        if re.match(itempattern, item, re.I):
            data = data + item + '\n'
    f.write(data)
    f.close()

    refresh(textarea)

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
textarea = tk.Text(textframe, width=400)
textarea.pack(pady=20, expand='yes')

searchbox = tk.Entry(searchframe)
searchbox.pack(side="right")
searchboxlabel = tk.Label(searchframe,text="Search")
searchboxlabel.pack(side="right")

editbox = tk.Entry(entryframe, width=100)
editbox.pack(side="right")
editboxlabel = tk.Label(entryframe,text="add")
editboxlabel.pack(side="left")

refresh_btn=tk.Button(buttonframe,height=1,width=10, text="Refresh",command=lambda: refresh(textarea))
refresh_btn.pack(side="right")
save_btn=tk.Button(buttonframe,height=1,width=10, text="Save",command=lambda: save())
save_btn.pack(side="right")

# Bind shortcuts
root.bind('<Control-e>', lambda x: textarea.focus_set())
root.bind('<Control-f>', lambda x: searchbox.focus_set())
root.bind('<Control-s>', lambda x: save())
root.bind('<Control-r>', lambda x: refresh(textarea))
root.bind('<Control-x>', lambda x: delete())
searchbox.bind('<Return>', lambda x: search(textarea, searchbox))
editbox.bind('<Return>', lambda x: add())

# utilities
itempattern = '^\([A-Z]\)\s+.+'

home = str(Path.home())

conf_file = Path.home() / ".tougdo" / "tougdo.conf"
conf_parser = configparser.ConfigParser()
conf_parser.read(conf_file)

todo_txt_file = conf_parser['todo.txt']['todo.txt_file']



refresh(textarea)

root.mainloop()