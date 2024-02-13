import RPi.GPIO as GPIO
from datetime import datetime
import json
import time

GPIO.setmode(GPIO.BCM)


class ButtonAndLamp:
    def __init__(self, pin):
        self.pin = pin
        self.status_sw = 0
        self.status_lamp = 0

    def update(self):
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.status_sw = GPIO.input(self.pin)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, self.status_lamp)


datetime_old = datetime.now()
run_step = 1
HIGH = 0
LOW = 1

re_b = ButtonAndLamp(7)
ok_b = ButtonAndLamp(8)

I = {
    # "Button Input 1": 7,
    # "Button Input 2": 8,
    "Senser Infrared 0": 5,
    "Senser Infrared 1": 12,
    "Senser Infrared 2": 20,
    "Senser Infrared 3": 16,
    "Reed Switch 11": 6,
    "Reed Switch 12": 13,
    "Reed Switch 21": 19,
    "Reed Switch 22": 21,
}
O = {
    # "Button_LED_1": 22,
    # "Button_LED_2": 24,
    "Stopper_1": 4,
    "Stopper_2": 18,
    "buzzer": 22
}
IO = {}
IO.update(O)
IO.update(I)

for k, v in I.items():
    GPIO.setup(v, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
for k, v in O.items():
    GPIO.setup(v, GPIO.OUT)


def on(pin):
    if not pin.isnumeric():
        pin = O.get(pin)
    pin = int(pin)
    GPIO.output(pin, GPIO.HIGH)
    print(f'func >> {pin} is on')


def off(pin):
    if not pin.isnumeric():
        pin = O.get(pin)
    pin = int(pin)
    GPIO.output(pin, GPIO.LOW)
    print(f'func >> {pin} is off')


def read(pinstr):
    if type(pinstr) == str:
        pin = I.get(pinstr)
    else:
        pin = pinstr
    res = GPIO.input(pin)
    # inv = [1,0]
    # res = inv[res]
    print(f'func >> {pinstr} is {res}')
    return res


def readall():
    data = {}
    for name, pin in IO.items():
        res = GPIO.input(pin)
        data[name] = [pin, res]
    print(f'func >> readall == {data}')
    return data


def main_program():
    global run_step, datetime_old
    print(run_step)
    re_b.update()
    ok_b.update()

    if 2 <= run_step <= 5:
        if read("Senser Infrared 1") == HIGH and read("Senser Infrared 2") == HIGH:
            # sen1 sen2 เจอ --> stop2 ลงมาเหยียบ
            on('Stopper_2')

    if run_step == 1:
        if read("Senser Infrared 0") == LOW and read("Senser Infrared 3") == LOW:
            # sen0 sen1 ไม่เจอ --> stopper1 ลง  ### เพื่อรอ pcb มา
            on('Stopper_1')
            run_step = 2

    elif run_step == 2:
        if read("Senser Infrared 3") == HIGH:
            # sen1 เจอ --> ___ ### ถ้าเจอ pcb มา delay รอถ่ายภาพ
            run_step = 3
            datetime_old = datetime.now()

    elif run_step == 3:
        if (datetime.now() - datetime_old).total_seconds() > 4:
            # หน่วงเวลา รอให้กล้องถ่ายภาพ
            run_step = 4

    elif run_step == 4:
        # บอกให้ predict
        with open('/home/pi/autorun/static/data.txt', 'w') as f:
            f.write('capture and predict')
        run_step = 5

    elif run_step == 5:
        # อ่านผลลัพธ์
        with open('/home/pi/autorun/static/data.txt') as f:
            res = f.read()
            print("res", res)

        if res == 'ok':
            run_step = 6
        if res == 'ng':
            run_step = 10
        else:
            time.sleep(0.1)

    elif run_step == 6:  # OK
        off('Stopper_1')
        run_step = 7
        datetime_old = datetime.now()

    elif run_step == 7:
        # หน่วงเวลา
        if (datetime.now() - datetime_old).total_seconds() > 2:
            off('Stopper_2')
            run_step = 8
    elif run_step == 8:
        with open('/home/pi/autorun/static/data.txt', 'w') as f:
            f.write('None')
        run_step = 1
    elif run_step == 10:
        re_b.status_lamp = 1
        ok_b.status_lamp = 1
        run_step = 11
        datetime_old = datetime.now()

    elif run_step == 11 and (datetime.now() - datetime_old).total_seconds() > 2:
        if re_b.status_sw == 0:
            run_step = 4  # reset
            re_b.status_lamp = 0
            ok_b.status_lamp = 0
        if ok_b.status_sw == 0:
            run_step = 6  # bypass
            re_b.status_lamp = 0
            ok_b.status_lamp = 0

    if run_step == 11:  # ng
        on('buzzer')
    else:
        off('buzzer')


if __name__ == '__main__':
    # while True:
    # try:
    if True:
        if True:

            with open("/home/pi/autorun/static/log.txt", 'a', encoding='utf-8') as f:
                f.write(f'{datetime.now()} run io\n\n')
            old_txt = '0'
            txt = '0'
            step_text = [
                'step 0',
                'ต้องไม่มีอะไรขวาง Infrared Senser 0 and 1 เพื่อจะให้ stoper 1 ลงมากั้น',
                'รอ PCB เข้ามา',
                'หน่วงเวลา รอให้กล้องถ่ายภาพ',
                'บอกให้ computer predict',
                'รออ่านผลลัพธ์ จากการ predict',
                'ปล่อย PCB โดย การยก Stopper_1 ขึ้น',
                'หน่วงเวลา รอยก Stopper_2 ขึ้น',
                'step 8',
                'step 9',
                'NG',
                'retry or bypass',
            ]
            while True:

                with open('/home/pi/autorun/static/run.txt') as f:
                    old_txt = txt
                    txt = f.read()
                printt = f'{datetime.now()} run={txt} run_step={run_step}'
                print(printt)
                with open("/home/pi/autorun/static/step.txt", 'w') as f:
                    print(run_step,type(run_step))
                    step_text = [
                'step 0',
                'ต้องไม่มีอะไรขวาง Infrared Senser 0 and 1 เพื่อจะให้ stoper 1 ลงมากั้น',
                'รอ PCB เข้ามา',
                'หน่วงเวลา รอให้กล้องถ่ายภาพ',
                'บอกให้ computer predict',
                'รออ่านผลลัพธ์ จากการ predict',
                'ปล่อย PCB โดย การยก Stopper_1 ขึ้น',
                'หน่วงเวลา รอยก Stopper_2 ขึ้น',
                'step 8',
                'step 9',
                'NG',
                'retry or bypass',
            ]
                    print(step_text)
                    print(step_text[run_step])
                    print(f'{printt}\n{step_text[run_step]}')
                    f.write(f'{printt}\n{step_text[run_step]}')
                if old_txt == '0' and txt == '1':  # สั่งrun
                    run_step = 1

                elif old_txt == '1' and txt == '0':  # สั่งหยุด
                    off('Stopper_1')
                    off('Stopper_2')

                elif txt == '0':
                    off('Stopper_1')
                    off('Stopper_2')

                elif txt == '1':
                    main_program()

                time.sleep(0.1)

        # except:        
        # # except Exception as e:
        # # with open("/home/pi/autorun/static/log.txt", 'a') as f:
        # # f.write(f'{datetime.now()}\n{e}\n\n')
        # time.sleep(3)
Traceback (most recent call last):
  File "/home/pi/autorun/io_rasp.py", line 226, in <module>
    print(step_text)
UnicodeEncodeError: 'latin-1' codec can't encode characters in position 12-28: ordinal not in range(256)

