import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import date,timedelta

monitoringlogs = "c:\\monitoringlogs\\"
class logFiledestoryer:
    lpath=monitoringlogs+'\\'+'temp'+'\\'
    from datetime import date, timedelta, time, datetime
    def listUp():
        fileList = os.listdir(logFiledestoryer.lpath)
        return fileList

    def run():
        tod = date.today()
        sortList = logFiledestoryer.listUp()
        sortList.sort()
        for path in sortList:
            if date.today()-md >= timedelta(weeks=1):
                print ("remove file : ", logFiledestoryer.lpath, path)
                removeFile = os.path.join(logFiledestoryer.lpath,path)
                os.remove(removeFile)

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
        prelog_path=monitoringlogs+'\\'+'temp'+'\\'+'pre.log' #비교용 로그파일
        textlog_path = open(event.src_path,'r',encoding='utf-8')
        t_logs = textlog_path.readlines()
        if not os.path.isfile(prelog_path): # /temp/new.log 없으면 생성
            p = open(prelog_path,'w',encoding='utf-8')
        p = open(prelog_path,'r',encoding='utf-8')
        p_logs = p.readlines()
        if len(t_logs) != len(p_logs): # 두 로그의 열갯수가 다르다면 
            new_lines=t_logs[-(len(t_logs)-len(p_logs)):]
            print(len(t_logs)-len(p_logs))
            if (len(t_logs)-len(p_logs)) > 0:
                print('new lines:'+str(len(new_lines)))
                for line in new_lines:  #새로 기록된 내용에서 한번이라도 일치하면 새로운 기록된 내용 모두 보관하고 ,보내고 반복문 break 
                    for_break = False
                    l=line.split()
                    for i in range(len(l)):
                        l[i]=l[i].casefold()
                        if findTarget in l[i]:
                            for_break = True
                            Handler.createTemp_Log(new_lines)                   
                            break
                    if for_break == True:
                        break
            #모니터링 로그의 수가 더 적어졌다면 어떤 조건에 의해 기존참조파일 자체가 갱신됐으므로 내용자체를 메일전송        
            elif (len(t_logs)-len(p_logs)) < 0 : 
                num = Handler.find_prelog(os.path.dirname(prelog_path))
                date_prelog=os.path.dirname(prelog_path)+'\\'+time.strftime("%Y%m%d")+' pre'+str(num+1)+'.log'
                shutil.copy2(prelog_path, date_prelog)
                Handler.createTemp_Log(t_logs)

            shutil.copy(event.src_path,prelog_path)
        p.close()

    def createTemp_Log(content):
        filename=time.strftime("%Y%m%d-%H%M%S")+'.log'
        pik = open(monitoringlogs+'\\'+'temp'+'\\'+filename, 'w', encoding='utf-8')
        pik.writelines(content)
        Handler.send_mail(Handler.convertStr(content),filename)  

    def convertStr(arr): #리스트 문자열로 변환 함수
        str_R=""
        for s in arr:
            str_R += str(s)
        return str_R 

    def send_mail(data,subject): #smtp 구글 메일 연동
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login('test@gmail.com', 'gsewmgryeogpmbvf')

        msg = MIMEText(data) #메일 내용
        msg['Subject'] = str(subject) #메일 제목

        smtp.sendmail('test@gmail.com', 'test@naver.com', msg.as_string())
        smtp.quit()

    def find_prelog(path):
        files=os.listdir(path)
        list=[]
        for file in files:
            t=time.strftime("%Y%m%d")+' pre'
            if t in file: 
                list.append(file)
        return len(list)

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
logFiledestoryer.run()
myWatcher.run()
