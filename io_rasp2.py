step_text = [
                'step 0',
                'ต้องไม่มีอะไรขวาง'
            ]

print(step_text)


pi@raspberrypi:~/autorun $ python io_rasp2.py 
Traceback (most recent call last):
  File "/home/pi/autorun/io_rasp2.py", line 6, in <module>
    print(step_text)
UnicodeEncodeError: 'latin-1' codec can't encode characters in position 12-28: ordinal not in range(256)
