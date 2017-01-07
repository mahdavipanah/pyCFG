#!/usr/bin/env python3
"""
pyCFG - Python context free grammar(CFG) parser library and application

Version : 1.0.0
Author : Hamidreza Mahdavipanah
Repository: http://github.com/mahdavipanah/pyCFG
License : MIT License
"""
import tkinter
import tkinter.scrolledtext
from tkinter import messagebox
from tkinter import filedialog
import webbrowser
from copy import copy

from cfg import CFG


class pyCFG(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.title("pyCFG")
        self.geometry("440x360")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(3, weight=1)

        tkinter.Label(self, text='Rules (R):').grid(row=0, sticky=tkinter.W)
        self.rules_text = tkinter.scrolledtext.ScrolledText(self)
        self.rules_text.grid(row=1, sticky=tkinter.NSEW, columnspan=4)

        tkinter.Label(self, text='Variables (V):').grid(row=2, column=0, sticky=tkinter.W)
        self.variables_entry = tkinter.Entry(self)
        self.variables_entry.grid(row=2, column=1, sticky=tkinter.NSEW)

        tkinter.Label(self, text='Terminals (Σ):').grid(row=2, column=2, sticky=tkinter.W)
        self.terminals_entry = tkinter.Entry(self)
        self.terminals_entry.grid(row=2, column=3, sticky=tkinter.NSEW)

        tkinter.Label(self, text='Start variable (S): ').grid(row=3, column=0, sticky=tkinter.W)
        self.start_variable_entry = tkinter.Entry(self)
        self.start_variable_entry.grid(row=3, column=1, sticky=tkinter.NSEW)

        tkinter.Label(self, text='Null character : ').grid(row=3, column=2, sticky=tkinter.W)
        self.null_character_entry = tkinter.Entry(self)
        self.null_character_entry.grid(row=3, column=3, sticky=tkinter.NSEW)

        evaluate_button_frame = tkinter.Frame(bg='Green')
        evaluate_button_frame.grid(row=4, column=0, sticky=tkinter.NSEW, columnspan=4)
        evaluate_button_frame.grid_columnconfigure(0, weight=1)
        tkinter.Button(evaluate_button_frame, text='Evaluate', command=self._evaluate).grid(sticky=tkinter.NSEW,
                                                                                            padx=1,
                                                                                            pady=1)

        self.grammar_mode = tkinter.IntVar(self, value=0)
        self.radioButtons = []
        self.radioButtons.append(tkinter.Radiobutton(self, text='CFG',
                                                     variable=self.grammar_mode,
                                                     indicatoron=0,
                                                     value=0,
                                                     command=self._change_grammar_mode))
        self.radioButtons[0].grid(row=5, column=0, columnspan=2, sticky=tkinter.NSEW)
        self.radioButtons.append(tkinter.Radiobutton(self, text='Remove null rules',
                                                     variable=self.grammar_mode,
                                                     indicatoron=0,
                                                     value=1,
                                                     command=self._change_grammar_mode))
        self.radioButtons[1].grid(row=5, column=2, columnspan=2, sticky=tkinter.NSEW)
        self.radioButtons.append(tkinter.Radiobutton(self, text='Remove unit rules',
                                                     variable=self.grammar_mode,
                                                     indicatoron=0,
                                                     value=2,
                                                     command=self._change_grammar_mode))
        self.radioButtons[2].grid(row=6, column=0, columnspan=2, sticky=tkinter.NSEW)
        self.radioButtons.append(tkinter.Radiobutton(self, text='Reduct',
                                                     variable=self.grammar_mode,
                                                     indicatoron=0,
                                                     value=3,
                                                     command=self._change_grammar_mode))
        self.radioButtons[3].grid(row=6, column=2, columnspan=2, sticky=tkinter.NSEW)
        self.radioButtons.append(tkinter.Radiobutton(self, text='Chamsky',
                                                     variable=self.grammar_mode,
                                                     indicatoron=0,
                                                     value=4,
                                                     command=self._change_grammar_mode))
        self.radioButtons[4].grid(row=7, column=0, columnspan=4, sticky=tkinter.NSEW)

        self.string_frame = tkinter.Frame(self)
        self.string_frame.grid(row=8, column=0, columnspan=4, sticky=tkinter.NSEW)
        self.string_frame.columnconfigure(1, weight=1)
        tkinter.Label(self.string_frame, text='String : ').grid(row=0, column=0, sticky=tkinter.W)
        self.string_entry = tkinter.Entry(self.string_frame)
        self.string_entry.grid(row=0, column=1, sticky=tkinter.NSEW)
        tkinter.Button(self.string_frame, text="Check", command=self._check_string).grid(row=0, column=2)

        self._change_widgets_state(tkinter.DISABLED)

        self.about_window = None

        menu = tkinter.Menu(self)
        menu.add_command(label="Load from file", command=self._load_from_file)
        menu.add_command(label="Save to file", command=self._save_to_file)
        help_menu = tkinter.Menu(menu, tearoff=0)
        help_menu.add_command(label="Help", command=self._show_help)
        help_menu.add_command(label="About", command=self._show_about)
        menu.add_cascade(label="Help", menu=help_menu)
        self['menu'] = menu

        self.cfg = [None for _ in range(5)]

    def _check_string(self):
        if self.cfg[4].cyk(self.string_entry.get()):
            messagebox.showinfo("CYK algorithm", "Grammar can generate entered string")
        else:
            messagebox.showerror("CYK algorithm", "Grammar cannot generate entered string")

    def _evaluate(self):
        self._change_widgets_state(tkinter.DISABLED)

        try:
            rules = set()
            for line in self.rules_text.get("1.0", 'end-1c').strip().split('\n'):
                line = line.strip()
                if not line:
                    continue

                line_parts = line.split('->')
                if len(line_parts) != 2:
                    raise ValueError("Rule syntax error : {}".format(line))

                line_parts = [line_part.strip() for line_part in line_parts]

                if line_parts[1].count('|') != 0:
                    second_parts = line_parts[1].split('|')
                    for second_part in second_parts:
                        second_part = second_part.strip()
                        if not second_part:
                            raise ValueError("Rule syntax error : {}".format(line))

                        rules.add((line_parts[0], second_part))

                else:
                    rules.add((line_parts[0], line_parts[1]))

            variables = set()
            for variable in self.variables_entry.get().strip().split(','):
                variable = variable.strip()
                if not variable:
                    continue

                variables.add(variable)

            terminals = set()
            for terminal in self.terminals_entry.get().strip().split(','):
                terminal = terminal.strip()
                if not terminal:
                    continue

                terminals.add(terminal)

            _cfg = CFG(variables, terminals, rules, self.start_variable_entry.get(), self.null_character_entry.get())

            cfg = [copy(_cfg) for _ in range(5)]
            cfg[1].remove_null_rules()
            cfg[2].remove_null_rules()
            cfg[2].remove_unit_rules()
            cfg[3].simplify()
            cfg[4].chamsky()

        except ValueError as e:
            messagebox.showerror("Input CFG Error", e.args[0])
            self.cfg = [None for _ in range(5)]
            return

        self.cfg = cfg
        self._change_widgets_state(tkinter.NORMAL)
        self._change_grammar_mode()

    def _load_from_file(self):
        file_name = filedialog.askopenfilename(title="Choose a file as input")
        if not file_name:
            return

        try:
            with open(file_name) as file:
                lines = [line.rstrip() for line in file]

                if len(lines) < 4:
                    messagebox.showerror("Error in input file", "Input file content is not correct.")
                    return

                self._fill_inputs(lines[0], lines[1], lines[2], lines[3], '\n'.join(lines[4:]))

        except:
            messagebox.showerror("Error opening input file",
                                 "Some problem happened while opening input file.")

    def _save_to_file(self):
        file_name = filedialog.asksaveasfilename(title="Choose a file to save grammar")
        if not file_name:
            return

        try:
            with open(file_name, 'w') as file:
                file_lines = []
                file_lines.append(self.variables_entry.get())
                file_lines.append(self.terminals_entry.get())
                file_lines.append(self.start_variable_entry.get())
                file_lines.append(self.null_character_entry.get())
                file_lines.append(self.rules_text.get("1.0", 'end-1c'))
                file.write('\n'.join(file_lines))
        except:
            messagebox.showerror("Error saving to file",
                                 "Some problem happened while saving grammar to the file.")

    @staticmethod
    def _show_help():
        webbrowser.open('http://github.com/mahdavipanah/pyCFG')

    def _show_about(self):
        if self.about_window:
            self.about_window.lift()
            return

        self.about_window = tkinter.Toplevel(self)
        self.about_window.title("About pyCFG")
        self.about_window.minsize(width=400, height=230)
        self.about_window.maxsize(width=400, height=230)
        self.about_window.geometry('400x230')
        self.about_window.resizable(0, 0)
        tkinter.Label(self.about_window, text="pyCFG", font="TkDefaultFont 15 bold").pack(pady=(15, 10))
        tkinter.Label(self.about_window, text="1.0.0", font="TkDefaultFont 10").pack()
        tkinter.Label(self.about_window, text="Github repository:", font="TkDefaultFont 10").pack(pady=(15, 0))
        github_link = tkinter.Label(self.about_window, text="http://github.com/mahdavipanah/pyCFG",
                                    font="TkDefaultFont 10",
                                    fg="Blue", cursor="fleur")
        github_link.pack(pady=(0, 10))
        github_link.bind('<Button-1>', lambda x: webbrowser.open('http://github.com/mahdavipanah/pyCFG'))
        tkinter.Label(self.about_window, text="Created by:", font="TkDefaultFont 10").pack()
        tkinter.Label(self.about_window, text="Hamidreza Mahdavipanah", font="TkDefaultFont 10").pack()
        tkinter.Label(self.about_window, text="Licensed under MIT license", font="TkDefaultFont 8").pack(pady=(20, 0))

        def on_close():
            self.about_window.destroy()
            self.about_window = None

        self.about_window.protocol('WM_DELETE_WINDOW', on_close)
        self.about_window.mainloop()

    def _change_widgets_state(self, state):
        self.grammar_mode.set(0)

        self.string_entry.delete(0, tkinter.END)

        for rb in self.radioButtons:
            rb['state'] = state

        for child in self.string_frame.winfo_children():
            child['state'] = state

    def _fill_inputs(self, variables, terminals, start_variable, null_character, rules):
        self.variables_entry.delete(0, tkinter.END)
        self.variables_entry.insert(0, variables)
        self.terminals_entry.delete(0, tkinter.END)
        self.terminals_entry.insert(0, terminals)
        self.start_variable_entry.delete(0, tkinter.END)
        self.start_variable_entry.insert(0, start_variable)
        self.null_character_entry.delete(0, tkinter.END)
        self.null_character_entry.insert(0, null_character)
        self.rules_text.delete("1.0", tkinter.END)
        self.rules_text.insert("1.0", rules)

    def _change_grammar_mode(self):
        cfg = self.cfg[self.grammar_mode.get()]
        self._fill_inputs(' ,'.join(cfg.variables),
                          ' ,'.join(cfg.terminals),
                          cfg.start_variable,
                          cfg.null_character,
                          cfg.str_rules())


if __name__ == '__main__':
    pyCFG().mainloop()
