#import speech_recognition as sr
import pyttsx
import pygame
import sys
import sqlite3
import os
import wiiuse.pygame_wiimote as pygame_wiimote



#Center the screen for fullscreen effect
os.environ['SDL_VIDEO_CENTERED'] = '1'

class ActivityDatabase:
	def __init__(self):
		self.db = self.init_database()
		self.cursor = self.db.cursor()

	#Create the database table if necessary
	def init_database(self):
		try:
			days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
			db = sqlite3.connect('activelist.db')
			cursor = db.cursor()

			#create two tables, one for day and one for the activities
			cursor.execute('''CREATE TABLE IF NOT EXISTS
							  activities_t(day TEXT, activity_num INTEGER, subject TEXT, activity TEXT) ''')

			for i in range(7):
				for j in range(20):
					cursor.execute('''INSERT INTO activities_t(day, activity_num, subject, activity)
					Values(?,?,?,?)''', (days[i], j, "Create new activity", "Enter your activity here") )

			db.commit()

		except Exception as e:
			db.rollback()
			raise e

		return db

	def updateActivity(self, activity, day, index):
		self.cursor.execute('''UPDATE activities_t SET activity = ? WHERE day = ? and activity_num = ? ''', (activity, day, index))
		self.db.commit()

	def updateSubject(self, subject, day, index):
		self.cursor.execute('''UPDATE activities_t SET subject = ? WHERE day = ? and activity_num = ? ''', (subject, day, index))
		self.db.commit()

	def retrieveActivity(self, day, index):
		self.cursor.execute('''SELECT activity FROM activities_t WHERE day = ? and activity_num = ? ''', (day, index))
		for row in self.cursor:
			return row[0]

	def retrieveSubject(self, day, index):
		self.cursor.execute('''SELECT subject FROM activities_t WHERE day = ? and activity_num = ? ''', (day, index))
		for row in self.cursor:
			return row[0]

#Audio driver to record audio from the user and translate it into text for activities
# class AudioRecorder:
# 	def __init__(self):
# 		self.recorder = sr.Recognizer()
# 		#self.recorder.pause_threshold = 0.5
# 		self.mic = sr.Microphone(1)

# 	def recordAudio(self):
# 		print "Starting..."
# 		with self.mic as source:
# 			audio = self.recorder.listen(source)
# 		try:
# 			return self.recorder.recognize(audio)
# 		except LookupError:
#  			return "Failure, please try again!"	

#Voice driver object to control the text to speech for the user. (AUDITORY DESIGN)
class VoiceDriver:
	def __init__(self, activities):
		self.engine = pyttsx.init()
		self.engine.setProperty('rate', 120)
		self.activities = activities
		self.active = False

	def speak(self, input):
		self.active = True
		self.engine.say(input)
		self.engine.runAndWait()

	def isBusy(self):
		return self.busy

	def stop(self):
		self.engine.stop()
		self.engine.endLoop()

#Activity object to control our todo list, contains the days and activities for those days. 
class ActivityList:
	def __init__(self):
		self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		self.database = ActivityDatabase()
		self.dayIndex = 0
		self.activityIndex = 0
		self.dayChosen = False
		self.activityChosen = False

	#Set the current day's activity
	def setActivity(self, activity):
		self.database.updateActivity(activity, self.days[self.dayIndex], self.activityIndex)

	#Set the current day's subject
	def setSubject(self, subject):
		self.database.updateSubject(subject, self.days[self.dayIndex], self.activityIndex)


