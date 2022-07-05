import os

path_arr = os.getcwd().split("\\")
path_arr.pop(len(path_arr) - 1)
path = ""
for i in path_arr:
  path += i + "/"