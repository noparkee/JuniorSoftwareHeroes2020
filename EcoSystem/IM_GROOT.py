#####
#   이수하 / 포항제철중 
#####

import learn_mod
import RPi.GPIO as GPIO
import dateTime
import time
import spidev
import pigpio
import smbus
import os
import DHT22        # 온습도 센서

# 사용할 i2c 채널 번호
I2C_CH = 1
# BH1750 주소
BH1750_DEV_ADDR = 0x23

# 조도의 측정
# 값이 1lx 단위로 측정되며 샘플링 시간은 120ms이고 계속 측정하는 모드
CONT_H_RES_MODE     = 0x10

i2c = smbus.SMBus(I2C_CH)

# dhtDevice = adafruit_dht.DHT11(board.D4)
# 팬의 핀을 5번, 6번 핀으로 설정하고 펌프의 핀을 23번, 24번으로 설정합니다.
pins = {'pan1':5, 'pin':6, 'pump1':23, 'pump2':24}

# R, G, B의 핀을 각각 19, 21, 20으로 설정합니다.
ledfs = {'r':19, 'g':21, 'b':20}

# GPIO 핀 모드를 BCM으로 설정합니다.
GPIO.setmode(GPIO.BCM)

# 각 핀을 출력으로 설정하고, HIGH로 설정해 LED를 끕니다.
for i in leds:
    GPIO.setup(leds[i], GPIO.OUT)
    GPIO.output(leds[i], GPIO.HIGH)

for i in pins:
    GPIO.setup(pins[i], GPIO.OUT)
    GPIO.output(pins[i], GPIO.HIGH)


# 라이브러리
pi = pigpio.pi()

s = DHT22.sensor(pi, 4)

s.trigger()
time.sleep(0.5)

# 시간에 대한 리스트
timelist = []
# 습도에 대한 리스트
humlist = []
# 온도에 대한 리스트
templist = []



# window 함수를 정의합니다.
def windowcontrol(win_open):
    if (win_open):
        pi.set_servo_pulsewidth(13, 1200) # 13번 채널에 연결된 서보모터를 90도로 이동
    else:
        pi.set_servo_pulsewidth(13, 500) # 13번 채널에 연결된 서보모터를 0도로 이동

def panpump(hum, temp):
    if (70. > hum):
        os.system('mpg321 /home/pi/JUSOHE/week7/mp3/hum_motor_run.mp3')
        print("습도 낮음")
        GPIO.output(pins['pump1'], GPIO.HIGH)
        GPIO.output(pins['pump2'], GPIO.LOW)
    else:
        print("습도 정상")
        GPIO.output(pins['pump1'], GPIO.LOW)
        GPIO.output(pins['pump2'], GPIO.LOW)
    
    # 0.1초만 펌프 동작
    time.sleep(0.1)
    GPIO.output(pins['pump1'], GPIO.LOW)
    GPIO.output(pins['pump2'], GPIO.LOW)

    if (28. < temp):
        print("더워서 창문을 열어요")
        os.system('mpg321 /home/pi/JUSOHE/week7/mp3/high_win_open.mp3')
        windowcontrol(True)
    else:
        if (26. < temp):
            print("더워서 팬을 돌려요")
            os.system('mpg321 /home/pi/JUSOHE/week7/mp3/high_fan_run.mp3')
            GPIO.output(pins['pan1'], GPIO.HIGH)
            GPIO.output(pins['pan2'], GPIO.LOW)
    
    # 5초간 팬 동작 후 초기화
    time.sleep(5)
    GPIO.output(pins['pan1'], GPIO.LOW)
    GPIO.output(pins['pan2'], GPIO.LOW)