class ActivityScreen:
	def __init__(self, activities):
		self.screenInfo = pygame.display.Info()
		self.activities = activities
		self.width = self.screenInfo.current_w
		self.height = self.screenInfo.current_h
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.background = pygame.Surface(self.screen.get_size())
		self.font = pygame.font.Font(None, 40)
		self.day = activities.days[self.activities.dayIndex]
		self.activityNum = activities.activityIndex
		self.subjectSelected = True
		self.instructionText = self.font.render("Press A to record", 1, (255,255,255))
		self.initBackground()
		self.initDisplay()
		self.updateSelection()

	#Initialize the black background and full screen
	def initBackground(self):
		self.background = self.background.convert()
		self.background.fill((0, 0, 0))
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

	#Initialize the display for the day, activity, and subject
	def initDisplay(self):
		positionX = self.width / 2
		positionY = self.height / 5

		#Set the text for the three fields title, subject, and activity
		titleText = self.font.render(self.day + ", " + "Activity " + str(self.activityNum+1), 1, (255,255,255))
		subjectText = self.font.render(self.activities.database.retrieveSubject(self.day, self.activityNum), 1, (255,255,255))
		activityText = self.font.render(self.activities.database.retrieveActivity(self.day, self.activityNum), 1, (255,255,255))

		#Position all text objects
		positionX = positionX-titleText.get_rect().width/2
		self.background.blit(titleText, (positionX, positionY))

		#This is activity hasn't been set yet
		if self.activities.database.retrieveActivity(self.day, self.activityNum) == "Enter your activity here":
			self.background.blit(self.instructionText, (positionX, self.height - self.instructionText.get_rect().height*2))

		#Update the screen with the new background and draw rectangles around the subject and activity fields
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

	#Update the currently selected field, subject or the activity
	def updateSelection(self):
		subjectText = self.font.render(self.activities.database.retrieveSubject(self.day, self.activityNum), 1, (255,255,255))
		activityText = self.font.render(self.activities.database.retrieveActivity(self.day, self.activityNum), 1, (255,255,255))

		positionX = self.width / 2 - self.width / 4
		positionY = self.height / 5 + 50

		#If the subject is selected, highlight it as the current selection for the user to know which field is active
		if self.subjectSelected:
			subjectText = self.font.render(self.activities.database.retrieveSubject(self.day, self.activityNum), 1, (0, 0, 0))
			activityText = self.font.render(self.activities.database.retrieveActivity(self.day, self.activityNum), 1, (255, 255, 255))
			self.background.fill(pygame.Color("black"), (positionX-10, positionY+50, self.width / 2, self.height / 3))
			self.background.fill(pygame.Color("yellow"), (positionX-10, positionY-10, self.width/2, 50))


		#Otherwise, highlight the activity section as the current selection for the user
		else:
			activityText = self.font.render(self.activities.database.retrieveActivity(self.day, self.activityNum), 1, (0, 0, 0))
			subjectText = self.font.render(self.activities.database.retrieveSubject(self.day, self.activityNum), 1, (255, 255, 255))
			self.background.fill(pygame.Color("yellow"), (positionX-10, positionY+50, self.width / 2, self.height / 3))
			self.background.fill(pygame.Color("black"), (positionX-10, positionY-10, self.width/2, 50))
		
		self.background.blit(subjectText, (positionX, positionY))
		self.background.blit(activityText, (positionX, positionY+60))
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

		pygame.draw.rect(self.screen, pygame.Color("white"), (positionX-10, positionY-10, self.width / 2, 50), 2)
		pygame.draw.rect(self.screen, pygame.Color("white"), (positionX-10, positionY+50, self.width / 2, self.height / 3), 2)
		pygame.display.update()
	

