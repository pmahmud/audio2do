import pygame
import sys
import sqlite3
import os

#Initialize pygame
pygame.init()

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

			cursor.execute('''SELECT * FROM activities_t ''');
			size = len(cursor.fetchall())

			if size == 0:
				for i in range(7):
					for j in range(14):
						cursor.execute('''INSERT INTO activities_t(day, activity_num, subject, activity)
						Values(?,?,?,?)''', (days[i], j, "Create new activity", "Enter your activity here") )

			db.commit()

		except Exception as e:
			db.rollback()
			raise e

		return db

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

#Activity object to control our todo list, contains the days and activities for those days. 
class ActivityList:
	def __init__(self):
		self.days 	 	    = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		self.database 	    = ActivityDatabase()
		self.dayIndex       = 0
		self.activityIndex  = 0
		self.dayChosen      = False
		self.recording      = False
		self.activityChosen = False

	#Set the current day's activity
	def setActivity(self, activity):
		self.database.updateActivity(activity, self.days[self.dayIndex], self.activityIndex)

	def getActivity(self):
		return self.database.retrieveSubject(self.days[self.dayIndex], self.activityIndex)

	def isEmpty(self):
		if self.getActivity() == "Create new activity":
			return True
		return False

	def isEmptyLast(self):
		if self.database.retrieveSubject(self.days[self.dayIndex], 13) == "Create new activity":
			return True
		return False

	#Set the current day's subject
	def setSubject(self, subject):
		self.database.updateSubject(subject, self.days[self.dayIndex], self.activityIndex)

	def adjustActivities(self):
		adjustRange = 14 - self.activityIndex
		currentIndex = self.activityIndex
		nextSubject = self.database.retrieveSubject(self.days[self.dayIndex], currentIndex + 1)

		for i in range(adjustRange):
			self.database.updateSubject(nextSubject, self.days[self.dayIndex], currentIndex)
			currentIndex += 1
			nextSubject = self.database.retrieveSubject(self.days[self.dayIndex], currentIndex + 1)
			if nextSubject == "Create new activity" or i == (adjustRange - 1):
				break
		self.database.updateSubject("Create new activity", self.days[self.dayIndex], currentIndex)

	def getDay(self):
		return self.days[self.dayIndex]

	def getDayIndex(self):
		return self.dayIndex

	def getActivityIndex(self):
		return self.activityIndex

