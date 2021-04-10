from telegram import telegram, file
import threading
import os, sys, json, time
import cv2
from spycam import spycam

def check(tg, camera, chat):
	time.sleep(1)
	i=0
	while camera.isrecord == True:
		
		if camera.detect == True:
			i = i +1
			print("c'è uno! "  + str(i))

			camera.detect = False
			img = camera.uomo
			camera.uomo = None
			print(camera.detect)
			try:
				cv2.imwrite('tmp.jpg', img)
				for user in chat:
					tg.send_pic('tmp.jpg', user)
					tg.send_update("C'è qualcuno", user)
				os.remove("tmp.jpg")

			except:
				pass
		time.sleep(1)


if __name__ == '__main__':
	#configurazione bot e introduzione chat_id

	with open("config.json", "r") as f:
		conf = json.load(f)
		chat = []
		chat.append(conf["user1"])
		chat.append(conf["user2"])
		master = conf["master"]
		cond = conf["comandi"]
		parz = conf["parziali"]
		token = conf["token"]
		tg = telegram(token)

	print(chat)
	chat[:] = (value for value in chat if value != "")
	print(len(chat))

	for i in chat:

		tg.send_update("Mi sono appena avviato. Ti contatterò qui!", i)
		#nuovo utente
	c = ""
	if len(chat) == 0:

		while "Avvio" not in c:
			c, ch = tg.waiting(cond, parz)
		conf["user1"] = ch
		with open("config.json", "w") as f:
			json.dump(conf, f)
		tg.send_update("Ok ti contatterò qui!", ch)
	with open("cam_params.json", "r") as f:
		params = json.load(f)
	#creo una lista con i parametri
	print(params)
	lista = [ x["current"] for x in params.values() ]
	camera = spycam(*lista)
	print(camera)
	print(params)
	del lista
	bw = True #utile?
	full = False




	while c != "Spegni":
		#loop principale
		#devo sistemare i permessi delle chat assolutamente
			c, ch = tg.waiting(cond, parz)
			print(c)
			if "Avvio" in c:
				if full == False:
					conf["user2"] = ch
					with open("config.json", "w") as f:
						json.dump(conf, f)
					tg.send_update("Ok ti contatterò qui!", ch)
					full = True
					chat.append(ch)
			if c == "file" and ch == master:
				file = tg.obj
				print(file.name)
				#fai controlli sul formato
				for user in chat:
					tg.send_update("C'è un nuovo aggiornamento, il dispositivo verrà riavviato", user)
				if file.format == "text/x-python":
					tg.get_file(file.id, file.name)
					tg.send_update("Ok aggiornamento riuscito", master)
					#routine di reboot
					from subprocess import call
					call("sudo reboot", shell=True)
				else:
					tg.send_update("Formato sbagliato!", chat)


			if ch in chat:
				if c == "Stop":
					camera.stop()
					for user in chat:
						tg.send_update("Ok, smetto di controllare la casa!", user)
				elif c == "Start":
					if camera.isrecord== False:
						camera.start()

						#qua sono incastrato con telegram
						t0 = threading.Thread(target = check, args = [tg, camera, chat])
						t0.start()
						t = threading.Thread(target=camera.recording)
						t.start()
						for user in chat:
							tg.send_update("Ok, inizio a controllare la casa!", user)
						
				elif c == "Foto":
					img = camera.pic()
					cv2.imwrite('tmp.jpg', img)
					tg.send_pic('tmp.jpg', ch)
					tg.send_update("Ecco la foto", ch)
					os.remove("tmp.jpg")
				elif c == "Dimenticami":
					for user in conf.values():
						if user == ch:
							user = ""
					with open("config.json", "w") as f:
						json.dump(conf, f)
					for i in len(chat):
						if chat(i) == ch:
							chat.pop[i]
					full = False
					if len(chat) == 0:
						c = "Riavvia"
				elif c == "Riavvia":
					camera.stop()
					for user in chat:
						tg.send_update("Sto riavviando, a presto!", user)
					time.sleep(1)
					from subprocess import call
					call("sudo reboot", shell=True)
				elif "Soglia" in c:
					l = c.split(" ")
					try:
						camera.thresh = l[1]
						params["threshold"]["current"] = int(l[1])
						with open("cam_params.json", "w") as f:
							json.dump(params, f)
						tg.send_update("Ok ho impostato la soglia a " + l[1], ch)
					except:
						tg.send_update("Imposta la soglia di sensibilità ai movimenti di default è  " + str(params["threshold"]["default"]), ch)

				elif "Contrasto" in c:
					print(c)
					l = c.split(" ")
					try:
						#sbagliato!! proteggi cam!!
						camera.cam.contrast = int(l[1])
						params["contrast"]["current"] = int(l[1])
						with open("cam_params.json", "w") as f:
							json.dump(params, f)
						tg.send_update("Ok ho impostato il contrasto a " + l[1], ch)
					except:
						tg.send_update("Specifica il valore, in percentuale, da -100 a 100. Di default è " + str(params["contrast"]["default"]), ch)
						
				elif "Luminosit" in c:
					print(c)
					l = c.split(" ")
					try:
						camera.cam.brightness = int(l[1])
						params["brightness"]["current"] = int(l[1])
						with open("cam_params.json", "w") as f:
							json.dump(params, f)
						tg.send_update("Ok ho impostato la luminosità a " + l[1], ch)
					except:
						
						tg.send_update("Specifica il valore, in percentuale, da 0 in poi. Di default è " + str(params["brightness"]["default"]), ch)




	camera.stop()
	for user in chat:
		tg.send_update("Sto spegnendo tutto, ciao!", user)
	time.sleep(1)
	from subprocess import call
	call("sudo poweroff", shell=True)