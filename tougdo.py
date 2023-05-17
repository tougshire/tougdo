from datetime import date, timedelta
import tkinter as tk
import re


def refresh(textarea):

    f = open("c:\\users\\benja\\onedrive\\todo_txt\\todo.txt", "r")
    data = f.read()
    f.close()
    items = data.split('\n')
    parsed_items=[]
    itempattern = '^\s*\([A-Z]\)\s.*'
    duepattern = 'due:((\d\d\d\d-\d\d-\d\d)|today|tomorrow)'
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

def save(textarea):

    f = open("c:\\users\\benja\\onedrive\\todo_txt\\todo.txt", "w")
    itempattern = '^\([A-Z]\)\s.*'

    data = textarea.get(1.0, tk.END)
    items = data.split('\n')
    data = ''
    for i, item in enumerate(items):
        if re.match(itempattern, item):
            data = data + item + '\n'
    f.write(data)
    f.close()

    refresh(textarea)

def search(textarea, searchbox):
    pos = textarea.index(tk.INSERT)
    if not pos > "":
        pos = "1.0"
    print('tp236hc28', pos)
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

top = tk.Frame(root)
top.pack()

bottom = tk.Frame(root)
bottom.pack()

textarea = tk.Text(top, width=400)
textarea.pack(pady=20, expand='yes')

searchbutton = tk.Button(bottom, height=1, text="Search", command=lambda: search(textarea, searchbox))
searchbutton.pack(side="right")
searchbox = tk.Entry(bottom)
searchbox.pack(side="right")
searchboxlabel = tk.Label(bottom,text="Search")
searchboxlabel.pack(side="right")

refresh_btn=tk.Button(bottom,height=1,width=10, text="Refresh",command=lambda: refresh(textarea))
refresh_btn.pack(side="right")
save_btn=tk.Button(bottom,height=1,width=10, text="Save",command=lambda: save(textarea))
save_btn.pack(side="right")

refresh(textarea)

root.mainloop()