#Screen object that controls the visual updates. (VISUAL DESIGN)
class MainScreen:
	def __init__(self, activities):
		self.screenInfo = pygame.display.Info()
		self.activities = activities
		self.width = self.screenInfo.current_w
		self.height = self.screenInfo.current_h
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.background = pygame.Surface(self.screen.get_size())
		self.font = pygame.font.Font(None, 40)
		self.dayText = ""
		self.activityText = ""
		self.currentX = 0
		self.initBackground()
		self.initDays()
		self.initActivities()
		self.drawLines()

	#Initialize the black background and full screen
	def initBackground(self):
		self.background = self.background.convert()
		self.background.fill((0, 0, 0))
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

	#Initialize the todo list by drawing each day to the top of the screen. This is portable to many screen sizes
	def initDays(self):
		rect_width = self.width / 7
		rect_x = 0
		rect_y = 0

		for i in range(7):
			self.background.fill(pygame.Color("white"), (rect_x, rect_y, rect_x + rect_width, 100))
			self.dayText = self.font.render(self.activities.days[i], 1, (0,0,0))
			self.background.blit(self.dayText, (rect_x+rect_width/2-self.dayText.get_rect().width/2, rect_y+35))
			rect_x += rect_width

		self.dayText = self.font.render(self.activities.days[0], 1, (0,0,0))
		self.background.fill(pygame.Color("yellow"), (self.currentX, 0, rect_width, 100))
		self.background.blit(self.dayText, (rect_width - (3*self.dayText.get_rect().width/2)+10, rect_y+35))
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

	#Initialize empty activities for your todo list. draws the title and the empty activities with 20 in total. 
	def initActivities(self):
		rect_width = self.width / 2
		rect_height = ((self.height / 3)/5)
		currentHeight = rect_height + self.height / 3
		currentWidth = 0
		currentX = 0

		#Add the activity title
		positionX = self.width / 2
		positionY = self.height / 4
		self.activityText = self.font.render("Activities", 1, (255,255,255))
		self.background.blit(self.activityText, (positionX-self.activityText.get_rect().width/2, positionY))
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

		#Add the default text for the activities
		for i in range(20):
			currentActivity = self.font.render(self.activities.database.retrieveSubject(self.activities.days[self.activities.dayIndex], i), 1, (255,255,255))
			currentWidth = self.width/4-(currentActivity.get_rect().width/2)

			#First row drawn, start the second row
			if i == 10:
				currentHeight = rect_height + self.height / 3
			if i > 9:
				currentWidth = self.width/2 + self.width/4 - currentActivity.get_rect().width / 2
				currentX = self.width / 2

			self.background.fill(pygame.Color("black"), (currentX, currentHeight, rect_width, rect_height))
			self.background.blit(currentActivity, (currentWidth, currentHeight-currentActivity.get_rect().height/2-rect_height/2))
			currentHeight += rect_height

		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

	#When user hits the left or right arrows, update the current day selected with yellow box.
	def updateDay(self):
		if self.activities.dayIndex > 6:
			self.activities.dayIndex = 0
		if self.activities.dayIndex < 0:
			self.activities.dayIndex = 6
		
		rect_width = self.width / 7

		for i in range(7):
			if i == self.activities.dayIndex:
				break
			else:
				self.currentX += rect_width

		self.drawLines()
		self.dayText = self.font.render(self.activities.days[self.activities.dayIndex], 1, (0,0,0))
		self.background.fill(pygame.Color("yellow"), (self.currentX, 0, rect_width, 100))
		self.background.blit(self.dayText, (self.currentX+rect_width/2-self.dayText.get_rect().width/2, 35))
		self.screen.blit(self.background, (0, 0))
		self.drawLines()
		self.currentX = 0
		pygame.display.flip()

	#When the user hits the left or right arrows, change the previous selected day back to unselected with white box.
	def clearDay(self):
		rect_width = self.width / 7

		for i in range(7):
			if i == self.activities.dayIndex:
				break
			else:
				self.currentX += rect_width

		self.drawLines()
		self.dayText = self.font.render(self.activities.days[self.activities.dayIndex], 1, (0,0,0))
		self.background.fill(pygame.Color("white"), (self.currentX, 0, rect_width, 100))
		self.background.blit(self.dayText, (self.currentX+rect_width/2-self.dayText.get_rect().width/2, 35))
		self.screen.blit(self.background, (0, 0))
		self.drawLines()
		self.currentX = 0
		pygame.display.flip()

	#Once the user has chosen a day, we can update the visual for currently selected activity to be highlighted with yellow
	def updateActivity(self):
		if self.activities.activityIndex > 19:
			self.activities.activityIndex = 0
		if self.activities.activityIndex < 0:
			self.activities.activityIndex = 19

		rect_width = self.width / 2
		rect_height = ((self.height / 3)/5) 
		currentHeight = self.height / 3
		currentX = 0

		for i in range(20):

			#First row passed, change height and width
			if i == 10:
				currentHeight = self.height / 3
			if i > 9:
				currentX = self.width / 2

			if i == self.activities.activityIndex:
				break
			else:	
				currentHeight += rect_height

		self.activityText = self.font.render(self.activities.database.retrieveSubject(self.activities.days[self.activities.dayIndex],self.activities.activityIndex), 1, (0,0,0))
		self.background.fill(pygame.Color("yellow"), (currentX, currentHeight, rect_width, rect_height))
		self.background.blit(self.activityText, (currentX + self.width/4 - self.activityText.get_rect().width/2, currentHeight+rect_height/4))
		self.screen.blit(self.background, (0, 0))
		self.drawLines()
		pygame.display.flip()

	#Upon using the D-PAD to choose a new activity the previous activity selected is reset to unselected
	def clearActivity(self):
		rect_width = self.width / 2
		rect_height = ((self.height / 3)/5) 
		currentHeight = self.height / 3
		currentX = 0

		for i in range(20):

			#First row passed, change height and width
			if i == 10:
				currentHeight = self.height / 3
			if i > 9:
				currentX = self.width / 2

			if i == self.activities.activityIndex:
				break
			else:	
				currentHeight += rect_height

		self.activityText = self.font.render(self.activities.database.retrieveSubject(self.activities.days[self.activities.dayIndex],self.activities.activityIndex), 1, (255,255,255))
		self.background.fill(pygame.Color("black"), (currentX, currentHeight, rect_width, rect_height))
		self.background.blit(self.activityText, (currentX + self.width/4 - self.activityText.get_rect().width/2, currentHeight+rect_height/4))
		self.screen.blit(self.background, (0, 0))
		self.drawLines()
		pygame.display.flip()

	#Draws the lines outlining the 20 activities
	def drawLines(self):
		lineHeight = ((self.height / 3)/5)
		currentHeight = lineHeight + self.height / 3
		pygame.draw.line(self.screen, pygame.Color("white"), (0, self.height / 3), (self.width, self.height / 3), 2)
		pygame.draw.line(self.screen, pygame.Color("white"), (self.width/2, self.height / 3), (self.width/2, self.height), 2)
		pygame.draw.line(self.screen, pygame.Color("white"), (self.width-2, self.height / 3), (self.width-2, self.height), 2)

		for i in range(10):
			pygame.draw.line(self.screen, pygame.Color("white"), (0, currentHeight), (self.width, currentHeight), 2)
			currentHeight += lineHeight

		pygame.display.flip()

