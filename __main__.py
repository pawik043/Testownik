import os, sys, random, json, time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QHBoxLayout, QFrame, QStackedLayout, QGridLayout,
    QMessageBox, QInputDialog
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QColor, QFont, QPainterPath

CONFIG_NAME = "session.json"
RECENT_FILE = "recent.json"

# ---------- Progress Bar ----------
class ProgressWidget(QWidget):
    def __init__(self, state, counter_label=None):
        super().__init__()
        self.state = state
        self.counter_label = counter_label
        self.setFixedHeight(30)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if not self.state:
            return

        statuses = list(self.state["status"].values())
        total = len(statuses)
        if total == 0:
            return

        correct = sum(1 for s in statuses if s == 'correct')
        partial = sum(1 for s in statuses if s == 'partial')
        wrong = sum(1 for s in statuses if s == 'wrong')
        answered = correct + partial + wrong

        w = self.width()
        h = self.height()
        radius = h / 2

        painter.setPen(Qt.NoPen)

        # Smooth rounded background bar
        painter.setBrush(QColor("#3a3a3c"))
        painter.drawRoundedRect(0, 0, w, h, radius, radius)

        # Clip everything to the rounded outer shape so inner sections stay smooth
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, radius, radius)
        painter.setClipPath(path)

        if answered > 0:
            correct_w = w * correct / answered
            partial_w = w * partial / answered
            wrong_w = w * wrong / answered

            # Draw progress sections across the full bar, normalized by answered questions only
            x = 0
            if correct_w > 0:
                painter.setBrush(QColor("#30d158"))
                painter.drawRect(x, 0, correct_w, h)
                x += correct_w

            if partial_w > 0:
                painter.setBrush(QColor("#ff9f0a"))
                painter.drawRect(x, 0, partial_w, h)
                x += partial_w

            if wrong_w > 0:
                painter.setBrush(QColor("#ff453a"))
                painter.drawRect(x, 0, w - x, h)

        painter.setClipping(False)

        if self.counter_label:
            self.counter_label.setText(f"Correct: {correct}  Partial: {partial}  Wrong: {wrong}")
            self.counter_label.setFont(QFont("Helvetica", 12, QFont.Bold))

# ---------- Answer Box ----------
class AnswerBox(QFrame):
    def __init__(self, text, index, callback):
        super().__init__()
        self.index = index
        self.callback = callback
        self.selected = False
        self.setStyleSheet(self.default_style())

        layout = QVBoxLayout(); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color:#e5e5e7; font-size:16px; font-weight:600; background: transparent; border: none; padding: 0px; margin: 0px;")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def default_style(self):
        return """
        QFrame {
            background: #2c2c2e;
            border-radius: 22px;
            border: 2px solid transparent;
            padding: 16px;
        }
        QLabel {
            color: #e5e5e7;
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }
        """

    def selected_style(self):
        return """
        QFrame {
            background: #0a84ff33;
            border-radius: 22px;
            border: 2px solid #0a84ff;
            padding: 16px;
        }
        QLabel {
            color: #e5e5e7;
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }
        """

    def mousePressEvent(self, event):
        if not self.isEnabled():
            return
        self.selected = not self.selected
        self.setStyleSheet(self.selected_style() if self.selected else self.default_style())
        self.callback(self.index, self.selected)

    def mark_correct(self):
        self.selected = False
        self.setStyleSheet("""
        QFrame {
            background: #30d158;
            border-radius: 22px;
            border: 2px solid transparent;
            padding: 16px;
        }
        QLabel {
            color: #ffffff;
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
        }
        """)

    def mark_wrong(self):
        self.selected = False
        self.setStyleSheet("""
        QFrame {
            background: #ff453a;
            border-radius: 22px;
            border: 2px solid transparent;
            padding: 16px;
        }
        QLabel {
            color: #ffffff;
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
        }
        """)

    def mark_missing(self):
        self.selected = False
        self.setStyleSheet("""
        QFrame {
            background: #ffd60a;
            border-radius: 22px;
            border: 2px solid transparent;
            padding: 16px;
        }
        QLabel {
            color: #ffffff;
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
        }
        """)