#Screen object that controls the visual updates. (VISUAL DESIGN)
class MainScreen:
	def __init__(self, activities):
		self.dpad 		= pygame.image.load("buttons/next_prev.png")
		self.homeBtn 	= pygame.image.load("buttons/home.png")
		self.selectBtn 	= pygame.image.load("buttons/a.png")
		self.backBtn	= pygame.image.load("buttons/b.png")
		self.removeBtn  = pygame.image.load("buttons/remove.png")
		self.addBtn 	= pygame.image.load("buttons/add.png")
		self.screenInfo = pygame.display.Info()
		self.activities = activities
		self.width 		= self.screenInfo.current_w
		self.height 	= self.screenInfo.current_h
		self.screen 	= pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
		self.background = pygame.Surface(self.screen.get_size())
		self.font 		= pygame.font.Font(None, 40)
		self.dayText	= ""
		self.activityText = ""
		self.currentX 	= 0
		self.initBackground()
		self.initDays()
		self.initActivities()
		self.drawLines()

	#Initialize the black background and full screen
	def initBackground(self):
		self.background = self.background.convert()
		self.background.fill((0, 0, 0))
		self.screen.blit(self.background, (0, 0))
		pygame.draw.rect(self.screen, (237, 243, 251), (100, 100, 130, 170), 0)
		pygame.display.flip()

	#Draw the instructions based on what the user needs to do
	def drawDayInstructions(self):
		dpadX 	= 50 - (self.dpad.get_rect().width/2)
		dpadY 	= (self.height - self.height / 8)+self.dpad.get_rect().height / 4
		homeX 	= self.width - 200
		selectX = dpadX + 250
		
		self.screen.blit(self.dpad, (dpadX, dpadY))
		self.screen.blit(self.homeBtn, (homeX, dpadY))
		self.screen.blit(self.selectBtn, (selectX, dpadY))

		selectText = self.font.render("- Select", 1, (0, 0, 0))
		moveText   = self.font.render("- Navigate", 1, (0,0,0))
		exitText   = self.font.render("- Exit", 1, (0,0,0))
		self.screen.blit(selectText, (selectX+self.selectBtn.get_rect().width+5, dpadY+self.dpad.get_rect().height / 4));
		self.screen.blit(exitText, (homeX+self.homeBtn.get_rect().width+5, dpadY+self.dpad.get_rect().height / 4));
		self.screen.blit(moveText, (dpadX+self.dpad.get_rect().width+5, dpadY+self.dpad.get_rect().height / 4));

	#Draw the instructions based on what the user needs to do
	def drawActivityInstructions(self):
		dpadX 	= 50 - (self.dpad.get_rect().width/2)
		dpadY 	= (self.height - self.height / 8)+self.dpad.get_rect().height / 4
		homeX 	= self.width - 200
		selectX = dpadX + 250
		backX   = selectX + 200
		addX	= backX + 150
		removeX = addX + 150

		self.screen.blit(self.dpad, (dpadX, dpadY))
		self.screen.blit(self.homeBtn, (homeX, dpadY))
		self.screen.blit(self.selectBtn, (selectX, dpadY))
		self.screen.blit(self.backBtn, (backX, dpadY))
		self.screen.blit(self.addBtn, (addX, dpadY))
		self.screen.blit(self.removeBtn, (removeX, dpadY))

		selectText = self.font.render("- Record", 1, (0, 0, 0))
		moveText   = self.font.render("- Navigate", 1, (0,0,0))
		exitText   = self.font.render("- Exit", 1, (0,0,0))
		backText   = self.font.render("- Back", 1,(0,0,0))
		addText    = self.font.render("- Add", 1, (0,0,0))
		removeText = self.font.render("- Remove", 1, (0,0,0))


		self.screen.blit(backText, (backX+self.backBtn.get_rect().width, dpadY+self.dpad.get_rect().height / 4));
		self.screen.blit(addText, (addX+self.addBtn.get_rect().width-5, dpadY+self.dpad.get_rect().height / 4));
		self.screen.blit(removeText, (removeX+self.removeBtn.get_rect().width-5, dpadY+self.dpad.get_rect().height / 4));
		self.screen.blit(selectText, (selectX+self.selectBtn.get_rect().width+5, dpadY+self.dpad.get_rect().height / 4));
		self.screen.blit(exitText, (homeX+self.homeBtn.get_rect().width+5, dpadY+self.dpad.get_rect().height / 4));
		self.screen.blit(moveText, (dpadX+self.dpad.get_rect().width+5, dpadY+self.dpad.get_rect().height / 4));

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
		rect_height = ((self.height / 3)/4)
		currentHeight = self.height / 5
		currentX = 0

		#Add the activity title
		positionX = self.width / 2
		positionY = self.height / 4

		#Add the default text for the activities
		for i in range(14):
			currentActivity = self.font.render(self.activities.database.retrieveSubject(self.activities.days[self.activities.dayIndex], i), 1, (255,255,255))

			#First row drawn, start the second row
			if i == 7:
				currentHeight = self.height / 5
			if i > 6:
				currentX = self.width / 2

			self.background.fill(pygame.Color("black"), (currentX, currentHeight, rect_width, rect_height))
			self.background.blit(currentActivity, (currentX + self.width / 4 - currentActivity.get_rect().width/2, currentHeight + currentActivity.get_rect().height/2))
			currentHeight += rect_height

		self.screen.blit(self.background, (0, 0))
		self.drawLines()
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
		if self.activities.activityIndex > 13:
			self.activities.activityIndex = 0
		if self.activities.activityIndex < 0:
			self.activities.activityIndex = 13

		rect_width = self.width / 2
		rect_height = ((self.height / 3)/4) 
		currentHeight = self.height / 5
		currentX = 0

		for i in range(14):

			#First row passed, change height and width
			if i == 7:
				currentHeight = self.height / 5
			if i > 6:
				currentX = self.width / 2

			if i == self.activities.activityIndex:
				break
			else:	
				currentHeight += rect_height

		self.activityText = self.font.render(self.activities.database.retrieveSubject(self.activities.days[self.activities.dayIndex],self.activities.activityIndex), 1, (0,0,0))
		if self.activities.dayChosen:
			self.background.fill(pygame.Color("yellow"), (currentX, currentHeight, rect_width, rect_height))
		self.background.blit(self.activityText, (currentX + self.width/4 - self.activityText.get_rect().width/2, currentHeight+rect_height/4))
		self.screen.blit(self.background, (0, 0))
		self.drawLines()
		pygame.display.flip()

	def recordingActivity(self):
		if self.activities.activityIndex > 13:
			self.activities.activityIndex = 0
		if self.activities.activityIndex < 0:
			self.activities.activityIndex = 13

		rect_width = self.width / 2
		rect_height = ((self.height / 3)/4) 
		currentHeight = self.height / 5
		currentX = 0

		for i in range(14):

			#First row passed, change height and width
			if i == 7:
				currentHeight = self.height / 5
			if i > 6:
				currentX = self.width / 2

			if i == self.activities.activityIndex:
				break
			else:	
				currentHeight += rect_height

		self.activityText = self.font.render(self.activities.database.retrieveSubject(self.activities.days[self.activities.dayIndex],self.activities.activityIndex), 1, (0,0,0))
		if self.activities.dayChosen:
			self.background.fill(pygame.Color("red"), (currentX, currentHeight, rect_width, rect_height))
		self.background.blit(self.activityText, (currentX + self.width/4 - self.activityText.get_rect().width/2, currentHeight+rect_height/4))
		self.screen.blit(self.background, (0, 0))
		self.drawLines()
		pygame.display.flip()

	#Upon using the D-PAD to choose a new activity the previous activity selected is reset to unselected
	def clearActivity(self):
		rect_width = self.width / 2
		rect_height = ((self.height / 3)/4) 
		currentHeight = self.height / 5
		currentX = 0

		for i in range(14):

			#First row passed, change height and width
			if i == 7:
				currentHeight = self.height / 5
			if i > 6:
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
		lineHeight = ((self.height / 3)/4)
		currentHeight = lineHeight + self.height / 5
		#top line
		pygame.draw.line(self.screen, pygame.Color("white"), (0, self.height / 5), (self.width, self.height / 5), 2)
		#middle line
		pygame.draw.line(self.screen, pygame.Color("white"), (self.width/2, self.height / 5), (self.width/2, currentHeight+(lineHeight*6)), 2)
		#far right line
		pygame.draw.line(self.screen, pygame.Color("white"), (self.width-2, self.height / 5), (self.width-2, currentHeight+(lineHeight*6)), 2)
		#far left line
		pygame.draw.line(self.screen, pygame.Color("white"), (0, self.height / 5), (0, currentHeight+(lineHeight*6)), 2)
		for i in range(7):
			pygame.draw.line(self.screen, pygame.Color("white"), (0, currentHeight), (self.width, currentHeight), 2)
			currentHeight += lineHeight

		pygame.draw.rect(self.screen, (237, 243, 251), (0, currentHeight-5, self.width, self.width), 0)
		if self.activities.dayChosen:
			self.drawActivityInstructions()	
		else:
			self.drawDayInstructions()
		pygame.display.flip()

