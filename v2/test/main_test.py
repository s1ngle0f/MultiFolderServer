import os


# def prepare_zippath(s):
#     s = s.replace(chr(92), '/')
#     char = '/'
#     while char * 2 in s:
#         s = s.replace(char * 2, char)
#     return os.path.relpath(s, '/').replace(chr(92), '/')

# print(prepare_zippath('\\Coursework_1sem_3course\\coursework\\src\\main\\resources\\static\\vendors\\themify-icons\\SVG\\layout-media-overlay-alt-2.svg'))

import subprocess

# result = subprocess.run(['sudo', 'pwd'], capture_output=True, text=True)
username = 'user1'
password = '123123'
result = subprocess.run(["sudo", "useradd", "-m", username])
# result = subprocess.run(["sudo", "useradd", username], input=f"{password}\n{password}\n\n\n\n\n\n\n".encode())
print(result.stdout)
# result = subprocess.run(["su", "-", username])
# print(result.stdout)
result = subprocess.run(["su", username, "-c", "mkdir -p ~/.ssh"])
print(result.stdout)
result = subprocess.run(["su", username, "-c", "touch ~/.ssh/authorized_keys"])
print(result.stdout)
result = subprocess.run(["su", username, "-c", "chmod 600 ~/.ssh/authorized_keys"])
print(result.stdout)
result = subprocess.run(["su", username, "-c", "chmod 700 ~/.ssh"])
print(result.stdout)

with open(f"/home/{username}/.ssh/authorized_keys", 'r') as file:
    lines = file.read()
    for line in lines:
        print(line)
        file.w

# result = subprocess.run(["su", "-", username])
# print(result.stdout)
# result = subprocess.run(["pwd"])
# print(result.stdout)

# result = subprocess.run(["su", "-", username, '\n', "pwd"])
# print(result.stdout)