# luxledcontrol 함수를 정의합니다.
def luxledcontrol(hum, temp):
    luxBytes = i2c.read_i2c_block_data(BH1750_DEV_ADDR, CONT_H_RES_MODE, 2)
    lux = int.from_bytes(luxBytes, byteorder='big')

    if lux >= 800:
        print('{0}lux RED LED on. ITS TOO BRIGHT NOW !'.format(lux))
        # 빨간색 LED를 킵니다.
        GPIO.output(leds['r'], GPIO.LOW)
        GPIO.output(leds['g'], GPIO.HIGH)
        GPIO.output(leds['b'], GPIO.HIGH)
    else:
        print('{0}lux'.format(lux))

        #초록색 LED를 킵니다.
        GPIO.output(leds['r'], GPIO.HIGH)
        GPIO.output(leds['g'], GPIO.LOW)
        GPIO.output(leds['b'], GPIO.HIGH)

    win_door = pi.get_servo_pulsewidth(13)
    if ( win_door == 1200 and 28. > temp and 50. > lux):
        print("어두워서 창문을 닫아요")
        os.system('mpg321 /home/pi/JUSOHE/week7/mp3/dark_win_close.mp3')
        windowcontrol(False)
    
    else:
        if (win_dppr == 1200 and 22. > temp):
            print("추워서 창문을 닫아요")
            os.system('mpg321 /home/pi/JUSOHE/week7/mp3/cold_win_close.mp3')
            windowcontrol(False)
        else:
            print("식물이 좋아요")



# 창문 열기
pi.set_servo_pulsewidth(13, 0)      # 13번 채널에 연결된 서보모터를 꺼줍니다.
time.sleep(1)
windowcontrol(False)    # 닫힘
time.sleep(1)
os.system('mpg321 /home/pi/JUSOHE/week7/mp3/first_win_open.mp3')
windowcontrol(True)     # 열기

dataMag = 20    # 데이터 횟수
step = 30       # 학습 횟수

i = 0
# i가 step값 보다 작은 범위 내에서 아래 과정을 반복합니다.
try:
    while True:

        # 센서값을 읽어서 저장합니다.
        s.trigger()
        time.sleep(.5)

        h = s.humidity()
        t = s.temperature()

        # 현재 시각에 대한 값을 저장합니다.
        now = datetime.datetime.now()

        # 시각을 시, 분, 초로 나타냅니다.
        nowTime = now.strftime('%H: %M: %S')

        # 온도 습도를 형식에 맞게 출력합니다.
        print('{0} Temp = {1:0.01f}*C Humidity = {2:0.01f}%'.format(nowTime, t, h))

        # i를 시간의 리스트 값으로 추가합니다.
        timelist.append(i)
        
        # 측정된 습도값을 리스트값에 추가합니다.
        humilist.append(h)
        
        # 측정된 온도값을 리스트값에 추가합니다.
        templist.append(t)
        
        # 실제 시간간격을 0.01초로 설정합니다.
        time.sleep(.01)

        if i % dataMag == 0 and i != 0:
             
            w_h, b_h = learn.LinearRegression(step , 0.001, humilist, timelist, dataMag)
            w_t, b_t = learn.LinearRegression(step , 0.001, templist, timelist, dataMag)     
             
            timeNext = dataMag

            s.trigger()
            time.sleep(.5)

            print("w_h: {0} b_h: {1}".format(W_h, b_h))
            next_hum = w_h * timeNext + b_h
            real_hum = s.humidity()
            print("예측 습도:{0} 실제 습도:{1} 오차:{2}".format(next_hum, real_hum, abs(next_hum - real_num)))

            print("w_t: {0} b_t: {1}".format(W_t, b_t))
            next_temp = w_t * timeNext + b_t 
            real_temp = s.temperature()
            print("예측 온도:{0} 실제 온도:{1} 오차:{2}".format(next_temp, real_temp, abs(next_temp - real_temp)))

            i = 0

            timelist.clear()
            humilist.clear()
            templist.clear()

            panpump(next_hum, next_temp)

        else:
            i = i + 1

except KeyboardInterrupt:
    print("finish")