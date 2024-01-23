import random
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import mysql.connector


class MainApp:
    def __init__(self):
        self.connection = mysql.connector.connect(host="localhost", user="root", passwd="AkniLUAp01-", database="quiz")
        self.cursor = self.connection.cursor()
        self.question_num = 0
        self.quizzes_list = []
        self.get_list_of_quizzes()

    def create(self):
        self.root = Tk()
        self.root.configure(bg="light gray")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        self.root.title("Quiz app")
        self.menu(self.root, self.quizzes_list)

    def menu(self, root, quizzes_list):
        self.quizzes_list = quizzes_list
        self.root = root
        self.menu_frame = Frame(self.root)
        self.menu_frame.grid(row=0, column=0, sticky=NSEW)

        Label(self.menu_frame, text="Welcome to Quiz app!", font=('Arial', 40), bg='light gray') \
            .grid(row=0, column=0, columnspan=2, sticky=EW, padx=80, pady=20, ipadx=300, ipady=50)

        Button(self.menu_frame, text="Start Quiz", font=('Arial', 25), bg="gray", command=self.choose_quiz) \
            .grid(row=1, column=0, ipadx=49, padx=500, ipady=10, pady=20)

        Button(self.menu_frame, text="Add new Quiz", font=('Arial', 25), bg="gray", command=self.new_quiz) \
            .grid(row=2, column=0, ipadx=21, ipady=10, pady=20)

        Button(self.menu_frame, text="Delete Quiz", font=('Arial', 25), bg="gray", command=self.delete_quiz) \
            .grid(row=3, column=0, ipadx=38, ipady=10, pady=20)

        Button(self.menu_frame, text="Exit", font=('Arial', 20), bg="gray", command=self.exit_from_app) \
            .grid(row=4, column=0, sticky=E, padx=40, ipadx=30, pady=50)

    def exit_from_app(self):
        result = tkinter.messagebox.askquestion(title='Warning', message="Do you want to close Quiz app?")
        if result == "yes":
            self.root.destroy()
        elif result == "no":
            pass

    def new_quiz(self):
        create_new_quiz = AddNewQuiz(self.root, self.menu_frame, self.quizzes_list, self.connection, self.cursor)
        create_new_quiz.new_quiz_name()

    def delete_quiz(self):
        delete_unnecessary_quizzes = DeleteQuiz(self.root, self.quizzes_list, self.connection, self.cursor)
        delete_unnecessary_quizzes.delete_quiz()

    def get_list_of_quizzes(self):
        get_user_tables = "SELECT table_name FROM information_schema.tables WHERE table_type='BASE TABLE'" \
                          " AND table_schema = 'quiz' AND NOT table_name = 'history' AND NOT table_name = 'physics'" \
                          " AND NOT table_name = 'biology' AND NOT table_name = 'geography'" \
                          " AND NOT table_name = 'health'"
        self.cursor.execute(get_user_tables)
        rows = self.cursor.fetchall()
        for row in rows:
            row = row[0]
            self.quizzes_list.append(row)

    def choose_quiz(self):
        self.menu_frame.destroy()

        self.choose_quiz_top_frame = Frame(self.root, bg='light gray')
        self.choose_quiz_top_frame.grid()

        self.choose_quiz_user_quizzes = Frame(self.root, bg='light gray')
        self.choose_quiz_user_quizzes.grid(pady=40)

        self.canvas = Canvas(self.choose_quiz_user_quizzes, bg='light gray', height=180, width=450,
                             highlightthickness=0)
        self.canvas.grid(padx=100, ipadx=300)

        Label(self.choose_quiz_top_frame, text='Choose your Quiz', font=('Arial', 30)) \
            .grid(row=0, column=0, columnspan=5, pady=40, ipadx=30, ipady=30, padx=450)

        i = 0
        default_quizzes = ['History', 'Physics', 'Biology', 'Geography', 'Health']
        for default_quiz in default_quizzes:
            Button(self.choose_quiz_top_frame, text=default_quiz, font=('Arial', 20), bg="gray",
                   command=lambda def_quiz=default_quiz: self.start_quiz(def_quiz)) \
                .grid(row=1, column=i, ipady=30, ipadx=10, pady=40)
            i += 1

        scrollbar = Scrollbar(self.choose_quiz_user_quizzes, orient='horizontal', command=self.canvas.xview)
        scrollbar.grid(row=1, column=0, columnspan=50, ipadx=465)
        self.canvas.configure(xscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas_frame = Frame(self.canvas, bg='light gray')
        self.canvas.create_window((0, 0), window=self.canvas_frame, anchor="s")

        i = 0
        for quiz in self.quizzes_list:
            Button(self.canvas_frame, text=quiz, font=('Arial', 20), bg="gray", width=10, height=4,
                   command=lambda user_quiz=quiz: self.start_quiz(user_quiz), wraplength=150) \
                .grid(row=0, column=i, padx=20, pady=20)
            i += 1

        Button(self.choose_quiz_user_quizzes, text="Exit", font=('Arial', 20), bg='grey',
               command=self.exit_quiz_choice) \
            .grid(row=2, column=0, sticky=SE, pady=10, padx=20, ipadx=20)

    def start_quiz(self, quiz_name):
        self.choose_quiz_user_quizzes.destroy()
        self.choose_quiz_top_frame.destroy()
        run_quiz = Quiz(self.root, quiz_name, self.quizzes_list, self.connection, self.cursor)
        run_quiz.layout()

    def exit_quiz_choice(self):
        self.choose_quiz_user_quizzes.destroy()
        self.choose_quiz_top_frame.destroy()
        self.menu(self.root, self.quizzes_list)


class AddNewQuiz:
    def __init__(self, root, menu_frame, quizzes_list, connection, cursor):
        self.root = root
        self.menu_frame = menu_frame
        self.connection = connection
        self.cursor = cursor
        self.question_num = 0
        self.curr_question = 0
        self.main_menu = MainApp()
        self.quizzes_list = quizzes_list

    def new_quiz_name(self):
        self.quiz_name_root = Toplevel(self.root)
        self.quiz_name_root.geometry('400x200')
        self.quiz_name_root.title("New Quiz name")
        self.quiz_name_root.grid_columnconfigure(0, weight=1)
        self.quiz_name_root.grid_columnconfigure(1, weight=1)

        self.quiz_name = Entry(self.quiz_name_root, width=20, font=('Arial', 20))
        self.quiz_name.grid(row=0, column=0, columnspan=2, pady=30)
        self.quiz_name.insert(0, 'Entry name of your quiz')
        self.quiz_name.bind("<Button-1>", lambda e: self.quiz_name.delete(0, END))

        Button(self.quiz_name_root, text="Submit", command=self.add_new_quiz, font=('Arial', 20), bg='gray') \
            .grid(row=1, column=0, sticky=W, padx=20, pady=35, ipadx=5)

        Button(self.quiz_name_root, text="Close", command=self.quiz_name_root.destroy, font=('Arial', 20), bg='gray') \
            .grid(row=1, column=1, sticky=E, padx=20, pady=35, ipadx=15)

        self.quiz_name_root.grab_set()

    def add_new_quiz(self):
        self.user_quiz_name = self.quiz_name.get()
        if self.user_quiz_name not in self.quizzes_list and not self.user_quiz_name == "Entry name of your quiz":
            self.sql_table()

            self.quiz_name_root.destroy()
            self.menu_frame.destroy()

            self.add_new_frame = Frame(self.root, bg='light gray')
            self.add_new_frame.grid(row=0, column=0, sticky=NSEW)
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)

            Label(self.add_new_frame, text="Enter question and four answers: ", font=('Arial', 20))\
                .grid(row=0, column=0, columnspan=2, pady=30, padx=350, ipady=50, ipadx=100)

            self.entry_question = Text(self.add_new_frame, font=('Arial', 20), width=50, wrap=WORD, height=3)
            self.entry_question.grid(row=1, column=0, columnspan=2)
            self.entry_question.insert(tkinter.END, "Enter your question here")
            self.entry_question.bind("<Button-1>", lambda e: self.entry_question.delete("1.0", END))

            self.entry_answer_1 = Entry(self.add_new_frame, font=('Arial', 20), width=20)
            self.entry_answer_1.grid(row=3, column=0, pady=50, padx=80, sticky=E, ipady=10)
            self.entry_answer_1.insert(0, "First answer (correct)")
            self.entry_answer_1.bind("<Button-1>", lambda e: self.entry_answer_1.delete(0, END))

            self.entry_answer_2 = Entry(self.add_new_frame, font=('Arial', 20))
            self.entry_answer_2.grid(row=3, column=1, pady=50, padx=80, sticky=W, ipady=10)
            self.entry_answer_2.insert(0, "Second answer")
            self.entry_answer_2.bind("<Button-1>", lambda e: self.entry_answer_2.delete(0, END))

            self.entry_answer_3 = Entry(self.add_new_frame, font=('Arial', 20))
            self.entry_answer_3.grid(row=4, column=0, pady=20, padx=80, sticky=E, ipady=10)
            self.entry_answer_3.insert(0, "Third answer")
            self.entry_answer_3.bind("<Button-1>", lambda e: self.entry_answer_3.delete(0, END))

            self.entry_answer_4 = Entry(self.add_new_frame, font=('Arial', 20))
            self.entry_answer_4.grid(row=4, column=1, pady=20, padx=80, sticky=W, ipady=10)
            self.entry_answer_4.insert(0, "Fourth answer")
            self.entry_answer_4.bind("<Button-1>", lambda e: self.entry_answer_4.delete(0, END))

            Button(self.add_new_frame, font=('Arial', 20), text="Exit", command=self.exit_add, bg="gray")\
                .grid(row=6, column=0, columnspan=2, sticky=SE, padx=50, ipadx=15)

            Button(self.add_new_frame, font=('Arial', 20), text="New question", command=self.new_question, bg="gray")\
                .grid(row=5, column=1, sticky=W, padx=100, ipadx=40)

            Button(self.add_new_frame, font=('Arial', 20), text="End quiz", command=self.end_quiz, bg="gray")\
                .grid(row=6, column=0, columnspan=2, pady=20)

            Button(self.add_new_frame, font=('Arial', 20), text="Previous question",
                   command=self.prev_question, bg="gray")\
                .grid(row=5, column=0, sticky=E, padx=100, ipadx=15)
        elif self.user_quiz_name == "Entry name of your quiz":
            tkinter.messagebox.showinfo(title="Information", message="Please enter Quiz name")
        else:
            tkinter.messagebox.showinfo(title="Information", message="This Quiz name already exists")

    def sql_table(self):
        create_table = "CREATE TABLE IF NOT EXISTS `{}`(QuestionNumber CHAR(2), Question tinytext," \
                       " Answer1 tinytext, Answer2 tinytext, Answer3 tinytext, Answer4 tinytext);" \
            .format(self.user_quiz_name)
        self.cursor.execute(create_table)

    def save_to_sql(self):
        question = self.entry_question.get("1.0", END)
        answer_1 = self.entry_answer_1.get()
        answer_2 = self.entry_answer_2.get()
        answer_3 = self.entry_answer_3.get()
        answer_4 = self.entry_answer_4.get()
        self.question_num += 1
        insert_query = 'INSERT INTO `{}` (QuestionNumber, Question, Answer1, Answer2, Answer3, Answer4) VALUES ' \
                       '(%s,%s,%s,%s,%s,%s)'.format(self.user_quiz_name)
        values_to_insert = (self.question_num, question, answer_1, answer_2, answer_3, answer_4)
        self.cursor.execute(insert_query, values_to_insert)
        self.connection.commit()

    def new_question(self):
        self.curr_question += 1
        self.save_to_sql()
        self.clean_entry_boxes()

    def clean_entry_boxes(self):
        self.entry_question.delete("1.0", END)
        self.entry_answer_1.delete(0, END)
        self.entry_answer_2.delete(0, END)
        self.entry_answer_3.delete(0, END)
        self.entry_answer_4.delete(0, END)
        self.entry_question.insert(tkinter.END, "Enter your question here")
        self.entry_answer_1.insert(0, "First answer")
        self.entry_answer_2.insert(0, "Second answer")
        self.entry_answer_3.insert(0, "Third answer")
        self.entry_answer_4.insert(0, "Fourth answer")

    def end_quiz(self):
        result = tkinter.messagebox.askquestion(title='Warning', message='Do you want to end your Quiz?')
        if result == 'yes':
            self.save_to_sql()
            self.add_new_frame.destroy()
            self.get_list_of_quizzes()
            print(self.quizzes_list)
            self.main_menu.menu(self.root, self.quizzes_list)
        else:
            pass

    def get_list_of_quizzes(self):
        get_user_tables = "SELECT table_name FROM information_schema.tables WHERE table_type='BASE TABLE'" \
                          " AND table_schema = 'quiz' AND NOT table_name = 'history' AND NOT table_name = 'physics'" \
                          " AND NOT table_name = 'biology' AND NOT table_name = 'geography'" \
                          " AND NOT table_name = 'health'"
        self.cursor.execute(get_user_tables)
        rows = self.cursor.fetchall()
        self.quizzes_list.clear()
        for row in rows:
            row = row[0]
            self.quizzes_list.append(row)

    def prev_question(self):
        read_table = "SELECT * FROM quiz.`{}` WHERE QuestionNumber = {}".format(self.user_quiz_name, self.curr_question)
        self.cursor.execute(read_table)
        rows = self.cursor.fetchall()
        for row in rows:
            self.entry_question.delete("1.0", END)
            self.entry_answer_1.delete(0, END)
            self.entry_answer_2.delete(0, END)
            self.entry_answer_3.delete(0, END)
            self.entry_answer_4.delete(0, END)
            self.entry_question.insert(tkinter.END, row[1])
            self.entry_answer_1.insert(0, row[2])
            self.entry_answer_2.insert(0, row[3])
            self.entry_answer_3.insert(0, row[4])
            self.entry_answer_4.insert(0, row[5])

        update_data = "DELETE FROM `{}` WHERE QuestionNumber = {}".format(self.user_quiz_name, self.curr_question)
        self.cursor.execute(update_data)
        self.question_num -= 1
        self.curr_question -= 1

    def exit_add(self):
        result = tkinter.messagebox.askquestion(title="Warning", message="Do you want to exit to main menu?")
        if result == "yes":
            self.add_new_frame.destroy()
            self.main_menu.menu(self.root, self.quizzes_list)
        elif result == "no":
            pass


