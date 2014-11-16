import pyttsx
import pygame
import sys
import sqlite3
import threading
from threading import Thread
import thread
import os

pygame.init()

class ActivityDatabase:
	def __init__(self):
		self.db = self.init_database()
		self.cursor = self.db.cursor()
		self.init_database()

	#Create the database table if necessary
	def init_database(self):
		try:
			days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
			db = sqlite3.connect('activelist2.db')
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

#Voice driver object to control the text to speech for the user. (AUDITORY DESIGN)
class VoiceDriver:
	def __init__(self, activities):
		self.engine = pyttsx.init()
		self.engine.setProperty('rate', 150)
		self.activities = activities
		self.speaking = False

	def speak(self, location, input):
		self.engine.say(input)
		self.engine.startLoop()

	def stop(self):
		self.engine.endLoop()
		self.engine.stop()

	def createSpeakThread(self, VoiceOutput, input):
		newArgs = (1, input)
		thread = Thread(target=self.speak, args=newArgs)
		if self.speaking:
			self.stop()
			self.speaking = False
		return thread

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

	def incrementDay(self):
		self.dayIndex += 1
		if self.dayIndex > 6:
			self.dayIndex = 0

	def decrementDay(self):
		self.dayIndex -= 1
		if self.dayIndex < 0:
			self.dayIndex = 6

	def incrementActivity(self):
		self.activityIndex += 1

	def decrementActivity(self):
		self.activityIndex -= 1

	def resetActivityIndex(self):
		self.activityIndex = 0

	def getDay(self):
		return self.days[self.dayIndex]

	def getActivity(self):
		return self.activityIndex

def main():	
	#USED JUST FOR TESTING PYGAME KEYBOARD INPUT (requires this for some reason)
	screenInfo = pygame.display.Info()
	width = screenInfo.current_w
	height = screenInfo.current_h
	screen = pygame.display.set_mode((width, height))
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((0, 0, 0))
	screen.blit(background, (0, 0))
	pygame.display.flip()

	#All the important stuff
	Activities = ActivityList()
	VoiceOutput = VoiceDriver(Activities)
	running = 1

	#Initialize the day as monday being spoken
	thread1 = VoiceOutput.createSpeakThread(VoiceOutput, Activities.getDay())
	thread1.start()
	VoiceOutput.speaking = True

	while running:
		event = pygame.event.poll()
		if event.type == pygame.QUIT:
			running = 0
			VoiceOutput.stop()

		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_RIGHT:
				Activities.resetActivityIndex()
				Activities.incrementDay()
				thread1 = VoiceOutput.createSpeakThread(VoiceOutput, Activities.getDay())
				thread1.start()
				VoiceOutput.speaking = True

			if event.key == pygame.K_LEFT:
				Activities.resetActivityIndex()
				Activities.decrementDay()
				thread1 = VoiceOutput.createSpeakThread(VoiceOutput, Activities.getDay())
				thread1.start()
				VoiceOutput.speaking = True

			if event.key == pygame.K_UP:
				if Activities.getActivity() == -1:
					Activities.incrementActivity()
				activity = Activities.database.retrieveSubject(Activities.getDay(), Activities.getActivity())
				if activity == None: 
					thread1 = VoiceOutput.createSpeakThread(VoiceOutput, "End of activities")
					thread1.start()
					VoiceOutput.speaking = True
				else:
					thread1 = VoiceOutput.createSpeakThread(VoiceOutput, activity)
					thread1.start()
					VoiceOutput.speaking = True
					Activities.incrementActivity()

			if event.key == pygame.K_DOWN:
				Activities.decrementActivity()
				activity = Activities.database.retrieveSubject(Activities.getDay(), Activities.getActivity())
				if activity == None: 
					thread1 = VoiceOutput.createSpeakThread(VoiceOutput, "End of activities")
					thread1.start()
					VoiceOutput.speaking = True
				else:
					thread1 = VoiceOutput.createSpeakThread(VoiceOutput, activity)
					thread1.start()
					VoiceOutput.speaking = True

main()