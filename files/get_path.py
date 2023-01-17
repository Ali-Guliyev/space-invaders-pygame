import os

path_arr = os.getcwd().split("\\")

if ("dist" in path_arr):
  dist_i = path_arr.index("dist")
  path_arr.pop(dist_i)

path = ""
for i in path_arr:
  path += i + "/"

