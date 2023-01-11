import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime
import time
monitoringlogs = "c:\\monitoringlogs\\"

class Handler(FileSystemEventHandler):

    def __init__(self):  # Handler 호출시 함수 실행
        files = os.listdir(monitoringlogs)
        global prev
        prev = None
        for file in files:
            if os.path.isfile(monitoringlogs+file):
                curr = self.checkstate(monitoringlogs+file)
                if prev == None:
                    prev = curr

    def on_created(self, event):  # 파일 생성시
        print(f'event type : {event.event_type}\n'

              f'event src_path : {event.src_path}')
        Handler.readfile(self, event)
        #TODO:임시로그파일도 변화를 주어야 하는지?

    def on_deleted(self, event):
        print((event.event_type, os.path.basename(event.src_path)))
        if os.path.exists(event.event_type):
            print(('fail', os.path.basename(event.src_path)))

    def on_modified(self, event):
        #TODO:파일이 존재하고 데이터 크기 변화가 있어서 작동하는지? 중복확인인지? 확장자가 log인지
        if os.path.isfile(event.src_path):
            logfile_name=os.path.basename(event.src_path)
            if logfile_name == 'text.log':          
                print((event.event_type, os.path.basename(event.src_path)))
                self.checkstate(event.src_path)

                curr = self.checkstate(event.src_path)
                global prev
                if prev != None and prev != curr:
                    print('Data modified')
                    Handler.readfile(self, event)

    def checkstate(self, event):
        if os.path.isfile(event):
            file_org = []
            getime = os.path.getmtime(event)
            file_org.append(getime)
            return file_org

    def readfile(self, event):  # 파일 이동 함수
        find_Target='error'
        prelogpath=monitoringlogs+'\\'+'temp'+'\\'+'new.log' #비교용 로그파일
        default_log = open(event.src_path,'r',encoding='utf-8')
        d_logs = default_log.readlines()
        if not os.path.isfile(prelogpath): # /temp/new.log 없으면 생성
            c = open(prelogpath,'w',encoding='utf-8')
        c = open(prelogpath,'r',encoding='utf-8')
        c_lines = c.readlines()
        if len(d_logs) != len(c_lines): # 두 로그의 열갯수가 다르다면 
            print(len(d_logs),len(c_lines))
            new_lines=d_logs[-(len(d_logs)-len(c_lines)):] 
            for line in new_lines:
                l=line.split()
                for i in range(len(l)):
                    l[i]=l[i].casefold()
                    if find_Target in l[i]:
                        filename=time.strftime("%Y%m%d-%H%M%S")+'.log'
                        pik = open(monitoringlogs+'\\'+'temp'+'\\'+filename, 'w', encoding='utf-8')
                        pik.writelines(new_lines)
                        shutil.copy(event.src_path,prelogpath)
        c.close()


class Watcher:
    # 생성자
    def __init__(self, path):
        self.event_handler = None      # Handler
        self.observer = Observer()     # Observer 객체 생성
        self.target_directory = path   # 감시대상 경로
        self.currentDirectorySetting()  # instance method 호출 func(1)

    # func (1) 현재 작업 디렉토리
    def currentDirectorySetting(self):
        print("=======================================")
        print("로그파일 모니터링:  ", end=" ")
        os.chdir(self.target_directory)
        print("{cwd}".format(cwd=os.getcwd()))
        print("=======================================")

    # func (2)
    def run(self):
        self.event_handler = Handler()  # 이벤트 핸들러 객체 생성
        self.observer.schedule(
            self.event_handler,
            self.target_directory,
            recursive=False
        )

        self.observer.start()  # 감시 시작
        try:
            while True:  # 무한 루프
                time.sleep(1)  # 1초 마다 대상 디렉토리 감시
        except KeyboardInterrupt as e:  # 사용자에 의해 "ctrl + z" 발생시
            print("감시 중지...")
            self.observer.stop()  # 감시 중단


myWatcher = Watcher(monitoringlogs)
myWatcher.run()
