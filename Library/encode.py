import base64

def enc():
    for i in range(1, 9):
        password = '%su12345' % i
        print(base64.b64encode(password.encode()))

def dec():
    password = b'MXUxMjM0NQ=='.decode('utf-8')
    print(password)

dec()