def main():
	#Initialize pygame
	pygame.init()
	running = True
	# initialze the wiimotes
	if os.name != 'nt': print 'press 1&2'
	pygame_wiimote.init(1, 5) # look for 1, wait 5 seconds
	n = pygame_wiimote.get_count() # how many did we get?

	if n == 0:
		print 'no wiimotes found'
		sys.exit(1)

	wm = pygame_wiimote.Wiimote(0) # access the wiimote object

	#Create objects
	Activities = ActivityList()
	screen = MainScreen(Activities)
#	VoiceRecord = AudioRecorder()
	VoiceOutput = VoiceDriver(Activities)

	#Infinite loop to run the program
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				print 'quiting'
				running = False
				break
			elif event.type in [ pygame_wiimote.WIIMOTE_BUTTON_PRESS]:
				print event.button, 'pressed on', event.id
				#print type(event.button)
				if event.button=='Right' and not Activities.dayChosen:
					if Activities.activityChosen == False:
						screen.clearDay()
						Activities.dayIndex += 1
						screen.updateDay()
				if event.button=='Left' and not Activities.dayChosen:
					if Activities.activityChosen == False:
						screen.clearDay()
						Activities.dayIndex -= 1
						screen.updateDay()
				if event.button=='Up' and Activities.dayChosen:
					if Activities.activityChosen == False:
						screen.clearActivity()
						Activities.activityIndex -= 1
						screen.updateActivity()
					else:
						if screen.subjectSelected:
							screen.subjectSelected = False
							screen.updateSelection()
						else:
							screen.subjectSelected = True
							screen.updateSelection()

				if event.button=='Down' and  Activities.dayChosen:
					if Activities.activityChosen == False:
						screen.clearActivity()
						Activities.activityIndex += 1
						screen.updateActivity()
					else:
						if screen.subjectSelected:
							screen.subjectSelected = False
							screen.updateSelection()
						else:
							screen.subjectSelected = True
							screen.updateSelection()
				if event.button =='A':
					if not Activities.dayChosen:
						Activities.dayChosen = True
						screen.initActivities()
						screen.updateActivity()
					else:
						if Activities.activityChosen == False:
							Activities.activityChosen = True
							screen = ActivityScreen(Activities)
						else:
							if screen.subjectSelected:
								pass
							#	newSubject = VoiceRecord.recordAudio()
							#	Activities.setSubject(newSubject)
							#	screen.updateSelection()
							else:
								pass
							#	newActivity = VoiceRecord.recordAudio()
							#	Activities.setActivity(newActivity)
							#	screen.updateSelection()
				if event.button =='B':
					if Activities.activityChosen == False:
						screen.clearActivity()
						Activities.activityIndex = 0
						Activities.dayChosen = False
					else:
						screen = MainScreen(Activities)
	 					Activities.activityIndex = 0
	 					Activities.dayIndex = 0
						Activities.activityChosen = False
						Activities.dayChosen = False

			elif event.type in [ pygame_wiimote.WIIMOTE_BUTTON_RELEASE,pygame_wiimote.NUNCHUK_BUTTON_RELEASE ]:
				print event.button, 'released on', event.id

		'''event = pygame.event.poll()
		if event.type == pygame.QUIT:
			running = 0
        if event.type in [ pygame_wiimote.WIIMOTE_BUTTON_PRESS,pygame_wiimote.NUNCHUK_BUTTON_PRESS ]:
        	print event.button, 'pressed on', event.id

		if event.type == pygame.KEYDOWN:

			#Press escape to quit, change to HOME button on wiimote
			if event.key == pygame.K_ESCAPE:
				running = 0

			#Navigate the days with the left/right arrows keys, change to D-PAD left/right buttons on wiimote
			if event.key == pygame.K_RIGHT and not Activities.dayChosen:
				if Activities.activityChosen == False:
					screen.clearDay()
					Activities.dayIndex += 1
					screen.updateDay()

			if event.key == pygame.K_LEFT and not Activities.dayChosen:
				if Activities.activityChosen == False:
					screen.clearDay()
					Activities.dayIndex -= 1
					screen.updateDay()

			#Select the day with the enter key, change to A button on the wiimote
			if event.key == pygame.K_RETURN:
				if not Activities.dayChosen:
					Activities.dayChosen = True
					screen.initActivities()
					screen.updateActivity()
				else:
					if Activities.activityChosen == False:
						Activities.activityChosen = True
						screen = ActivityScreen(Activities)
					else:
						if screen.subjectSelected:
							pass
						#	newSubject = VoiceRecord.recordAudio()
						#	Activities.setSubject(newSubject)
						#	screen.updateSelection()
						else:
							pass
						#	newActivity = VoiceRecord.recordAudio()
						#	Activities.setActivity(newActivity)
						#	screen.updateSelection()

			#Navigate the day's activities with up/down arrow keys, change to D-PAD up/down buttons on wiimote
			if event.key == pygame.K_UP and Activities.dayChosen:
				if Activities.activityChosen == False:
					screen.clearActivity()
					Activities.activityIndex -= 1
					screen.updateActivity()
				else:
					if screen.subjectSelected:
						screen.subjectSelected = False
						screen.updateSelection()
					else:
						screen.subjectSelected = True
						screen.updateSelection()

			if event.key == pygame.K_DOWN and Activities.dayChosen:
				if Activities.activityChosen == False:
					screen.clearActivity()
					Activities.activityIndex += 1
					screen.updateActivity()
				else:
					if screen.subjectSelected:
						screen.subjectSelected = False
						screen.updateSelection()
					else:
						screen.subjectSelected = True
						screen.updateSelection()

			#Unselect activity and choose a new day
			if event.key == pygame.K_BACKSPACE and Activities.dayChosen:
				if Activities.activityChosen == False:
					screen.clearActivity()
					Activities.activityIndex = 0
					Activities.dayChosen = False
				else:
					screen = MainScreen(Activities)
 					Activities.activityIndex = 0
 					Activities.dayIndex = 0
					Activities.activityChosen = False
					Activities.dayChosen = False


		if event.type == pygame.KEYUP:
			if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
				pass'''
	pygame_wiimote.quit()
	pygame.quit()
			
main()