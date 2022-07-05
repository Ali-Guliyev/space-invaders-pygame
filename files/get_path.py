import os

path_arr = os.getcwd().split("\\")

if (path_arr[len(path_arr) - 1] != "space-invaders"):
  path_arr.pop(len(path_arr) - 1)

print(path_arr)

path = ""
for i in path_arr:
  path += i + "/"