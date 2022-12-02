import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from pymongo import MongoClient
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

client = MongoClient('복붙하기')
db = client["pmsbme"]  # pmsbme 데이터베이스 불러오기
pms = db["pms"]
bme = db["bme"]


class Graph(QMainWindow):
    def __init__(self):
        super().__init__()

        self.count_prev = []  # 공공데이터 정보에 대한 시간을 담기 위한 리스트
        self.temp_prev = []  # 온도 공공데이터 값을 담기 위한 리스트
        self.humidity_prev = []  # 습도 공공데이터 값을 담기 위한 리스트

        for d, cnt in zip(db['bme'].find().sort('date', -1), range(100, 0, -1)):  # mongdb에 맞춰서 수정
            self.count_prev.append(d['date'])  # 시간을 count_prev에 저장
            self.temp_prev.append(int(d['temp']))  # temp_prev의 값을 저장
            self.humidity_prev.append(int(d['humi']))  # humidity_prev의 값을 저장

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        vbox = QVBoxLayout(self.main_widget)

        graph_bms = FigureCanvas(Figure(figsize=(4, 4)))
        self.addToolBar(NavigationToolbar(graph_bms, self))
        vbox.addWidget(graph_bms)
        self.graph_bme_ax = graph_bms.figure.subplots()
        self.graph_bme_ax.plot(self.count_prev, self.temp_prev, color='red')
        self.graph_bme_ax.plot(self.count_prev, self.humidity_prev, color='blue')

        graph = FigureCanvas(Figure(figsize=(4, 4)))
        self.addToolBar(NavigationToolbar(graph, self))
        vbox.addWidget(graph)
        self.graph_ax = graph.figure.subplots()
        self.timer = graph.new_timer(100, [(self.update_graph, (), {})])  # 0.1초 간격으로 호출
        self.timer.start()

        hbox = QHBoxLayout(self.main_widget)
        vbox.addLayout(hbox)
        
        self.tempStatus = QTextEdit()
        hbox.addWidget(self.tempStatus)

        self.humStatus = QTextEdit()
        hbox.addWidget(self.humStatus)

        self.airStatus = QTextEdit()
        hbox.addWidget(self.airStatus)

        self.airStandard = QTextEdit()
        self.airStandard.setText('좋음: 0~30\n보통: 31~80\n나쁨: 81~150\n매우 나쁨: 151 이상')
        hbox.addWidget(self.airStandard)

        self.setWindowTitle("미세먼지 측정")
        self.setGeometry(300, 100, 600, 600)
        self.show()


    def update_graph(self):  # 그래프 변화 함수

        self.count_pms = []  # 미세먼지 정보에 대한 시간을 담기 위한 리스트
        self.pm10 = []  # pm10의 값을 담기 위한 리스트
        self.pm25 = []  # pm25의 값을 담기 위한 리스트
        self.pm1 = []  # pm1의 값을 담기 위한 리스트
        self.count_bme = []  # 온습도 정보에 대한 시간을 담기 위한 리스트
        self.temp = []  # temp의 값을 담기 위한 리스트
        self.humidity = []  # humidity의 값을 담기 위한 리스트

        for d, cnt in zip(db['pms'].find().sort('date', -1), range(100, 0, -1)):  # mongodb에 맞춰서 수정
            self.count_pms.append(d['date'])  # 시간을 count에 저장
            self.pm1.append(int(d['pm1']))  # pm1의 값을 저장
            self.pm25.append(int(d['pm25']))  # pm25의 값을 저장
            self.pm10.append(int(d['pm10']))  # pm10의 값을 저장

        for d, cnt in zip(db['bme'].find().sort('date', -1), range(100, 0, -1)):  # mongodb에 맞춰서 수정
            self.count_bme.append(d['date'])  # 시간을 count에 저장
            self.temp.append(int(d['temp']))  # temp의 값을 저장
            self.humidity.append(int(d['humi']))  # humidity의 값을 저장

        status1 = f"현재 미세먼지 농도는 {self.pm10[0]}입니다."
        status2 = f"온도: {self.temp[0]}"
        status3 = f"습도: {self.humidity[0]}"

        self.tempStatus.setText(status2)
        self.humStatus.setText(status3)
        self.airStatus.setText(status1)

        self.graph_ax.clear()  # 그래프 초기화
        self.graph_ax.plot(self.count_pms, self.pm25, color='pink')  # 점 찍기
        self.graph_ax.plot(self.count_pms, self.pm1, color='red')  # 점 찍기
        self.graph_ax.plot(self.count_pms, self.pm10, color='blue')  # 점 찍기
        self.graph_ax.figure.canvas.draw()  # 그리기


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Graph()
    sys.exit(app.exec_())
