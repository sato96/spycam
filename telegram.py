import telepot
import time



class telegram(object):
	"""telegram notification"""
	def __init__(self, token):
		self.TOKEN = token #identifica il nostro bot
		self.bot = telepot.Bot(self.TOKEN) #inizializzo telepot
		self._obj = None
		resp = self.bot.getUpdates() #controllo l'ultimo messaggio
		if len(resp) == 0:
			self.ini = 0 #se c'è un messaggio dal bot o se non ci sono messaggi
		else:
			self.ini = int(resp[len(resp)-1]['update_id']) #altrimento prendo l'ultimo offset disponibile
		
	@property
	def obj(self):
		return self._obj
   
	def send_update(self, msg, chat):
		#mando il messaggio e controllo se il messaggio è una stringa
		self.bot.sendMessage(chat,str(msg))



	def waiting(self, cond, parz = [], chat = ""): #loop per l'attesa dei messaggi
		#condizione di comando arrivato
		is_condition = None
		chat_id = None
		if chat == "":
			while is_condition == None:
				try:
					is_condition, chat_id = self.msg(cond, parz)
				except :
					is_condition = "Errore " 
					chat_id=None
				time.sleep(0.5)

		else:
			while is_condition == None and chat_id != chat:
				try:
					is_condition, chat_id = self.msg(cond, parz)
				except :
					is_condition = "Errore " 
					chat_id=None
				time.sleep(0.5)
		return is_condition, chat_id

		


	def msg(self, condition, parziali): #controllo del messaggio
	#controlla che condition sia una lista di stringhe
		if self.ini == 0: #se non ci sono messaggi inviati non serve aumentare l'offset
			response = self.bot.getUpdates()
			if response != []:
				#qua serve se non ci sono messaggi prima
				#serve nel caso in cui ho self.ini=0 ma nessuno ha mandato un messaggio con un comando utile
				#infatti così  aggiorno l'offset al primo messaggio sennò resterei bloccato
				self.ini = response[len(response)-1]['update_id']
			
		else:
			response = self.bot.getUpdates(offset = self.ini + 1)#sennò mi prendo il successivo
			if response != []:
				self.ini = self.ini + 1

		if len(response) == 0: #in ogni caso considero il caso in cui non ci sono i messaggi. 
		#Da getUpdates ho una lista di dizionari(ogni dizionario è un messaggio con i suoi parametri)
			is_condition = None
			chat_id = ''

		else: #mi prendo l'ultimo dizionario e vedo se il testo di un comando c'è
			print(response[len(response) - 1])
			try:
				chat_id = response[len(response)- 1]['message']['chat']['id']
				print(response[len(response)- 1]['message']['document'])
				is_condition = "file"
				self._obj=file(response[len(response)- 1])
			except:
				if response[len(response) - 1]['message']['text'] in condition:
					chat_id = response[len(response)- 1]['message']['chat']['id']
					is_condition = response[len(response) - 1]['message']['text']

				else:
					for stringa in parziali:
						if stringa in response[len(response) - 1]['message']['text']:
							is_condition = response[len(response) - 1]['message']['text']
							chat_id = response[len(response)- 1]['message']['chat']['id']
							break
						is_condition = None
						chat_id = ''


			
		return is_condition, chat_id


	def send_pic(self, path, chat_id):
		self.bot.sendPhoto(chat_id, open(path, 'rb'))

	def get_file(self, file_id, path):
		self.bot.download_file(file_id, path)




#classe che astre il file, in realtà è semplicemente un set di informazioni
#prende un json e lo mette come oggetto. Il fatto è così è più facile da capire

class file(object):
	def __init__(self, response = None):
		try:
			self.chat_id = response['message']['chat']['id']
			self.name = response['message']['document']['file_name']
			self.format = response['message']['document']['mime_type']
			self.id = response['message']['document']['file_id']
		except:
			print("Response non valido")
		