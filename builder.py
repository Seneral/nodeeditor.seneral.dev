#!/usr/bin/python
import sys
import json
import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

reURL = re.compile(r"(?:src|href|data(?:-?[A-Za-z0-9]{0,6})?)\s*=\s*[\"\']([^\"\']*)[\"\']")
curPageID = "$CURPAGE"
config = None
frame = None

def main(argv):
	global config
	# Read config
	configPath = argv[1] if len(argv) > 1 else 'config.json'
	configFile = open(configPath, "r");
	configData = json.loads(configFile.read())
	configFile.close()
	config = Config(configData)
	# First-time build
	build()
	# Setup watchdog to build changed files
	observer = Observer()
	observer.schedule(ConfigChange(), '.', recursive=False)
	observer.schedule(SourceChange(), config.sourceFolder, recursive=True)
	observer.start()
	try:
		while True:
			time.sleep(20)
	except KeyboardInterrupt:
		pass
	finally:
		observer.stop()
		observer.join()

class Rule: 
	def __init__ (self, data):
		self.match = data['match']
		if 'source' in data:
			self.source = data['source']
			self.select = re.compile(data['select'] if 'select' in data else '(.*)', re.DOTALL)
		else:
			self.value = data['value'] if 'value' in data else ''
	def __str__(self):
		if hasattr(self, 'source'):
			return '("{0}" -> "{1}" from "{2}")'.format(self.match, self.select.pattern, self.source)
		return '("{0}" -> "{1}")'.format(self.match, self.value)

class Config:
	def __init__(self, data):
		self.sourceFolder = data['sourceFolder'] if 'sourceFolder' in data else "SOURCE"
		self.buildFolder = data['buildFolder'] if 'buildFolder' in data else "BUILD"
		self.frameFile = data['frameFile'] if 'frameFile' in data else "frame.html"
		self.relativePaths = data['relativePaths'] if 'relativePaths' in data else True
		self.onlyExisting = data['onlyExisting'] if 'onlyExisting' in data else False
		self.rules = []
		if 'rules' in data:
			for rule in data['rules']:
				self.rules.append(Rule(rule))

class ConfigChange(FileSystemEventHandler):
	patterns = [ '*.json', '*.html' ]
	def on_any_event(self, event):
		if not event.is_directory:
			build()

class SourceChange(FileSystemEventHandler):
	def on_any_event(self, event):
		if not event.is_directory:
			changedPath = None
			buildPath = os.path.join(config.buildFolder, event.src_path[len(config.sourceFolder)+1:])
			if event.event_type == 'deleted':
				if (os.path.isfile(buildPath)):
					os.remove(buildPath)
			elif event.event_type == 'moved':
				if (os.path.isfile(buildPath)):
					os.remove(buildPath)
				changedPath = event.dest_path
			else:
				changedPath = event.src_path
			if changedPath is not None: # Now check if file is still in sources
				if changedPath.startswith(config.sourceFolder):
					buildFile(changedPath[len(config.sourceFolder)+1:])
				else:
					print ("Moved out of source folder: '" + changedPath + "'")

def build():
	global frame
	# Load frame HTML
	frameFile = open(config.frameFile, "r")
	frame = unicode(frameFile.read(), 'utf-8')
	frameFile.close()
	# Check main folders
	if not os.path.exists(config.sourceFolder):
		os.makedirs(config.sourceFolder)
	if not os.path.exists(config.buildFolder):
		os.makedirs(config.buildFolder)
	# Get sources
	sources = []
	for root,d,files in os.walk(config.sourceFolder):
		for file in files:
			sources.append(os.path.join(root, file)[len(config.sourceFolder)+1:])
	# Process sources
	for sourcePath in sources:
		buildFile(sourcePath)
	
def buildFile(sourcePath):
	print ("Processing page '" + sourcePath + "'")
	# Read source
	sourceFile = open(os.path.join(config.sourceFolder, sourcePath), "r")
	source = unicode(sourceFile.read(), 'utf-8')
	sourceFile.close()
	# Apply rules on frame
	html = frame; # Frame is cached globally
	for rule in config.rules:
		match = rule.match.replace(curPageID, sourcePath)
		if hasattr(rule, 'source'):
			if (rule.source == curPageID):
				fileContent = source
			else: 
				file = open(rule.source, "r")
				fileContent = unicode(file.read(), 'utf-8')
				file.close()
			valueMatch = re.search(rule.select, fileContent)
			value = valueMatch.group(1) if valueMatch else ''
		else: 
			value = rule.value.replace(curPageID, sourcePath)
		html = html.replace(match, value)
	# Check paths
	if config.relativePaths:
		def makeURLRelative(match):
			url = match.group(1)
			if config.onlyExisting:
				if not os.path.isfile(os.path.join(config.buildFolder, url)):
					return match.group(0)
			elif url.startswith("http") or url.startswith("mailto:") or url.startswith("/") or url.startswith("\\") or url.startswith("#"):
				return match.group(0)
			relurl = os.path.relpath(url, os.path.dirname(sourcePath)) if url else ""
			return match.group(0).replace(url, relurl)
		html = re.sub(reURL, makeURLRelative, html)
	# Write target
	targetPath = os.path.join(config.buildFolder, sourcePath)
	if not os.path.exists(os.path.dirname(targetPath)):
		os.makedirs(os.path.dirname(targetPath))
	targetFile = open(targetPath, "w+")
	targetFile.write(html.encode('utf-8'))
	targetFile.close()

main(sys.argv)