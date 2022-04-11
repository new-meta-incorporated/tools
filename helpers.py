import random
import json
import requests
import sys
import codecs
import os

from flask import Flask, redirect, url_for, request, jsonify, make_response, render_template

import conf

# CONF #

DEBUG = conf.datasources["debug"]
DATA_DIR = conf.datasources["data_dir"]

# /CONF #

### MAIN ###
#Backend Flask app code starts there
app = Flask(__name__)

def getAvailableMovesNames():
	moveNames = []
	movesDataFile = open(DATA_DIR + "moves.ts", "r", encoding='utf-8')
	movesData = movesDataFile.read()
	movesDataFile.close()
	moveBlocks = movesData.split("\n\t},\n\t")
	moveBlocks.pop(0)
	for moveBlock in moveBlocks:
		moveName = moveBlock.split(':')[0]
		moveNames.append(moveName)
	return moveNames

def validateMoveName(moveName):
	availableMovesNames = getAvailableMovesNames()
	if moveName in availableMovesNames:
		return True
	return False

def getTypescriptBlock(pokemon, moves):
	#carriageReturn = "\r\n"
	carriageReturn = "<br/>"
	#tabulation = "\t"
	tabulation = "&nbsp;&nbsp;&nbsp;"
	typescriptBlock = ""
	typescriptBlock += pokemon + ": {" + carriageReturn
	typescriptBlock += tabulation + "learnset: {" + carriageReturn
	for move in moves:
		typescriptBlock += tabulation + tabulation + move + ": [\"8M\", \"7M\"]," + carriageReturn
	typescriptBlock +=  tabulation + "}," + carriageReturn
	typescriptBlock += "},"
	return typescriptBlock

def cleanSpecs(spec):
	invalidChars = ['-', ' ']
	for char in invalidChars:
		spec = spec.replace(char, '')
	spec = spec.lower()
	print(spec)
	return spec

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/getLearnsetBlock',methods = ['POST', 'GET'])
def getLearnsetBlock():
	if request.method == 'POST':
		if request.form:
			rejects = []
			learnsetSpec = cleanSpecs(request.form['learnsetSpec'])
			if "@" not in learnsetSpec:
				return render_template('learnsetsHelper.html', text="Input text does not match requirements")
			inputPokemonName = learnsetSpec.split('@')[0]
			inputMoves = learnsetSpec.split('@')[1].split(',')
            inputMoves = list(dict.fromkeys(inputMoves))
			for inputMove in inputMoves:
				if not validateMoveName(inputMove):
					rejects.append(inputMove)
			if rejects:
				return render_template('learnsetsHelper.html', text=rejects, rejects=True)
			typescriptResponse = getTypescriptBlock(inputPokemonName, inputMoves)
			return render_template('learnsetsHelper.html', text=typescriptResponse, mimetype='text/html')
	return render_template('learnsetsHelper.html')

if __name__ == '__main__':
	if DEBUG:
		app.run(debug = DEBUG)
	else:
		app.run(host='0.0.0.0')
