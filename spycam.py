from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import numpy as np
import imutils
import time



class spycam(object):

	def __init__(self, alfa = 50, beta = 0, thresh = 20):
		#super().__init__()
		self.isrecord = False
		#camera
		self.cam = PiCamera()
		#impostazione framerete e risoluzione
		self.cam.resolution = (640, 480)
		self.cam.framerate = 32
		#self.stream = PiCameraCircularIO(self.cam,  size=10)
		#definizione oggetto stream
		self.stream = PiRGBArray(self.cam,  size=(640, 480))
		#definzione variabile di detect del movimento
		self._uomo = None
		#stato di detect
		self.detect = False
		#freme precedente
		self._firstFrame = None
		#frame corrente
		self._current = None
		#soglia di segmentazione
		self._thresh = thresh
		#luminosità
		self.cam.brightness = alfa
		#contrasto
		self.cam.contrast = beta




	@property
	def uomo(self):
		return self._uomo

	@uomo.setter
	def uomo(self, new_value):
		self._uomo = new_value

	@uomo.deleter
	def uomo(self):
		del self._uomo


	#setter soglia di segmentazione
	@property
	def thresh(self):
		return self._thresh
	
	@thresh.setter
	def thresh(self, new_value):
		if new_value == "default":
			self._thresh = 20
		else:
			self._thresh = float(new_value)
		

	def isperson(self, frame):
	   # detect people in the image
		# returns the bounding boxes for the detected objects
	


		frameDelta = cv2.absdiff(self._firstFrame, frame)
		#era 25
		thresh = cv2.threshold(frameDelta, self._thresh, 255, cv2.THRESH_BINARY)[1]
		# dilate the thresholded image to fill in holes, then find contours
		# on thresholded image
		thresh = cv2.dilate(thresh, None, iterations=2)
		
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		cont = 0 #variabile per il controllo della lunghezza dei contorni
		# loop over the contours
		for c in cnts:
			# if the contour is too small, ignore it
			
			if cv2.contourArea(c) < 9000:
				continue
			# compute the bounding box for the contour, draw it on the frame,
			# and update the text
			cont += 1
			(x, y, w, h) = cv2.boundingRect(c)
			cv2.rectangle(self._current, (x, y), (x + w, y + h), (0, 0, 0), 2)
			#cv2.imwrite('Test.jpg', thresh)
		if cont > 0:
			self._uomo = self._current
			self.detect = True

		
			



	def recording(self):
		time.sleep(0.1)
		
		for frame in self.cam.capture_continuous(self.stream, format = "bgr",  use_video_port=True):
#format="bgr",

			image = frame.array
			
			#devo pensare che ok a giocare sulla soglia ma devo anche pensare a cambiare il contrasto
			image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			print(image.shape)
			#image = self.__adj_img(image, self._alfa, self._beta)

			#image = self.__adj_img(image, self._alfa, self._beta)
			
			self._current = image.copy()
			#image = cv2.GaussianBlur(image, (21, 21), 0)
			if self._firstFrame is None:
				pass
			else:
				self.isperson(image)
			#cv2.imwrite('Test_gray.jpg', grayImage) 
			self._firstFrame = image.copy()
			key = cv2.waitKey(1) & 0xFF
			# clear the stream in preparation for the next frame
			self.stream.truncate(0)
			# if the `q` key was pressed, break from the loop
			if self.isrecord == False:
				break
			

	def stop(self):
		self.isrecord = False
		self._firstFrame = None
		#self.cam.stop_recording()

	def start(self):
		self.isrecord = True
		#self.cam.start_recording(self.stream, format='rgb')
	#mettu l'istogramma delle luminosità
	def pic(self):
		img = PiRGBArray(self.cam,  size=(640, 480))

		self.cam.capture(img, format= "bgr")
		image = img.array
		image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		#image = self.__adj_img(image, self._alfa, self._beta)
		return image

	#alfa è contrasto beta è luminosità -> sono in %
	def __adj_img(self, img, alfa = 100, beta = 0):
		print(alfa)
		print(beta)
		alfa = alfa/100
		print(alfa)
		beta = beta * 127 / 100
		print(beta)
		beta = int(beta) * np.ones(img.shape)

		img = int(alfa) * img + beta
		return img