class DeleteQuiz:
    def __init__(self, root, quizzes_list, connection, cursor):
        self.root = root
        self.connection = connection
        self.cursor = cursor
        self.quizzes_list = quizzes_list

    def delete_quiz(self):
        self.get_list_of_quizzes()
        self.del_root = Toplevel(self.root)
        self.del_root.geometry('400x200')
        self.del_root.title("Delete Quiz window")
        self.del_root.grid_columnconfigure(0, weight=1)
        self.del_root.grid_columnconfigure(1, weight=1)

        self.quiz_to_del = ttk.Combobox(self.del_root, values=self.quizzes_list, font=('Arial', 20))
        self.quiz_to_del.set('Choose quiz to delete')
        self.quiz_to_del.grid(row=0, columnspan=2, column=0, pady=20, padx=40)

        Button(self.del_root, text="Delete", font=('Arial', 20), bg="gray", command=self.submit_del)\
            .grid(row=2, column=0, padx=20, pady=50, ipadx=10, sticky=W)

        Button(self.del_root, text="Close", font=('Arial', 20), bg="gray", command=self.del_root.destroy)\
            .grid(row=2, column=1, padx=20, pady=50, ipadx=15, sticky=E)

        self.del_root.grab_set()

    def submit_del(self):
        try:
            if self.quiz_to_del.get() == "Choose quiz to delete":
                tkinter.messagebox.showinfo(title="Information", message="Please choose quiz to delete.")
            else:
                delete_table = "DROP TABLE `{}`".format(self.quiz_to_del.get())
                self.cursor.execute(delete_table)
                self.quizzes_list.remove(self.quiz_to_del.get())
                self.quiz_to_del.configure(values=self.quizzes_list)
                tkinter.messagebox.showinfo(title="Information", message="Quiz successfully deleted.")
        except mysql.connector.errors.ProgrammingError:
            tkinter.messagebox.showinfo(title="Information",
                                        message="Quiz with this name don't exists, please try again.")

    def get_list_of_quizzes(self):
        get_user_tables = "SELECT table_name FROM information_schema.tables WHERE table_type='BASE TABLE'" \
                          " AND table_schema = 'quiz' AND NOT table_name = 'history' AND NOT table_name = 'physics'" \
                          " AND NOT table_name = 'biology' AND NOT table_name = 'geography'" \
                          " AND NOT table_name = 'health'"
        self.cursor.execute(get_user_tables)
        rows = self.cursor.fetchall()
        self.quizzes_list.clear()
        for row in rows:
            row = row[0]
            self.quizzes_list.append(row)


