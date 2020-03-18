import cv2
import imutils
import numpy as np
from PIL import Image
import pytesseract
from flask import Flask,jsonify,request
import os
from datetime import date

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app=Flask(__name__)

@app.route('/api/getText', methods=['POST'])
def getContour():
 try:
  f = request.files['file']
  f.save('input.jpg')
  img = cv2.imread('input.jpg', cv2.IMREAD_COLOR)

  img = cv2.resize(img, (620, 480))

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to grey scale
  gray = cv2.bilateralFilter(gray, 11, 17, 17)  # Blur to reduce noise
  edged = cv2.Canny(gray, 30, 200)  # Perform Edge detection

  # find contours in the edged image, keep only the largest
  # ones, and initialize our screen contour
  cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
  screenCnt = None

  # loop over our contours
  for c in cnts:
   # approximate the contour
   peri = cv2.arcLength(c, True)
   approx = cv2.approxPolyDP(c, 0.018 * peri, True)

   # if our approximated contour has four points, then
   # we can assume that we have found our screen
   if len(approx) == 4:
    screenCnt = approx
    break

  if screenCnt is None:
   detected = 0
   print("No contour detected")
  else:
   detected = 1

  if detected == 1:
   cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

  # Masking the part other than the number plate
  mask = np.zeros(gray.shape, np.uint8)
  new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1, )
  new_image = cv2.bitwise_and(img, img, mask=mask)

  # Now crop
  (x, y) = np.where(mask == 255)
  (topx, topy) = (np.min(x), np.min(y))
  (bottomx, bottomy) = (np.max(x), np.max(y))
  Cropped = gray[topx:bottomx + 1, topy:bottomy + 1]
  cv2.imwrite('Cropped.jpg', Cropped)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
  text = getText();
  if os.path.isfile('input.jpg'):
   os.remove('input.jpg')
  if os.path.isfile('Cropped.jpg'):
   os.remove('Cropped.jpg')
  return jsonify(text=text),200

 except:
  if os.path.isfile('input.jpg'):
   os.remove('input.jpg')
  if os.path.isfile('Cropped.jpg'):
   os.remove('Cropped.jpg')
  return jsonify(text='Please upload the correct image'),400

def getText():
 #Read the number plate
 text =  pytesseract.image_to_string(Image.open('Cropped.jpg'),lang='eng',config='--psm 6')
 return text

@app.route('/',methods=['GET','POST'])
def welcome():
 today = date.today()
 return jsonify(text='Hello its {}'.format(today))

if __name__ == '__main__':
   app.run(debug = True)