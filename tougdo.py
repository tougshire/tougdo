from datetime import date, timedelta
import tkinter as tk
import re
window = tk.Tk()
window.title('Tougshore To Do List')


def refresh(txtarea):

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
            print('tp235ha00', item_text)
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
                print('tp235h956', item_text)
                item_text = re.sub(duepattern, '', item_text, flags=re.I)
                print('tp235h957', item_text)


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

    txtarea.delete("1.0", "end")
    txtarea.insert('1.0',data)

def save(txtarea):

    f = open("c:\\users\\benja\\onedrive\\todo_txt\\todo.txt", "w")
    itempattern = '^\([A-Z]\)\s.*'

    data = txtarea.get(1.0, tk.END)
    items = data.split('\n')
    data = ''
    for i, item in enumerate(items):
        if re.match(itempattern, item):
            data = data + item + '\n'
    f.write(data)
    f.close()

    refresh(txtarea)

items = []
txtarea = tk.Text(window, width=400)
txtarea.pack(pady=20, expand='yes')

font=('Calibri 35')

refresh_btn=tk.Button(window,height=1,width=10, text="Refresh",command=lambda: refresh(txtarea))
refresh_btn.pack()
save_btn=tk.Button(window,height=1,width=10, text="Save",command=lambda: save(txtarea))
save_btn.pack()

refresh(txtarea)

window.mainloop()