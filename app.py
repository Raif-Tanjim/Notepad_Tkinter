import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import get_formatter_by_name
from pygments import highlight
import re
text_content = dict()

def get_text_widget():
    tab_widget = root.nametowidget(notebook.select())
    text_widget = tab_widget.winfo_children()[0]
    return text_widget

def confirm_close():
    return messagebox.askyesnocancel(
        message="Warning!!! You have unsaved changes. Are you sure you want to quit?",
        icon="question",
        title="Warning"
    )

def confirm_quit():
    unsaved = False
    for tab in notebook.tabs():
        tab_widget = root.nametowidget(tab)
        text_widget = tab_widget.winfo_children()[0]
        content = text_widget.get("1.0", "end-1c")
        if hash(content) != text_content[str(text_widget)]:
            unsaved = True
            break
    if unsaved and not confirm_close():
        return
    root.destroy()

def close_tab():
    current = get_text_widget()
    if current_tab_unsaved() and not confirm_close():
        return
    if len(notebook.tabs()) == 1:
        create_file()
    notebook.forget(current)

def current_tab_unsaved():
    tab_widget = root.nametowidget(notebook.select())
    text_widget = tab_widget.winfo_children()[0]
    content = text_widget.get("1.0", "end-1c")
    return hash(content) != text_content[str(text_widget)]

def check_for_changes():
    current = get_text_widget()
    content = current.get("1.0", "end-1c")
    name = notebook.tab("current")["text"]
    if hash(content) != text_content[str(current)]:
        if name[-1] != "*":
            notebook.tab("current", text=name + "*")
    elif name[-1] == "*":
        notebook.tab("current", text=name[:-1])

def create_file(content="", title="Untitled"):
    container = ttk.Frame()
    container.pack()
    
    text_area = tk.Text(container)
    text_area.insert("end", content)
    text_area.pack(side="left", fill="both", expand=True)
    notebook.add(container, text=title)
    notebook.select(container)
    
    text_content[str(text_area)] = hash(content)
    
    text_scroll = ttk.Scrollbar(container, orient="vertical", command=text_area.yview)
    text_scroll.pack(side="right", fill="y")
    text_area["yscrollcommand"] = text_scroll.set
    
def save_file():
    file_path = filedialog.asksaveasfilename()
    try:
        file_name = os.path.basename(file_path)
        text_widget = get_text_widget()
        content = text_widget.get("1.0", "end-1c")
        with open(file_name, "w") as file:
            file.write(content)
    except (AttributeError, ValueError):
        print("Operation Not successful")
        return
    notebook.tab("current", text=file_name)

def open_file():
    file_path = filedialog.askopenfilename()
    try:
        file_name = os.path.basename(file_path)
        with open(file_path, "r") as file:
            content = file.read()
    except (AttributeError, FileNotFoundError):
        print("File not opened!")
        return
    create_file(content, file_name)

def search_and_replace():
    search_window = tk.Toplevel(root)
    search_window.title("Search and Replace")

    search_label = ttk.Label(search_window, text="Search Text:")
    search_label.grid(row=0, column=0, padx=5, pady=5)
    search_entry = ttk.Entry(search_window, width=30)
    search_entry.grid(row=0, column=1, padx=5, pady=5)

    replace_label = ttk.Label(search_window, text="Replace Text:")
    replace_label.grid(row=1, column=0, padx=5, pady=5)
    replace_entry = ttk.Entry(search_window, width=30)
    replace_entry.grid(row=1, column=1, padx=5, pady=5)

    def perform_search_and_replace():
        search_text = search_entry.get()
        replace_text = replace_entry.get()
        text_widget = get_text_widget()
        content = text_widget.get("1.0", "end")
        updated_content = content.replace(search_text, replace_text)
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", updated_content)
        search_window.destroy()

    search_button = ttk.Button(search_window, text="Search and Replace", command=perform_search_and_replace)
    search_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="we")
    search_entry.focus_set()

def display_word_count(text_widget, status_bar):
    content = text_widget.get("1.0", "end")
    words = content.split()
    word_count = len(words)
    status_bar.config(text=f"Word Count: {word_count}")

def syntax_highlight(event=None):
    current_tab = get_text_widget()
    content = current_tab.get("1.0", "end-1c")
    lexer = get_lexer_for_filename("dummy.py", stripall=True)
    formatter = get_formatter_by_name("html", linenos=False, cssclass="highlight")
    highlighted_code = highlight(content, lexer, formatter)
    current_tab.delete("1.0", "end")
    current_tab.insert("1.0", highlighted_code)

def auto_capitalize(event=None):
    current_tab = get_text_widget()
    content = current_tab.get("1.0", "end-1c")
    sentences = re.split(r'(?<=[.!?]) +', content)
    capitalized_content = ' '.join(sentence.capitalize() for sentence in sentences)
    current_tab.delete("1.0", "end")
    current_tab.insert("1.0", capitalized_content)

def show_about():
    messagebox.showinfo(
        title="About",
        message="This is simple note pad with Tkinter"
    )

root = tk.Tk()
root.title("Text Editor")
root.option_add("*tearOff", False)
main = ttk.Frame()
main.pack(fill="both", expand=True, padx=23, pady=(2, 7))



status_bar = ttk.Label(root, text="Word Count: 0", anchor=tk.W)
status_bar.pack(side="bottom", fill="x")

menubar = tk.Menu()
root.config(menu=menubar)

file_menu = tk.Menu(menubar)
help_menu = tk.Menu(menubar)
menubar.add_cascade(menu=file_menu, label="File")
menubar.add_cascade(menu=help_menu, label="Help")

file_menu.add_command(label="New file", command=create_file, accelerator="Ctrl+N")
file_menu.add_command(label="Save file", command=save_file, accelerator="Ctrl+S")
file_menu.add_command(label="Open file", command=open_file, accelerator="Ctrl+O")
file_menu.add_command(label="Close Tab", command=close_tab, accelerator="Ctrl+Q")
file_menu.add_command(label="Exit", command=confirm_quit, accelerator="Escape")

file_menu.add_command(label="Search", command=search_and_replace, accelerator="Ctrl+F")

help_menu.add_command(label="About", command=show_about)

notebook = ttk.Notebook(main)
notebook.pack(fill="both", expand=True)
create_file()
root.bind("<KeyPress>", lambda event: check_for_changes())
root.bind("<Control-n>", lambda event: create_file())
root.bind("<Control-s>", lambda event: save_file())
root.bind("<Control-o>", lambda event: open_file())
root.bind("<Control-f>", lambda event: search_and_replace())
root.bind("<Control-q>", lambda event: close_tab())
root.bind("<Escape>", lambda event: confirm_quit())

root.bind("<KeyRelease>", lambda event: display_word_count(get_text_widget(), status_bar))

root.bind("<KeyRelease>", lambda event: auto_capitalize())  # Bind auto capitalize to any key release event

root.mainloop()
