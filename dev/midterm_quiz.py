""" Programming Language Concepts Quiz Application """
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import random
import os
from PIL import Image, ImageTk
import pygame.mixer

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Compiler Concepts Quiz")
        self.style = ttk.Style()
        self.timer_id = None  # Initialize timer reference
        self.remaining_time = 0  # Initialize timer counter
        self.style.configure('TButton', padding=5, width=20)
        self.style.configure('Selected.TButton', background='#e0e0e0')
        self.style.configure('Correct.TButton', background='#d4edda', foreground='#155724')
        self.style.configure('Incorrect.TButton', background='#f8d7da', foreground='#721c24')
        self.style.configure('Disabled.TButton', foreground='#666666', background='#f0f0f0')
        self.style.configure('Correct.TButton', background='#d4edda', foreground='#155724')
        self.style.configure('Incorrect.TButton', background='#f8d7da', foreground='#721c24')
        self.style.configure('Disabled.TButton', 
                        foreground='#666666',
                        background='#f0f0f0',
                        relief='flat')
        self.style.map('Disabled.TButton',
                    background=[('disabled', '#f0f0f0')],
                    foreground=[('disabled', '#666666')])        
        self.settings = {
            'timer_enabled': False,
            'max_attempts': 2,
            'text_size': 12,
            'theme': 'clam',
            'sound_effects': True,
            'background_music': False
        }
        
        # Initialize sound system
        pygame.mixer.init()
        self.sound_correct = pygame.mixer.Sound('correct.wav') if os.path.exists('correct.wav') else None
        self.sound_wrong = pygame.mixer.Sound('wrong.wav') if os.path.exists('wrong.wav') else None
        
        # Initialize scores and topic info
        self.topic_scores = {}
        self.topic_descriptions = {}
        self.current_file_path = "No file loaded"
        self.current_topic = None
        self.filename = "questions"; 
        self.questions = {}
        self.asked_questions = set()
        self.style.theme_use(self.settings['theme'])
        self.style.configure('TButton', padding=5)
        self.style.map('Selected.TButton',
            background=[('active', '#4a7ebb'), ('pressed', '#4a7ebb'), ('!disabled', '#4a7ebb')],
            foreground=[('active', 'white'), ('pressed', 'white'), ('!disabled', 'white')]
            )
        self.style.configure('Correct.TButton', 
                        background='#d4edda', 
                        foreground='#155724',
                        relief='flat')  # Remove button border
        self.style.configure('Incorrect.TButton', 
                        background='#f8d7da', 
                        foreground='#721c24',
                        relief='flat')
        self.style.map('Correct.TButton',
                    background=[('disabled', '#d4edda')])  # Force background when disabled
        self.style.map('Incorrect.TButton',
                    background=[('disabled', '#f8d7da')])
        
        self.load_questions_file()
        self.create_main_menu()

    def create_main_menu(self):
        self.clear_window()
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left Panel (Description and Topic Info)
        left_panel = ttk.Frame(main_frame, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Program Description
        desc_text = tk.Text(left_panel, wrap=tk.WORD, height=8, 
                          font=('Arial', self.settings['text_size']))
        desc_text.insert(tk.END, "Welcome to the Programming Concepts Quiz!\n\n"
                         "This application tests your knowledge of various programming paradigms, "
                         "language comparisons, compilation processes, and more. Select a topic "
                         "from the right to begin!")
        desc_text.config(state=tk.DISABLED)
        desc_text.pack(fill=tk.X, pady=(0, 20))
        
        # Topic Info Display
        self.topic_info_text = tk.Text(left_panel, wrap=tk.WORD, height=10,
                                     font=('Arial', self.settings['text_size']-1))
        self.update_topic_info()
        self.topic_info_text.config(state=tk.DISABLED)
        self.topic_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Right Panel (Controls)
        right_panel = ttk.Frame(main_frame, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File Path Section
        ttk.Label(right_panel, text="Question File:").pack(anchor=tk.W)
        self.file_path_entry = ttk.Entry(right_panel, width=30)
        self.file_path_entry.insert(0, self.current_file_path)
        self.file_path_entry.pack(pady=5)
        
        ttk.Button(right_panel, text="Load Question File", 
                 command=self.load_custom_file).pack(pady=5)
        
        # Topic Selection
        ttk.Label(right_panel, text="Select Topic:").pack(pady=(10, 0))
        self.topic_buttons_frame = ttk.Frame(right_panel)
        self.topic_buttons_frame.pack()
        self.update_topic_buttons()
        
        # Settings Button
        ttk.Button(right_panel, text="⚙ Settings", 
                 command=self.show_settings).pack(pady=20)
        
        # Quit Button
        ttk.Button(right_panel, text="Quit", command=self.root.quit).pack()
        
        self.show_score()

    def update_topic_info(self):
        """Update the topic information display"""
        info_text = "Loaded Topics:\n\n"
        for topic, desc in self.topic_descriptions.items():
            info_text += f"• {topic}:\n{desc}\n\n"
            score = self.topic_scores.get(topic, {'correct': 0, 'incorrect': 0})
            info_text += f"Score: {score['correct']} ✔ | {score['incorrect']} ✘\n\n"
        
        self.topic_info_text.config(state=tk.NORMAL)
        self.topic_info_text.delete(1.0, tk.END)
        self.topic_info_text.insert(tk.END, info_text)
        self.topic_info_text.config(state=tk.DISABLED)

    def update_topic_buttons(self):
        """Refresh topic selection buttons"""
        for widget in self.topic_buttons_frame.winfo_children():
            widget.destroy()
            
        topics = list(self.questions.keys())
        for topic in topics:
            btn = ttk.Button(self.topic_buttons_frame, text=topic, 
                           command=lambda t=topic: self.start_quiz(t))
            btn.pack(pady=3, fill=tk.X)

    def load_questions_file(self, filename=None):
        try:
            if filename:
                self.current_file_path = filename
                with open(filename, 'r') as f:
                    data = json.load(f)
                    self.questions = {k: v['questions'] for k, v in data.items()}
                    self.topic_descriptions = {k: v['description'] for k, v in data.items()}
                    self.topic_scores = {k: {'correct': 0, 'incorrect': 0} for k in data.keys()}
                self.file_path_entry.delete(0, tk.END)
                self.file_path_entry.insert(0, filename)
                self.update_topic_info()
                self.update_topic_buttons()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load questions: {str(e)}")

    def load_custom_file(self):
        filename = filedialog.askopenfilename(
            title="Select Question File",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
        if filename:
            self.load_questions_file(filename)
            self.create_main_menu()
        else:
            messagebox.showinfo("Info", "No file selected")

    def start_quiz(self, topic):
        self.current_topic = topic
        self.asked_questions = set()
        self.current_attempts = 0  # Reset attempts when starting new quiz
        self.show_question()

    def show_question(self):
        self.clear_window()
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None


        available_questions = [q for q in range(len(self.questions[self.current_topic])) 
                             if q not in self.asked_questions]
        
        if not available_questions:
            messagebox.showinfo("Info", "No more questions in this topic!")
            self.create_main_menu()
            return
            
        q_index = random.choice(available_questions)
        self.asked_questions.add(q_index)
        self.current_question = self.questions[self.current_topic][q_index]
        self.current_answer = self.current_question.get("answer", self.current_question.get("expected_answer", ""))
        self.current_attempts = 0
        self.selected_answers = []

        # Question Frame
        question_frame = ttk.Frame(self.root)
        question_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Question Text Box
        question_text = tk.Text(question_frame, wrap=tk.WORD, height=3,
                            font=('DejaVu Sans', self.settings['text_size']))  # Unicode font
        question_text.insert(tk.END, self.current_question["question"])
        question_text.config(state=tk.DISABLED)
        question_text.pack(pady=10)
        
        # Display Image if available
        if self.current_question.get("image"):
            try:
                img_path = os.path.join(os.path.dirname(self.current_file_path), 
                          self.current_question["image"])
                img = Image.open(img_path)
                img = img.resize((300, 200), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                img_label = ttk.Label(question_frame, image=photo)
                img_label.image = photo
                img_label.pack(pady=10)
            except Exception as e:
                print(f"Error loading image: {str(e)}")

        # Add Explanation Text Widget (initially hidden)
        self.explanation_text = tk.Text(question_frame, wrap=tk.WORD, height=4, 
                                    font=('Arial', self.settings['text_size']-1))
        self.explanation_text.pack_forget()  # Start hidden

        # Answer Section
        answer_frame = ttk.Frame(question_frame)
        answer_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Modify the radio question section in show_question()
        if self.current_question["type"] == "radio":
            self.answer_var = tk.StringVar()
            self.radio_buttons = {}  # To track button widgets
            
            for option in self.current_question["options"]:
                btn = ttk.Button(
                    answer_frame,
                    text=option,
                    command=lambda o=option: self.select_answer(o),
                    style='TButton'
                )
                btn.pack(fill=tk.X, pady=2)
                self.radio_buttons[option] = btn    

                # Add visual feedback for selection
                if self.answer_var.get() == option:
                    btn.config(style='Selected.TButton')
                else:
                    btn.config(style='TButton')

        elif self.current_question["type"] == "checkbox":
            for option in self.current_question["options"]:
                cb_var = tk.BooleanVar()
                cb = ttk.Checkbutton(
                    answer_frame,
                    text=option,
                    variable=cb_var,
                    command=lambda v=cb_var, o=option: self.toggle_checkbox(v, o)
                )
                cb.pack(anchor=tk.W, pady=2)

        elif self.current_question["type"] == "text":
            self.answer_entry = ttk.Entry(answer_frame, 
                                         font=('Arial', self.settings['text_size']))
            self.answer_entry.pack(pady=10, fill=tk.X)

        # Add Attempts Counter
        self.attempts_label = ttk.Label(question_frame, 
                                    font=('Arial', self.settings['text_size']-1),
                                    foreground='#666666')
        self.update_attempts_display()
        self.attempts_label.pack(pady=5)


        # Submit Button - modify this section
        self.submit_button = ttk.Button(question_frame, text="Submit Answer", 
                                    command=self.check_answer)
        self.submit_button.pack(pady=10)

        # Navigation Buttons
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(pady=10)
        
        ttk.Button(nav_frame, text="Next Question", 
                  command=self.show_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Main Menu", 
                  command=self.create_main_menu).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Quit", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        if self.settings['timer_enabled']:
            self.start_timer(30)

        self.show_score()
        
    # Add new method to handle answer selection
    def select_answer(self, option):
        self.answer_var.set(option)
        for opt, btn in self.radio_buttons.items():
            if opt == option:
                btn.configure(style='Selected.TButton')
            else:
                btn.configure(style='TButton')

    def load_questions_file(self, filename=None):
        try:
            if filename:
                self.current_file_path = filename
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Correct these two lines
                    self.questions = {k: v['questions'] for k, v in data.items()}
                    self.topic_descriptions = {k: v['description'] for k, v in data.items()}
                    self.topic_scores = {k: {'correct': 0, 'incorrect': 0} for k in data.keys()}
                self.file_path_entry.delete(0, tk.END)
                self.file_path_entry.insert(0, filename)
                self.update_topic_info()
                self.update_topic_buttons()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load questions: {str(e)}")

    def toggle_checkbox(self, var, option):
        if var.get():
            self.selected_answers.append(option)
        else:
            if option in self.selected_answers:
                self.selected_answers.remove(option)

    def update_attempts_display(self):
        remaining = self.settings['max_attempts'] - self.current_attempts
        self.attempts_label.config(
            text=f"Attempts remaining: {remaining}/{self.settings['max_attempts']}"
        )
        # Color coding
        if remaining == 1:
            self.attempts_label.config(foreground='#cc8800')
        elif remaining == 0:
            self.attempts_label.config(foreground='#cc0000')
        else:
            self.attempts_label.config(foreground='#666666')

    def check_answer(self):
        user_answer = None
        correct = False

        # Get user answer first
        if self.current_question["type"] == "radio":
            user_answer = self.answer_var.get()
            if not user_answer:
                messagebox.showwarning("No Answer", "Please select an answer before submitting!")
                return
            correct = user_answer == self.current_answer

        elif self.current_question["type"] == "checkbox":
            user_answer = sorted(self.selected_answers)
            correct = sorted(user_answer) == sorted(self.current_answer)

        elif self.current_question["type"] == "text":
            user_answer = self.answer_entry.get().strip().lower()
            correct = user_answer in [a.lower() for a in self.current_answer]

        # Increment attempts after checking answer
        self.current_attempts += 1

        if correct:
            # Handle correct answer
            self.topic_scores[self.current_topic]['correct'] += 1
            bg_color = '#dfffdf'
            if self.settings['sound_effects'] and self.sound_correct:
                self.sound_correct.play()
            
            # Disable all buttons and highlight correct
            if self.current_question["type"] == "radio":
                for option, btn in self.radio_buttons.items():
                    # Set style FIRST, then disable
                    btn.configure(style='Correct.TButton' if option == self.current_answer 
                                else 'Disabled.TButton')
                    btn.state(['disabled'])

            # Disable submit button
            self.submit_button.config(style='Disabled.TButton')
            self.submit_button.state(['disabled'])
            
            # Create or update continue button
            if hasattr(self, 'continue_btn'):
                self.continue_btn.destroy()
            self.continue_btn = ttk.Button(self.root, text="Continue →", command=self.show_question)
            self.continue_btn.pack(pady=20)

        else:
            bg_color = '#ffdfdf'
            if self.settings['sound_effects'] and self.sound_wrong:
                self.sound_wrong.play()

            if self.current_question["type"] == "radio" and user_answer:
                self.radio_buttons[user_answer].configure(style='Incorrect.TButton')
                self.radio_buttons[user_answer].state(['disabled'])

            if self.current_attempts >= self.settings['max_attempts']:
                # Display explanation in GUI
                explanation = self.current_question.get("explanation", "")
                self.explanation_text.config(state=tk.NORMAL)
                self.explanation_text.delete(1.0, tk.END)
                self.explanation_text.insert(tk.END, 
                    f"Correct answer: {self.current_answer}\n\n{explanation}")
                self.explanation_text.config(state=tk.DISABLED)
                self.explanation_text.pack(pady=10)  # Show explanation
                
                # Disable all answer buttons and show correct answer
                if self.current_question["type"] == "radio":
                    for option, btn in self.radio_buttons.items():
                        # Set style FIRST, then disable
                        btn.configure(style='Correct.TButton' if option == self.current_answer 
                                    else 'Incorrect.TButton')
                        btn.state(['disabled'])

                # Disable submit button
                self.submit_button.config(style='Disabled.TButton')
                self.submit_button.state(['disabled'])

                # Create or update continue button
                if hasattr(self, 'continue_btn'):
                    self.continue_btn.destroy()
                self.continue_btn = ttk.Button(self.root, text="Continue →", command=self.show_question)
                self.continue_btn.pack(pady=20)
            else:
                messagebox.showwarning("Incorrect", 
                    f"Attempts left: {self.settings['max_attempts'] - self.current_attempts}")
                # Remove messagebox and use inline display
                self.update_attempts_display()

        # Update visual feedback
        self.root.config(bg=bg_color)
        self.show_score()

        # Remove automatic background reset
    # (Let the Continue button handler manage the UI transition)

    def show_score(self):
        score_text = f"Score: {self.topic_scores[self.current_topic]['correct']} ✔ | {self.topic_scores[self.current_topic]['incorrect']} ✘" if self.current_topic else "Select a topic to start!"
        if hasattr(self, 'score_label'):
            self.score_label.destroy()
        self.score_label = ttk.Label(self.root, text=score_text, 
                                   font=('Arial', self.settings['text_size']), 
                                   anchor=tk.E)
        self.score_label.pack(fill=tk.X, padx=20, pady=5, anchor=tk.SE)

    def clear_window(self):
        if hasattr(self, 'score_label'):
            self.score_label.destroy()
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        
        ttk.Label(settings_win, text="Quiz Settings", 
                font=('Arial', 14)).grid(row=0, columnspan=2, pady=10)
        
        # Initialize variables here instead of using self
        self.max_attempts_var = tk.IntVar(value=self.settings['max_attempts'])
        self.text_size_var = tk.IntVar(value=self.settings['text_size'])

        ttk.Label(settings_win, text="Quiz Settings", 
            font=('Arial', 14)).grid(row=0, columnspan=2, pady=10)
        
        # Timer Toggle
        ttk.Label(settings_win, text="Enable Timer:").grid(row=1, column=0, sticky='w', padx=10)
        timer_var = tk.BooleanVar(value=self.settings['timer_enabled'])
        ttk.Checkbutton(settings_win, variable=timer_var).grid(row=1, column=1, sticky='e', padx=10)
        
        # Modified Max Attempts section
        ttk.Label(settings_win, text="Max Attempts:").grid(row=2, column=0, sticky='w', padx=10)
        attempts_spin = ttk.Spinbox(settings_win, from_=1, to=5, 
                                width=5, 
                                textvariable=self.max_attempts_var)
        attempts_spin.grid(row=2, column=1, sticky='e', padx=10)
        
        # Text Size
        # Create IntVars for numeric settings
        self.max_attempts_var = tk.IntVar(value=self.settings['max_attempts'])
        self.text_size_var = tk.IntVar(value=self.settings['text_size'])        

        # Max Attempts section (now using instance variables)
        ttk.Label(settings_win, text="Max Attempts:").grid(row=2, column=0, sticky='w', padx=10)
        attempts_spin = ttk.Spinbox(settings_win, from_=1, to=5, 
                                width=5, 
                                textvariable=self.max_attempts_var)
        attempts_spin.grid(row=2, column=1, sticky='e', padx=10)

        # Modified Text Size section
        ttk.Label(settings_win, text="Text Size:").grid(row=3, column=0, sticky='w', padx=10)
        size_spin = ttk.Spinbox(settings_win, from_=8, to=24, 
                            width=5, 
                            textvariable=self.text_size_var)
        size_spin.grid(row=3, column=1, sticky='e', padx=10)
        
        # Theme Selection
        ttk.Label(settings_win, text="Theme:").grid(row=4, column=0, sticky='w', padx=10)
        theme_var = tk.StringVar(value=self.settings['theme'])
        theme_menu = ttk.Combobox(settings_win, textvariable=theme_var, 
                                values=['clam', 'alt', 'default', 'classic'])
        theme_menu.grid(row=4, column=1, sticky='e', padx=10)
        
        # Sound Effects
        ttk.Label(settings_win, text="Sound Effects:").grid(row=5, column=0, sticky='w', padx=10)
        sound_var = tk.BooleanVar(value=self.settings['sound_effects'])
        ttk.Checkbutton(settings_win, variable=sound_var).grid(row=5, column=1, sticky='e', padx=10)
        
        # Background Music
        ttk.Label(settings_win, text="Background Music:").grid(row=6, column=0, sticky='w', padx=10)
        music_var = tk.BooleanVar(value=self.settings['background_music'])
        ttk.Checkbutton(settings_win, variable=music_var).grid(row=6, column=1, sticky='e', padx=10)
        
        # Modified Save Button command
        ttk.Button(settings_win, text="Save", 
                command=lambda: self.save_settings(
                    timer_var.get(),
                    self.max_attempts_var.get(),  # Get from IntVar
                    self.text_size_var.get(),     # Get from IntVar
                    theme_var.get(),
                    sound_var.get(),
                    music_var.get()
                )).grid(row=7, columnspan=2, pady=10)

    def save_settings(self, timer_enabled, max_attempts, text_size, theme, sound_effects, background_music):
        self.settings = {
            'timer_enabled': timer_enabled,
            'max_attempts': max_attempts,
            'text_size': text_size,
            'theme': theme,
            'sound_effects': sound_effects,
            'background_music': background_music
        }
        self.style.theme_use(theme)
        self.apply_settings()
        messagebox.showinfo("Settings Saved", "Settings updated successfully!")

    def apply_settings(self):
        self.style.configure('TButton', font=('Arial', self.settings['text_size']))
        self.style.configure('TLabel', font=('Arial', self.settings['text_size']))

    def start_timer(self, seconds):
        self.remaining_time = seconds
        self.timer_label = ttk.Label(self.root, text=f"Time left: {seconds}s",
                                   font=('Arial', self.settings['text_size']))
        self.timer_label.pack(pady=5)
        self.update_timer()

    def update_timer(self):
        if self.remaining_time > 0:
            self.timer_label.config(text=f"Time left: {self.remaining_time}s")
            self.remaining_time -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.check_answer(None)
            messagebox.showinfo("Timeout", "Time's up!")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x700")
    app = QuizApp(root)
    root.mainloop()