# ---------- Main App ----------
class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz Trainer")
        self.setStyleSheet("""
            QWidget { background: #1c1c1e; color: #e5e5e7; }
            QPushButton { background: #2c2c2e; border-radius: 12px; padding: 10px; font-size: 14px; color: #e5e5e7; }
            QPushButton:hover { background: #3a3a3c; }
        """)

        self.stack = QStackedLayout()
        self.setLayout(self.stack)
        self.recent_paths = self.load_recent()
        self.init_main_menu()
        self.init_quiz_ui()
        self.stack.setCurrentWidget(self.main_menu)

    def load_recent(self):
        if os.path.exists(RECENT_FILE):
            with open(RECENT_FILE) as f: return json.load(f)
        return []

    def save_recent(self, path):
        if path in self.recent_paths: self.recent_paths.remove(path)
        self.recent_paths.insert(0, path)
        self.recent_paths = self.recent_paths[:3]
        with open(RECENT_FILE,'w') as f: json.dump(self.recent_paths,f)

    def init_main_menu(self):
        self.main_menu = QWidget()
        layout = QVBoxLayout()
        title = QLabel("Quiz Trainer")
        title.setAlignment(Qt.AlignCenter); title.setFont(QFont("Helvetica",24,QFont.Bold))
        btn = QPushButton("Start Session"); btn.clicked.connect(self.load_folder)
        layout.addStretch(); layout.addWidget(title); layout.addWidget(btn)
        for path in self.recent_paths:
            p_btn = QPushButton(f"{path}"); p_btn.clicked.connect(lambda _,p=path: self.load_folder(p))
            layout.addWidget(p_btn)
        layout.addStretch(); self.main_menu.setLayout(layout)
        self.stack.addWidget(self.main_menu)

    def init_quiz_ui(self):
        self.quiz_widget = QWidget()
        main_layout = QHBoxLayout(); self.quiz_widget.setLayout(main_layout)

        self.left = QVBoxLayout()
        self.return_btn = QPushButton("Return to Main Menu"); self.return_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.main_menu))
        self.reset_btn = QPushButton("Reset Session"); self.reset_btn.clicked.connect(self.reset_session)
        self.timer_label = QLabel("0 min 00 sec"); self.timer_label.setAlignment(Qt.AlignCenter); self.timer_label.setFont(QFont("Helvetica",16,QFont.Bold))
        self.counter_label = QLabel("Correct: 0  Partial: 0  Wrong: 0"); self.counter_label.setAlignment(Qt.AlignCenter); self.counter_label.setFont(QFont("Helvetica",14,QFont.Bold))
        self.mastery_label = QLabel("0 / 0"); self.mastery_label.setAlignment(Qt.AlignCenter); self.mastery_label.setFont(QFont("Helvetica",16,QFont.Bold))
        self.progress = ProgressWidget(None, self.counter_label)
        self.left.addWidget(self.return_btn)
        self.left.addWidget(self.reset_btn)
        self.left.addStretch()
        self.left.addWidget(self.timer_label)
        self.left.addStretch()
        self.left.addWidget(self.mastery_label)
        self.left.addWidget(self.counter_label)
        self.left.addWidget(self.progress)

        line = QFrame(); line.setFrameShape(QFrame.VLine); line.setStyleSheet("color:#3a3a3c")
        main_layout.addLayout(self.left,1); main_layout.addWidget(line)

        self.right = QVBoxLayout(); main_layout.addLayout(self.right,3)
        self.question_label = QLabel(); self.question_label.setWordWrap(True); self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(QFont("Helvetica",20,QFont.Bold)); self.question_label.setStyleSheet("color:#e5e5e7; margin-bottom:15px;")
        self.answers = QGridLayout(); self.answers.setSpacing(12)
        self.submit_btn = QPushButton("Check"); self.submit_btn.clicked.connect(self.check_or_next)
        self.right.addWidget(self.question_label); self.right.addLayout(self.answers); self.right.addWidget(self.submit_btn)
        self.stack.addWidget(self.quiz_widget)

        self.questions=[]; self.queue=[]; self.state={}
        self.current=None; self.selected=set(); self.boxes=[]
        self.correct_count=0; self.waiting_next=False
        self.timer=QTimer(); self.timer.timeout.connect(self.update_timer); self.start_time=None

    # ---------- Quiz logic ----------
    def load_folder(self, folder=None):
        if not folder: folder=QFileDialog.getExistingDirectory(self);
        if not folder: return
        self.save_recent(folder)
        self.config_path=os.path.join(folder,CONFIG_NAME)
        self.questions=self.load_questions(folder)
        if os.path.exists(self.config_path):
            if QMessageBox.question(self,"Resume","Continue?",QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
                with open(self.config_path) as f: self.state=json.load(f); self.queue=self.state["queue"]
                if "required_correct" not in self.state:
                    self.state["required_correct"] = {q["file"]: 1 for q in self.questions}
                if "correct_streak" not in self.state:
                    self.state["correct_streak"] = {q["file"]: 0 for q in self.questions}
            else: os.remove(self.config_path); self.new_session()
        else: self.new_session()
        self.stack.setCurrentWidget(self.quiz_widget); self.timer.start(1000)
        self.update_mastery_label()
        self.progress.state = self.state; self.progress.update()
        self.next_q()

    def new_session(self):
        reps,_=QInputDialog.getInt(self,"Reps","Repetitions",1,1,5)
        self.state={
            "status": {q["file"]: "unanswered" for q in self.questions},
            "required_correct": {q["file"]: reps for q in self.questions},
            "correct_streak": {q["file"]: 0 for q in self.questions}
        }; self.queue=[]
        for q in self.questions: self.queue += [q["file"]]*reps
        random.shuffle(self.queue); self.correct_count=0
        self.start_time = time.time()
        self.update_timer()
        self.update_mastery_label()
        self.progress.state = self.state; self.progress.update()

    def reset_session(self):
        self.new_session()
        self.waiting_next = False
        self.submit_btn.setText("Check")
        self.selected.clear()
        self.update_mastery_label()
        if self.queue:
            self.next_q()

    def update_mastery_label(self):
        required = self.state.get("required_correct", {})
        streaks = self.state.get("correct_streak", {})
        total = len(required)
        mastered = sum(1 for f, needed in required.items() if streaks.get(f, 0) >= needed)
        self.mastery_label.setText(f"{mastered} / {total}")

    def load_questions(self,folder):
        out=[]
        for f in os.listdir(folder):
            if f.endswith(".txt"):
                with open(os.path.join(folder,f),encoding="utf-8") as fi: lines=fi.readlines()
                q=""; a=[]; c=[]
                for l in lines:
                    l=l.strip()
                    if l.startswith("?"): q=l[1:].strip()
                    elif l.startswith("*"): a.append(l[1:].strip()); c.append(len(a)-1)
                    elif l.startswith("-"): a.append(l[1:].strip())
                out.append({"file":f,"question":q,"answers":a,"correct":c})
        return out

    def next_q(self):
        if not self.queue: self.finish(); return
        self.waiting_next=False; self.submit_btn.setText("Check"); self.selected.clear()
        f=self.queue.pop(0); self.current=next(q for q in self.questions if q["file"]==f)
        self.render(); self.save()

    def render(self):
        self.question_label.setText(self.current["question"])
        for i in reversed(range(self.answers.count())): self.answers.itemAt(i).widget().setParent(None)
        self.boxes = []
        paired = list(enumerate(self.current["answers"]))
        random.shuffle(paired)
        self.answer_mapping = {i: orig_i for i, (orig_i, _) in enumerate(paired)}

        cols = 2 if len(paired) > 2 else 1
        for i, (_, a) in enumerate(paired):
            b = AnswerBox(a, i, self.on_select)
            b.setEnabled(True)
            self.answers.addWidget(b, i // cols, i % cols)
            self.boxes.append(b)
        self.progress.state = self.state
        self.progress.update()

    def on_select(self,i,s): self.selected.add(i) if s else self.selected.discard(i)

    def check_or_next(self):
        if self.waiting_next:
            self.next_q()
            return
        cs_random = set(i for i, orig_i in self.answer_mapping.items() if orig_i in self.current["correct"])
        for i, b in enumerate(self.boxes):
            b.setEnabled(False)
            if i in cs_random and i in self.selected:
                b.mark_correct()
            elif i in cs_random and i not in self.selected:
                b.mark_missing()
            elif i not in cs_random and i in self.selected:
                b.mark_wrong()
        f = self.current["file"]
        if self.selected == cs_random:
            self.state["status"][f] = "correct"
            needed = self.state.get("required_correct", {}).get(f, 1)
            current_streak = self.state.get("correct_streak", {}).get(f, 0)
            if current_streak < needed:
                self.state["correct_streak"][f] = current_streak + 1
        elif self.selected and self.selected.issubset(cs_random):
            self.state["status"][f] = "partial"
            [self.queue.insert(random.randint(len(self.queue)//2, len(self.queue)), f) for _ in range(2)]
        else:
            self.state["status"][f] = "wrong"
            [self.queue.insert(random.randint(len(self.queue)//2, len(self.queue)), f) for _ in range(2)]
        self.update_mastery_label()
        self.waiting_next = True
        self.submit_btn.setText("Next")
        self.save()

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.timer_label.setText(f"{minutes} min {seconds:02d} sec")

    def finish(self):
        if os.path.exists(self.config_path): os.remove(self.config_path)
        self.timer.stop(); QMessageBox.information(self,"Done","Session complete!"); self.stack.setCurrentWidget(self.main_menu)

    def save(self):
        self.state["queue"]=self.queue
        with open(self.config_path,"w") as f: json.dump(self.state,f,indent=2)

if __name__=="__main__":
    app=QApplication(sys.argv)
    w=QuizApp(); w.resize(950,600); w.show()
    sys.exit(app.exec())
