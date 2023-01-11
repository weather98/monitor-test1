import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import logging.handlers

monitoring = "C:\\monitoring\\"
monitoringlogs = "c:\\monitoringlogs\\"

# -----------logging--------------------------------------------

if __name__ == '__main__':

    # 1 logger instance를 만든다.
    logger = logging.getLogger("name")

    # logger handler 체크
    if len(logger.handlers) > 0:
        logger

    # 2 logger의 level을 가장 낮은 수준인 DEBUG로 설정해둔다.
    logger.setLevel(logging.DEBUG)

    # 3 formatter 지정
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(msg)s")

    # 4 handler instance 생성
    console = logging.StreamHandler()
    if not os.path.exists(monitoringlogs):
        os.makedirs(monitoringlogs)

    # 로그를 일별 파일에 자동저장
    timedfilehandler = logging.handlers.TimedRotatingFileHandler(filename=monitoringlogs+'\\'+'text.log', when='midnight', interval=1, encoding='utf-8')
    timedfilehandler.setFormatter(formatter)
    timedfilehandler.suffix = "%Y%m%d"

    # 5 handler 별로 다른 level 설정
    console.setLevel(logging.INFO)
    timedfilehandler.setLevel(logging.DEBUG)

    # 6 handler 출력 format 지정
    console.setFormatter(formatter)
    timedfilehandler.setFormatter(formatter)

    # 7 logger에 handler 추가
    logger.addHandler(console)
    logger.addHandler(timedfilehandler)
    logger.setLevel(level=logging.DEBUG)

# -----------watchdog--------------------------------------------


class Handler(FileSystemEventHandler):

    def __init__(self):  # Handler 호출시 함수 실행
        files = os.listdir(monitoring)
        global prev
        prev = None
        for file in files:
            if os.path.isfile(monitoring+file):
                curr = self.checkstate(monitoring+file)
                if prev == None:
                    prev = curr

    def on_created(self, event):  # 파일 생성시
        print(f'event type : {event.event_type}\n'

              f'event src_path : {event.src_path}')
        Handler.movefile(self, event)

    def on_deleted(self, event):
        logger.info((event.event_type, os.path.basename(event.src_path)))
        if os.path.exists(event.event_type):
            logger.error(('fail', os.path.basename(event.src_path)))

    # def on_moved(self, event): # 파일 이동시
    #     print (f'event type : {event.event_type}\n')

    def on_modified(self, event):
        if os.path.isfile(event.src_path): # 파일이 없어진 후에 로그 출력은 제거
            logger.info((event.event_type, os.path.basename(event.src_path)))
            self.checkstate(event.src_path)

            # curr가 바뀌었을때 currfile이 존재하면 movefile 실행
            curr = self.checkstate(event.src_path)
            global prev
            if prev != None and prev != curr:
                logger.info('파일이 바뀌었다 이동한다')
                Handler.movefile(self, event)

    def checkstate(self, event):
        if os.path.isfile(event):
            file_org = []
            getime = os.path.getmtime(event)
            file_org.append(getime)
            return file_org

    def movefile(self, event):  # 파일 이동 함수
        if event.is_directory:
            print("디렉토리 생성")
        else:
            """
            Fname : 파일 이름
            Extension : 파일 확장자 
            """
            Fname, Extension = os.path.splitext(
                os.path.basename(event.src_path))

            if Fname[:2] == 'IF':
                Nfolder = 'Interface'
            elif Fname[:2] == 'S ':
                Nfolder = 'Sample'
            elif Fname[:2] == 'M ':
                Nfolder = 'Micro'

            이동경로 = 'D:\\virtual_root\\'+'20'+Fname[2:4]+'\\'+Nfolder+'\\'+Fname+'\\'

            if Extension == '.jpg' or Extension == '.svs':
                if not os.path.isfile(이동경로+Fname+Extension):
                    if not os.path.exists(이동경로):
                        os.makedirs(이동경로)
                    shutil.move(event.src_path, 이동경로+Fname+Extension)
                    logger.info((event.event_type, 이동경로+Fname+Extension))
                else:
                    try:
                        i = 1
                        while i:
                            같은파일번호추가 = 이동경로+Fname+'('+str(i)+')'+Extension
                            if not os.path.isfile(같은파일번호추가):
                                shutil.move(event.src_path, 같은파일번호추가)
                                logger.info((event.event_type, 같은파일번호추가))
                                break
                            i += 1
                    except:
                        logger.error('fail', os.path.basename(event.src_path))


class Watcher:
    # 생성자
    def __init__(self, path):
        print("감시 중 ...")
        self.event_handler = None      # Handler
        self.observer = Observer()     # Observer 객체 생성
        self.target_directory = path   # 감시대상 경로
        self.currentDirectorySetting()  # instance method 호출 func(1)

    # func (1) 현재 작업 디렉토리
    def currentDirectorySetting(self):
        print("====================================")
        print("현재 작업 디렉토리:  ", end=" ")
        os.chdir(self.target_directory)
        print("{cwd}".format(cwd=os.getcwd()))
        print("====================================")

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


myWatcher = Watcher(monitoring)
myWatcher.run()
