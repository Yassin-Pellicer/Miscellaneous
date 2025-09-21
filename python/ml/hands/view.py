import cv2
import mediapipe as mp
import numpy as np
import pickle
import os
import time
import landmarks as lm   # your custom landmarks file

def open_pickle(filename):
  with open(filename, "rb") as f:
    data = pickle.load(f)
    for entry in data:
      return entry["points"]

def print_image(filename, index):
  points = open_pickle(filename)

  def draw_image(i):
    image = np.zeros((500, 500, 3), dtype=np.uint8)
    for (x, y) in points[i]:
      image[int(np.floor(y)), int(np.floor(x))] = [0, 255, 0]
    cv2.imshow("Image", image)
    cv2.setMouseCallback('Image', onclick)

  def onclick(event, x, y, flags, param):
    nonlocal index
    if event == cv2.EVENT_LBUTTONDOWN:
      index = (index + 1) % len(points)
    draw_image(index)

  draw_image(index)

  cv2.waitKey(0)
  cv2.destroyAllWindows()

  
if __name__ == "__main__":
  index = 19
  print_image("pickles/casa.pickle", index)

