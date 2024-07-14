import numpy as np
import cv2 as cv

def showimage(img: np.ndarray, window_title: str) -> None:
    cv.imshow(window_title, img)
    cv.waitKey(0)
