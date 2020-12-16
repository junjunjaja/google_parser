import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLCDNumber, QDial, QVBoxLayout
import pickle
from PyQt5 import uic
from google_parser import *
from PyQt5.QtWidgets import *
from main_ui import *
uipath = "ui/"
#Ui_MainWindow = Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("text parser")
        self.search.textChanged.connect(self.search_text_input)
        self.search.returnPressed.connect(self.do_search)
        self.search_push.clicked.connect(self.do_search)
        self.print_num = 0
        self.font_box.valueChanged.connect(self.font_size)
        self.page_box.valueChanged.connect(self.page_size)
        self.font_box.setValue(13)
        self.font_box.setSingleStep(1)
        self.page_box.setValue(2)
        self.page_box.setSingleStep(1)

        self.next.clicked.connect(self.page_up)
        self.before.clicked.connect(self.page_down)

        self.split_ = 120
        self.start = 0
        self.n = self.page_box.value()
        self.end = self.n
        self.verbose = False
        self.time_ = False
        self.count = 0
        self.state = "검색어를 입력하세요"
    def font_size(self):
        val = self.font_box.value()
        self.problem.setFontPointSize(val)
        self.solution.setFontPointSize(val)
        self.problem.setText(self.problem.toPlainText())
        self.solution.setText(self.solution.toPlainText())
    def page_size(self):
        self.n = self.page_box.value()

    def search_text_input(self):
        if self.state != self.search.text():
            self.state = self.search.text()
            self.start = 0
            self.end = self.n
            self.count = 0
    def page_up(self):
        if self.limit_page > self.print_num:
            self.print_num += 1
        self.printing(self.print_num)
    def page_down(self):
        if self.print_num > 0:
            self.print_num -= 1
        else:
            return
        self.printing(self.print_num)
    def printing(self,num):
        p = self.ret.iloc[num]["prob"]
        p = p.split(". ")
        p_ = []
        for _ in p:
            if len(_) >= self.split_:
                p_.extend([_[:int(len(_)//2)],_[int(len(_)//2):]])
            else:
                p_.append(_)
        s = self.ret.iloc[num]["sol"]
        s_ = [s[i:i+self.split_] for i in range(0,len(s),self.split_)]
        self.problem.clear()
        self.solution.clear()
        for _ in p_:
            self.problem.append(_)
        for _ in s_:
            self.solution.append(_)

    def do_search(self):
        if self.count == 0:
            self.links = google_search(self.state, get_url=True,time_ = self.time_)
        else:
            self.problem.setText(f"기존 질문 {self.state[:30]}로 검색 시작")
            self.solution.clear()
        if self.end <= len(self.links):
            self.page_num.setText(f"{self.end}/{len(self.links)}")
        else:
            self.page_num.setText(f"{len(self.links)}/{len(self.links)}")
        if len(self.links) >= 1:
            if len(self.links) > self.start:
                if len(self.links) > self.end:
                    self.ret = asyncio.get_event_loop().run_until_complete(main(self.links[self.start:self.end], self.state, self.verbose, self.time_))
                else:
                    self.ret = asyncio.get_event_loop().run_until_complete(main(self.links[self.start:], self.state, self.verbose, self.time_))
            else:
                self.ret = asyncio.get_event_loop().run_until_complete(main(self.links, self.state, self.verbose, self.time_))
            self.print_num = 0
            self.printing(self.print_num)
            self.limit_page = self.ret.shape[0]-1
        else:
            self.problem.setText("need short")

        self.count += 1
        self.start += self.n
        self.end += self.n



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