def main():
	running = 1

	#Create objects
	Activities = ActivityList()
	screen = MainScreen(Activities)


	#Infinite loop to run the program
	while running:
		event = pygame.event.poll()
		if event.type == pygame.QUIT:
			running = 0

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
					screen.initActivities()
					screen.updateActivity()
					screen.clearActivity()

			if event.key == pygame.K_LEFT and not Activities.dayChosen:
				if Activities.activityChosen == False:
					screen.clearDay()
					Activities.dayIndex -= 1
					screen.updateDay()
					screen.initActivities()
					screen.updateActivity()
					screen.clearActivity()

			#Select the day with the enter key, change to A button on the wiimote
			if event.key == pygame.K_RETURN:
				if not Activities.dayChosen:
					Activities.dayChosen = True
					screen.dpad = pygame.image.load("buttons/up_down.png")
					screen.initActivities()
					screen.updateActivity()

			#Navigate the day's activities with up/down arrow keys, change to D-PAD up/down buttons on wiimote
			if event.key == pygame.K_UP and Activities.dayChosen:
					if Activities.activityIndex == 0 and not Activities.isEmptyLast():
						screen.clearActivity()
						Activities.activityIndex -= 1
						screen.updateActivity()
					if Activities.activityChosen == False and Activities.activityIndex > 0:
						screen.clearActivity()
						Activities.activityIndex -= 1
						screen.updateActivity()
					else:
						pass

			if event.key == pygame.K_DOWN and Activities.dayChosen and not Activities.isEmpty():
				if Activities.activityChosen == False:
					screen.clearActivity()
					Activities.activityIndex += 1
					screen.updateActivity()
				else:
					pass

			#Unselect activity and choose a new day
			if event.key == pygame.K_BACKSPACE and Activities.dayChosen:
				if Activities.activityChosen == False:
					screen.dpad = pygame.image.load("buttons/next_prev.png")
					screen.clearActivity()
					Activities.activityIndex = 0
					Activities.dayChosen = False
					screen.drawLines()

			#Once a day has been chosen, we can remove activities from the list
			if event.key == pygame.K_0:
				if Activities.dayChosen == True:
					if not Activities.isEmpty():
						Activities.adjustActivities()
						screen.initActivities()

			#RELEASE RECORD (A BUTTON)
			if event.key == pygame.K_a and Activities.recording:
				if Activities.dayChosen == True:
					screen.updateActivity()
					Activities.recording = False

			#PRESS RECORD (A BUTTON)
			if event.key == pygame.K_a and not Activities.recording:
				if Activities.dayChosen == True:
					screen.recordingActivity()
					Activities.recording = True

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
				pass

	pygame.quit()
			
main()