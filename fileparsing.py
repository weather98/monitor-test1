import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import logging.handlers

monitoringlogs = "c:\\monitoringlogs\\"
#TODO:임시로그 파일 확장자 변하게 test
if __name__ == '__main__':
    logger = logging.getLogger("name")

    if len(logger.handlers) > 0:
        logger

    timedfilehandler = logging.handlers.TimedRotatingFileHandler(filename=monitoringlogs+'\\'+'temp'+'\\'+'new.log', when='midnight', interval=1, encoding='utf-8')
    timedfilehandler.suffix = "%Y%m%d"

    logger.addHandler(timedfilehandler)
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

    def on_deleted(self, event):
        print((event.event_type, os.path.basename(event.src_path)))
        if os.path.exists(event.event_type):
            print(('fail', os.path.basename(event.src_path)))

    def on_modified(self, event):
        #두번 parsing 한다.. on_modified 작동원리 공부 더 필요
        if os.path.isfile(event.src_path):
            logfile_name=os.path.basename(event.src_path)
            if logfile_name == 'text.log':          
                curr = self.checkstate(event.src_path)
                global prev
                if prev != None and prev != curr:
                    print(os.path.basename(event.src_path), event.event_type)
                    Handler.readfile(self, event)
                    prev=curr # 윗단에서 실행완료후 추가 prev값을 현재값으로 갱신해주어 중복작동정지

    def checkstate(self, event):
        if os.path.isfile(event):
            file_org = []
            getime = os.path.getmtime(event)
            file_org.append(getime)
            return file_org

    def readfile(self, event):
        findTarget='error' #검색할 단어 설정
        prelogpath=monitoringlogs+'\\'+'temp'+'\\'+'new.log' #비교용 로그파일
        default_log = open(event.src_path,'r',encoding='utf-8')
        d_logs = default_log.readlines()
        if not os.path.isfile(prelogpath): # /temp/new.log 없으면 생성
            c = open(prelogpath,'w',encoding='utf-8')
        c = open(prelogpath,'r',encoding='utf-8')
        c_lines = c.readlines()
        if len(d_logs) != len(c_lines): # 두 로그의 열갯수가 다르다면 
            new_lines=d_logs[-(len(d_logs)-len(c_lines)):]
            print('new lines:'+str(len(new_lines)))
            for_break = False
            for line in new_lines:
                l=line.split()
                for i in range(len(l)):
                    l[i]=l[i].casefold()
                    if findTarget in l[i]:
                        for_break = True
                        filename=time.strftime("%Y%m%d-%H%M%S")+'.log'
                        pik = open(monitoringlogs+'\\'+'temp'+'\\'+filename, 'w', encoding='utf-8')
                        pik.writelines(new_lines)
                        Handler.send_mail(Handler.convertStr(new_lines),filename)                       
                        break
                if for_break == True:
                    break
            shutil.copy(event.src_path,prelogpath)
        c.close()
 
    def send_mail(data,subject): #smtp 구글 메일 연동
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login('test@gmail.com', 'gsewmgryeogpmbvf')

        msg = MIMEText(data)
        msg['Subject'] = str(subject)

        smtp.sendmail('test@gmail.com', 'test@naver.com', msg.as_string())

        smtp.quit()

    def convertStr(arr): #리스트 문자열로 변환 함수
        str_R=""
        for s in arr:
            str_R += str(s)
        return str_R 

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
