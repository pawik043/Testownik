import os, sys, random, json, time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QHBoxLayout, QFrame, QStackedLayout, QGridLayout,
    QMessageBox, QInputDialog, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QColor, QFont

CONFIG_NAME = "session.json"

# ---------- Dark Progress ----------
class ProgressWidget(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.setFixedHeight(18)

    def paintEvent(self, event):
        if not self.state:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        statuses = list(self.state["status"].values())
        total = len(statuses)
        if total == 0:
            return

        w = self.width() / total

        for i, s in enumerate(statuses):
            if s == "correct": color = QColor("#30d158")  # green
            elif s == "wrong": color = QColor("#ff453a")    # red
            else: color = QColor("#ffd60a")                # yellow/orange

            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(i*w, 0, w-2, self.height(), 6, 6)

# ---------- Answer Box ----------
class AnswerBox(QFrame):
    def __init__(self, text, index, callback):
        super().__init__()
        self.index = index
        self.callback = callback
        self.selected = False

        self.setStyleSheet(self.default_style())

        layout = QVBoxLayout()
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color:#e5e5e7; font-size:16px; font-weight:600;")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def default_style(self):
        return """
        QFrame {
            background: #2c2c2e;
            border-radius: 14px;
            border: 1px solid #3a3a3c;
            padding: 14px;
        }
        """

    def selected_style(self):
        return """
        QFrame {
            background: #0a84ff33;
            border-radius: 14px;
            border: 2px solid #0a84ff;
            padding: 14px;
        }
        """

    def mousePressEvent(self, event):
        self.selected = not self.selected
        self.setStyleSheet(self.selected_style() if self.selected else self.default_style())
        self.callback(self.index, self.selected)

    def mark_correct(self):
        self.setStyleSheet("background:#30d158; border-radius:14px; color:#fff;")

    def mark_wrong(self):
        self.setStyleSheet("background:#ff453a; border-radius:14px; color:#fff;")

    def mark_missing(self):
        self.setStyleSheet("background:#ffd60a; border-radius:14px; color:#fff;")

# ---------- Main App ----------
class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz Trainer")

        self.setStyleSheet("""
            QWidget { background: #1c1c1e; color: #e5e5e7; }
            QPushButton {
                background: #2c2c2e;
                border-radius: 12px;
                padding: 10px;
                font-size: 14px;
                color: #e5e5e7;
            }
            QPushButton:hover { background: #3a3a3c; }
        """)

        self.stack = QStackedLayout()
        self.setLayout(self.stack)

        self.init_main_menu()
        self.init_quiz_ui()
        self.stack.setCurrentWidget(self.main_menu)

    def init_main_menu(self):
        self.main_menu = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Quiz Trainer")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Helvetica", 24, QFont.Bold))

        btn = QPushButton("Start Session")
        btn.clicked.connect(self.load_folder)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(btn)
        layout.addStretch()

        self.main_menu.setLayout(layout)
        self.stack.addWidget(self.main_menu)

    def init_quiz_ui(self):
        self.quiz_widget = QWidget()
        main_layout = QHBoxLayout()
        self.quiz_widget.setLayout(main_layout)

        self.left = QVBoxLayout()
        self.timer_label = QLabel("0s")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.counter_label = QLabel("0 / 0")
        self.counter_label.setAlignment(Qt.AlignCenter)

        # Add separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("color:#3a3a3c")

        self.progress = ProgressWidget(None)

        self.left.addWidget(self.timer_label)
        self.left.addWidget(self.counter_label)
        self.left.addWidget(self.progress)
        self.left.addStretch()

        main_layout.addLayout(self.left,1)
        main_layout.addWidget(line)

        self.right = QVBoxLayout()
        main_layout.addLayout(self.right,3)

        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(QFont("Helvetica",20,QFont.Bold))
        self.question_label.setStyleSheet("color:#e5e5e7; margin-bottom:15px;")

        self.answers = QGridLayout()

        self.submit_btn = QPushButton("Check")
        self.submit_btn.clicked.connect(self.check_or_next)

        self.right.addWidget(self.question_label)
        self.right.addLayout(self.answers)
        self.right.addWidget(self.submit_btn)

        self.stack.addWidget(self.quiz_widget)

        self.questions=[]; self.queue=[]; self.state={}
        self.current=None; self.selected=set(); self.boxes=[]
        self.correct_count=0
        self.waiting_next=False

        self.timer=QTimer(); self.timer.timeout.connect(self.update_timer)
        self.start_time=None

    def load_folder(self):
        folder=QFileDialog.getExistingDirectory(self)
        if not folder: return

        self.config_path=os.path.join(folder,CONFIG_NAME)
        self.questions=self.load_questions(folder)

        if os.path.exists(self.config_path):
            if QMessageBox.question(self,"Resume","Continue?",QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
                with open(self.config_path) as f:
                    self.state=json.load(f)
                self.queue=self.state["queue"]
            else:
                os.remove(self.config_path); self.new_session()
        else: self.new_session()

        self.stack.setCurrentWidget(self.quiz_widget)
        self.start_time=time.time(); self.timer.start(1000)
        self.next_q()

    def new_session(self):
        reps,_=QInputDialog.getInt(self,"Reps","Repetitions",1,1,5)
        self.state={"status":{q["file"]:"new" for q in self.questions}}
        self.queue=[]
        for q in self.questions:
            self.queue += [q["file"]]*reps
        random.shuffle(self.queue)
        self.correct_count=0

    def load_questions(self,folder):
        out=[]
        for f in os.listdir(folder):
            if f.endswith(".txt"):
                with open(os.path.join(folder,f),encoding="utf-8") as fi:
                    lines=fi.readlines()
                q=""; a=[]; c=[]
                for l in lines:
                    l=l.strip()
                    if l.startswith("?"): q=l[1:].strip()
                    elif l.startswith("*"): a.append(l[1:].strip()); c.append(len(a)-1)
                    elif l.startswith("-"): a.append(l[1:].strip())
                out.append({"file":f,"question":q,"answers":a,"correct":c})
        return out

    def next_q(self):
        if not self.queue:
            self.finish(); return

        self.waiting_next=False
        self.submit_btn.setText("Check")
        self.selected.clear()

        f=self.queue.pop(0)
        self.current=next(q for q in self.questions if q["file"]==f)
        self.render()
        self.save()

    def render(self):
        self.question_label.setText(self.current["question"])

        for i in reversed(range(self.answers.count())):
            self.answers.itemAt(i).widget().setParent(None)

        self.boxes=[]
        cols=2 if len(self.current["answers"])>2 else 1

        for i,a in enumerate(self.current["answers"]):
            b=AnswerBox(a,i,self.on_select)
            self.answers.addWidget(b,i//cols,i%cols)
            self.boxes.append(b)

        self.progress.state=self.state
        self.progress.update()
        total=len(self.questions)
        known_count=sum(1 for s in self.state['status'].values() if s=='correct')
        self.counter_label.setText(f"Known: {known_count}/{total}")

    def on_select(self,i,s):
        (self.selected.add(i) if s else self.selected.discard(i))

    def check_or_next(self):
        if self.waiting_next:
            self.next_q(); return

        cs=set(self.current["correct"])
        for i,b in enumerate(self.boxes):
            if i in cs: b.mark_correct()
            elif i in cs and i not in self.selected: b.mark_missing()
            elif i not in cs and i in self.selected: b.mark_wrong()

        f=self.current["file"]
        if self.selected==cs:
            self.state["status"][f]="correct"
        else:
            self.state["status"][f]="wrong"
            for _ in range(2):
                pos=random.randint(len(self.queue)//2,len(self.queue))
                self.queue.insert(pos,f)

        self.waiting_next=True
        self.submit_btn.setText("Next")
        self.save()

    def update_timer(self):
        self.timer_label.setText(f"{int(time.time()-self.start_time)}s")

    def finish(self):
        if os.path.exists(self.config_path): os.remove(self.config_path)
        self.timer.stop()
        QMessageBox.information(self,"Done","Session complete!")
        self.stack.setCurrentWidget(self.main_menu)

    def save(self):
        self.state["queue"]=self.queue
        with open(self.config_path,"w") as f:
            json.dump(self.state,f,indent=2)


if __name__=="__main__":
    app=QApplication(sys.argv)
    w=QuizApp(); w.resize(900,550); w.show()
    sys.exit(app.exec())
