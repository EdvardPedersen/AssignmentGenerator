import subprocess
import tkinter
import tkinter.scrolledtext
import tkinter.ttk
import json
import os
import argparse

class DragDropListbox(tkinter.Listbox):
    """ A Tkinter listbox with drag'n'drop reordering of entries. """
    def __init__(self, master, **kw):
        kw['selectmode'] = tkinter.SINGLE
        tkinter.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.curIndex = None

    def setCurrent(self, event):
        self.curIndex = self.nearest(event.y)

    def shiftSelection(self, event):
        i = self.nearest(event.y)
        if i < self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.curIndex = i

class App:
    def __init__(self):
        self.parse_arguments()
        self.metadata = {}
        self.get_files()
        self.populate_categories()

        self.setup_layout()

        if self.arguments.full:
            for fn in self.metadata:
                self.list_tasks.insert(0,self.metadata[fn]["title"])
            self.generate_output()
            exit(0)



    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--task_dir", help="Directory containing tasks to solve, default 'tasks/'", default="tasks/")
        parser.add_argument("-a", "--assignment", help="Assignment title, default 'Assignment'", default="Assignment")
        parser.add_argument("-f", "--full", help="Generate assignment containing all tasks", action='store_true')
        self.arguments = parser.parse_args()

    def run(self):
        self.root.mainloop()

    def setup_layout(self):
        self.root = tkinter.Tk()
        self.tasks = tkinter.ttk.Treeview(self.root, columns=('name', 'strength', 'filename', 'tags'), show='headings')
        self.tasks.heading('name', text='Name')
        self.tasks.column(0, width=100)
        self.tasks.heading('strength', text='Diff')
        self.tasks.column(1, width=40)
        self.tasks.heading('tags', text='Tags')
        self.tasks.heading('filename', text="Filename")
        self.tasks.grid(row=0, column=1)
        self.tasks.bind('<<TreeviewSelect>>', self.select_task)

        self.categories = tkinter.ttk.Treeview(self.root, columns=('cat'), show='headings')
        self.categories.heading('cat', text='Category')
        self.categories.grid(row=0, column=0)
        for elem in self.cats:
            self.categories.insert('', 'end', values=(elem))
        self.categories.bind('<<TreeviewSelect>>', self.layout_tasks)

        self.text = tkinter.ttk.Notebook(width=500, height=500)
        self.text.grid(row=1, column=0)

        self.subwin = tkinter.Canvas(self.root)
        self.subwin.grid(row=1, column=1)

        self.list_tasks = DragDropListbox(self.subwin)
        self.list_tasks.grid(row=0, column=1)

        self.button = tkinter.ttk.Button(self.subwin, text="Generate assignment", command=self.generate_output)
        self.button.grid(row=1, column=1)
        self.button = tkinter.ttk.Button(self.subwin, text="+", command=self.add_task)
        self.button.grid(row=0, column=0)
        self.button = tkinter.ttk.Button(self.subwin, text="-", command=self.remove_task)
        self.button.grid(row=1, column=0)

    def populate_categories(self):
        self.cats = set()
        for file in self.metadata:
            for category in self.metadata[file]["tags"]:
                self.cats.add(category)

    def layout_tasks(self, event):
        categories = set()
        files = set()
        for selected in self.categories.selection():
            categories.add(self.categories.item(selected)['values'][0])
        for f in self.metadata:
            if len(set(self.metadata[f]["tags"]) & categories) > 0:
                files.add(f)
        for item in self.tasks.get_children():
            self.tasks.delete(item)
        for f in files:
            self.tasks.insert('', 'end', values=(self.metadata[f]["title"], self.metadata[f]["difficulty"], f, self.metadata[f]["tags"]))

    def select_task(self, event):
        for item in self.text.tabs():
            self.text.forget(item)
        for selected in self.tasks.selection():
            assignment = self.metadata[self.get_filename(self.tasks.item(selected)['values'][0])]
            t = tkinter.scrolledtext.ScrolledText(self.text)
            t.insert('end', assignment["assignment"])
            t.configure(state='disabled')
            self.text.add(t, text=assignment["title"])
            
        
    def get_filename(self, title):
        for filename in self.metadata:
            if self.metadata[filename]["title"] == title:
                return filename
        return None

    def add_task(self):
        for selected in self.tasks.selection():
            assignment = self.metadata[self.get_filename(self.tasks.item(selected)['values'][0])]
            self.list_tasks.insert(0,assignment["title"])

    def remove_task(self):
        for i in range(self.list_tasks.size()):
            if(self.list_tasks.selection_includes(i)):
                self.list_tasks.delete(i)

    def get_files(self):
        # Build the tree for the treeview
        for filename in os.listdir(self.arguments.task_dir):
            if filename[-5:] == ".json":
                with open(os.path.join(self.arguments.task_dir, filename)) as f:
                    obj = json.load(f)
                    self.metadata[filename] = obj
                    with open(os.path.join(self.arguments.task_dir, self.metadata[filename]["text"])) as tf:
                        self.metadata[filename]["assignment"] = tf.read()

    def generate_output(self):
        # Generate the output file
        full_text =  "---\n"
        full_text += f"title: {self.arguments.assignment}\n"
        full_text += "numbersections: true\n"
        full_text += "---\n\n"
        full_text_sol = ""
        for i in range(self.list_tasks.size()):
            cur_text = ""
            cur_text_sol = ""
            selected = self.list_tasks.get(i)
            assignment = self.metadata[self.get_filename(selected)]

            if "footer" not in assignment["tags"] and "header" not in assignment["tags"]:
                # Add header
                cur_text = cur_text + "\n" + f"# {assignment['title']}\n"

                # Add tags
                cur_text = cur_text + "Keywords: "
                for kw in assignment["tags"]:
                    cur_text = cur_text + kw + ", "
                cur_text = cur_text[:-2]
                cur_text = cur_text + "\n"

            cur_text = cur_text + "\n" + self.convert_format(assignment)
            cur_text_sol = cur_text + "\n## Solution \n\n"
            if("solution" in assignment):
                with open(os.path.join(self.arguments.task_dir, assignment["solution"])) as tf:
                    if(assignment["solution"][-2:] == ".c"):
                        cur_text_sol = cur_text_sol + "```c\n"
                    if(assignment["solution"][-3:] == ".py"):
                        cur_text_sol = cur_text_sol + "```python\n"
                    cur_text_sol = cur_text_sol + tf.read()
                    cur_text_sol = cur_text_sol + "```\n"
            else:
                cur_text_sol = cur_text_sol + "No solution given.\n"
            full_text = full_text + cur_text
            full_text_sol = full_text_sol + cur_text_sol
    
        args = ['pandoc', '-f', 'markdown']
        args.append('-o')
        args.append('assignment.pdf')
        subprocess.run(args, input=full_text.encode())

        args = ['pandoc', '-f', 'markdown']
        args.append('-o')
        args.append('assignment-solved.pdf')
        subprocess.run(args, input=full_text_sol.encode())

    def convert_format(self, task):
        if task["text"][-4:] == ".tex":
            args = ['pandoc', '-f', 'latex', '-t', 'markdown']
            completed = subprocess.run(args, input=task["assignment"], capture_output=True, text=True)
            task["assignment"] = completed.stdout
        return task["assignment"]

if __name__ == "__main__":
    app = App()
    app.run()
