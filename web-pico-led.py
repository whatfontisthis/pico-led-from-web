# 필요한 모듈을 가져옵니다.
import network  # 네트워크 연결에 필요한 모듈
import socket  # 소켓 통신에 필요한 모듈
from time import sleep  # 잠시 멈춤을 위해 사용하는 모듈
from picozero import pico_temp_sensor, pico_led  # Pico에서 온도 센서와 LED 제어 모듈
import machine  # 하드웨어 제어를 위한 모듈

# Wi-Fi 네트워크 정보 (SSID와 비밀번호 설정)
ssid = '####' # 와이파이 이름 입력
password = '####' # 와이파이 비밀번호

def connect():
    # Wi-Fi에 연결하는 함수
    wlan = network.WLAN(network.STA_IF)  # WLAN 인터페이스 생성 (STA 모드)
    wlan.active(True)  # WLAN 활성화
    wlan.connect(ssid, password)  # 설정된 Wi-Fi 네트워크에 연결
    while not wlan.isconnected():  # 연결이 완료될 때까지 대기
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]  # 연결된 Wi-Fi의 IP 주소를 가져옴
    print(f'Connected on {ip}')  # 연결 성공 메시지 출력
    return ip  # IP 주소 반환

def open_socket(ip):
    # 소켓을 열고 준비하는 함수
    address = (ip, 80)  # IP 주소와 포트 설정 (80번 포트 사용)
    connection = socket.socket()  # 소켓 객체 생성
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 소켓 재사용 설정
    connection.bind(address)  # 소켓과 IP 주소 및 포트를 바인딩
    connection.listen(1)  # 연결 대기 (최대 1개의 클라이언트 대기 가능)
    return connection  # 소켓 객체 반환

def webpage(temperature, state):
    # HTML 페이지 템플릿 생성 함수
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Pico Server</title>
            </head>
            <body>
            <form action="./lighton">
            <input type="submit" value="Light on" />  <!-- LED를 켜는 버튼 -->
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />  <!-- LED를 끄는 버튼 -->
            </form>
            <p>LED is {state}</p>  <!-- LED의 상태 표시 -->
            <p>Temperature is {temperature}</p>  <!-- 현재 온도 표시 -->
            </body>
            </html>
            """
    return html  # HTML 코드 반환

def serve(connection):
    # 웹 서버를 시작하는 함수
    state = 'OFF'  # 초기 LED 상태는 OFF
    pico_led.off()  # LED 끄기
    temperature = 0  # 초기 온도는 0으로 설정
    while True:
        client = connection.accept()[0]  # 클라이언트 연결 수락
        request = client.recv(1024)  # 클라이언트 요청 수신 (최대 1024바이트)
        request = str(request)  # 요청 데이터를 문자열로 변환
        try:
            request = request.split()[1]  # 요청의 경로를 파싱
        except IndexError:
            pass
        # LED 제어 요청 처리
        if request == '/lighton?':  # '/lighton' 요청이 들어오면
            pico_led.on()  # LED를 켜고
            state = 'ON'  # 상태를 ON으로 변경
        elif request == '/lightoff?':  # '/lightoff' 요청이 들어오면
            pico_led.off()  # LED를 끄고
            state = 'OFF'  # 상태를 OFF로 변경
        temperature = pico_temp_sensor.temp  # 현재 온도를 읽어옴
        html = webpage(temperature, state)  # 응답 HTML 생성
        client.send(html)  # 클라이언트로 HTML 전송
        client.close()  # 클라이언트 연결 종료

# 메인 코드 실행
try:
    ip = connect()  # Wi-Fi 연결
    connection = open_socket(ip)  # 소켓 열기
    print(f"Server running at http://{ip}:80")  # 서버 실행 메시지 출력
    serve(connection)  # 웹 서버 시작
except KeyboardInterrupt:
    machine.reset()  # 키보드 인터럽트(Ctrl+C) 발생 시 Pico 재부팅