class Quiz:
    def __init__(self, root, quiz_name, quizzes_list, connection, cursor):
        self.quizzes_list = quizzes_list
        self.root = root
        self.connection = connection
        self.cursor = cursor
        self.question_number = 1
        self.limit = 60
        self.quiz_name = quiz_name
        self.timer_works = False
        self.points = []
        self.user_answer = ""

    def layout(self):
        get_question = 'SELECT * FROM quiz.{} WHERE QuestionNumber= {}'\
            .format(self.quiz_name, self.question_number)
        get_last_question_number = 'SELECT QuestionNumber FROM quiz.{} ORDER BY CAST(QuestionNumber AS unsigned)' \
                                   ' DESC LIMIT 1'\
            .format(self.quiz_name)

        self.cursor.execute(get_question)
        rows = self.cursor.fetchall()
        get_question = rows[0][1]
        self.get_answer1 = rows[0][2]
        get_answer2 = rows[0][3]
        get_answer3 = rows[0][4]
        get_answer4 = rows[0][5]
        self.now = rows[0][0]

        self.cursor.execute(get_last_question_number)
        rows = self.cursor.fetchall()
        self.all_q = rows[0][0]

        answers = [self.get_answer1, get_answer2, get_answer3, get_answer4]
        self.randomized_answers = random.sample(answers, k=4)

        self.root.grid_columnconfigure(0, weight=1)

        self.top_frame = Frame(self.root, bg="light gray")
        self.top_frame.grid(row=0, column=0, sticky=N, pady=20)

        self.center_frame = Frame(self.root, bg="light gray")
        self.center_frame.grid(row=1, column=0, sticky=N)
        self.center_frame.grid_rowconfigure(0, weight=1)

        self.bottom_frame = Frame(self.root, bg="light gray")
        self.bottom_frame.grid(row=2, column=0, sticky=S)
        self.bottom_frame.grid_columnconfigure(0, weight=2)
        self.bottom_frame.grid_columnconfigure(1, weight=1)

        Label(self.top_frame, text=self.quiz_name, font=('Arial', 30))\
            .grid(row=0, column=0, ipadx=50, ipady=20, sticky=N, padx=450)

        Label(self.top_frame, text=get_question, font=('Arial', 20), width=60, height=4, wraplength=900)\
            .grid(row=1, column=0, pady=10, sticky=N)

        self.time = Label(self.top_frame, text=self.limit, font=('Arial', 35))
        self.time.grid(row=0, column=0, sticky=NE, padx=10)

        if not self.timer_works:
            self.timer()
            self.timer_works = True
        else:
            pass
        self.answer1_state = BooleanVar()
        self.answer2_state = BooleanVar()
        self.answer3_state = BooleanVar()
        self.answer4_state = BooleanVar()

        self.answer1 = Checkbutton(self.center_frame, text=self.randomized_answers[0], font=('Arial', 20), width=30,
                                   height=3, wraplength=450, variable=self.answer1_state, onvalue=True, offvalue=False,
                                   command=self.is_checked)
        self.answer1.grid(row=0, column=0, sticky=N, pady=10, padx=20)

        self.answer2 = Checkbutton(self.center_frame, text=self.randomized_answers[1], font=('Arial', 20), width=30,
                                   height=3, wraplength=450, variable=self.answer2_state, onvalue=True, offvalue=False,
                                   command=self.is_checked)
        self.answer2.grid(row=0, column=1, pady=10, padx=20)

        self.answer3 = Checkbutton(self.center_frame, text=self.randomized_answers[2], font=('Arial', 20), width=30,
                                   height=3, wraplength=450, variable=self.answer3_state, onvalue=True, offvalue=False,
                                   command=self.is_checked)
        self.answer3.grid(row=1, column=0, pady=20, padx=20)

        self.answer4 = Checkbutton(self.center_frame, text=self.randomized_answers[3], font=('Arial', 20), width=30,
                                   height=3, wraplength=450, variable=self.answer4_state, onvalue=True, offvalue=False,
                                   command=self.is_checked)
        self.answer4.grid(row=1, column=1, pady=20, padx=20)

        Label(self.bottom_frame, text="{}/{}".format(self.now, self.all_q), font=('Arial', 20))\
            .grid(row=1, column=0, pady=5, padx=10)

        Button(self.bottom_frame, text="Next question", font=('Arial', 20), width=30,
               command=self.next_question, bg="gray")\
            .grid(row=0, column=0, pady=15, padx=550)

        Button(self.bottom_frame, text="Exit", font=('Arial', 20), command=self.exit, bg="gray")\
            .grid(row=1, column=0, padx=10, sticky=SE, columnspan=2, rowspan=2, pady=5)

    def next_question(self):
        if self.answer1_state.get() == False and self.answer2_state.get() == False and\
                self.answer3_state.get() == False and self.answer4_state.get() == False:
            result = tkinter.messagebox.askquestion(title='Warning', message="You didn't choose answer, continue?")
            if result == "yes":
                self.change_question()
            if result == "no":
                pass
        else:
            self.check_answer()
            self.change_question()

    def change_question(self):
        self.limit = 60
        self.question_number += 1
        if int(self.question_number) <= int(self.all_q):
            self.bottom_frame.destroy()
            self.center_frame.destroy()
            self.top_frame.destroy()
            self.layout()
        else:
            self.bottom_frame.destroy()
            self.center_frame.destroy()
            self.top_frame.destroy()

            earned_points = len(self.points)

            self.result_frame = Frame(self.root, bg="light gray")
            self.result_frame.grid(row=0, column=0, sticky=EW)

            Label(self.result_frame, text="Quiz is over", font=('Arial', 50), bg="light grey") \
                .grid(row=0, column=0, padx=500, pady=40)
            Label(self.result_frame, text="Your results:", font=('Arial', 35), bg="light grey") \
                .grid(row=1, column=0, pady=70)
            Label(self.result_frame, text="{}/{}".format(earned_points, self.all_q), bg="light grey",
                  font=('Arial', 35)) \
                .grid(row=2, column=0, pady=40)
            Button(self.result_frame, text="Exit to menu", font=('Arial', 20), bg="grey", command=self.exit_to_menu) \
                .grid(row=3, column=0, pady=90)
            Button(self.result_frame, text="Try Again", font=('Arial', 20), bg="grey", command=self.try_again) \
                .grid(row=3, column=0, sticky=W, padx=60)

    def try_again(self):
        self.result_frame.destroy()
        restart_quiz = Quiz(self.root, self.quiz_name, self.quizzes_list, self.connection, self.cursor)
        restart_quiz.layout()

    def exit_to_menu(self):
        self.result_frame.destroy()
        exit_to_main_menu = MainApp()
        exit_to_main_menu.menu(self.root, self.quizzes_list)

    def timer(self):
        self.limit -= 1
        if self.limit >= 0:
            self.time.configure(text=self.limit)
            self.root.after(1000, self.timer)

        elif self.limit == -1:
            self.user_answer = ""
            self.next_question()

    def check_answer(self):
        correct_answer = ""
        for answer in self.randomized_answers:
            if answer == self.get_answer1:
                correct_answer = answer
            else:
                pass
        else:
            if self.user_answer == correct_answer:
                self.points.append(self.now)
            else:
                pass

    def is_checked(self):
        self.user_answer = ""
        if self.answer1_state.get():
            self.user_answer = self.answer1.cget('text')
            self.answer2.configure(state="disabled")
            self.answer3.configure(state="disabled")
            self.answer4.configure(state="disabled")

        elif self.answer2_state.get():
            self.user_answer = self.answer2.cget('text')
            self.answer1.configure(state="disabled")
            self.answer3.configure(state="disabled")
            self.answer4.configure(state="disabled")

        elif self.answer3_state.get():
            self.user_answer = self.answer3.cget('text')
            self.answer1.configure(state="disabled")
            self.answer2.configure(state="disabled")
            self.answer4.configure(state="disabled")

        elif self.answer4_state.get():
            self.user_answer = self.answer4.cget('text')
            self.answer1.configure(state="disabled")
            self.answer2.configure(state="disabled")
            self.answer3.configure(state="disabled")

        elif not self.answer1_state.get():
            self.user_answer = self.answer1.cget('text')
            self.answer1.configure(state="active")
            self.answer2.configure(state="active")
            self.answer3.configure(state="active")
            self.answer4.configure(state="active")

        elif not self.answer2_state.get():
            self.user_answer = self.answer2.cget('text')
            self.answer1.configure(state="active")
            self.answer3.configure(state="active")
            self.answer4.configure(state="active")

        elif not self.answer3_state.get():
            self.user_answer = self.answer3.cget('text')
            self.answer1.configure(state="active")
            self.answer2.configure(state="active")
            self.answer4.configure(state="active")

        elif not self.answer4_state.get():
            self.user_answer = self.answer4.cget('text')
            self.answer1.configure(state="active")
            self.answer2.configure(state="active")
            self.answer3.configure(state="active")

    def exit(self):
        confirm = tkinter.messagebox.askquestion(title='Warning', message="Do you want to exit?")
        if confirm == "yes":
            self.bottom_frame.destroy()
            self.center_frame.destroy()
            self.top_frame.destroy()
            self.quiz_name = ""
            app = MainApp()
            app.menu(self.root, self.quizzes_list)
        elif confirm == "no":
            pass


def main():
    run_app = MainApp()
    run_app.create()
    mainloop()


if __name__ == '__main__':
    main()
