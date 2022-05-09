import os
import json
from flask import Flask, request, jsonify, render_template

#User-defined config file
import conf

########################## CONF ##########################

DEBUG = conf.datasources["debug"]
TEXT_DATA_DIR = conf.datasources["text_data_dir"]
DATA_DIR = conf.datasources["data_dir"]
LOCAL_SPRITES_GIT_REPO = conf.git_repo["rootdir"]

########################## MAIN ##########################
#Backend Flask app code starts there
app = Flask(__name__)

def getJSONResult(splittedStringList):
	tmpDict = {}
	for objectAttr in splittedStringList:
		attr = objectAttr.split(':', 1)[0]
		value = objectAttr.split(':', 1)[1].strip()
		if '{' in value:
			values = value.split(',')
			value = {}
			for item in values:
				part1 = item.split(':')[0].strip().replace('{', '')
				part2 = item.split(':')[1].strip().replace('}', '').replace('\"', '')
				value[part1] = part2
		elif '[' in value:
			arrayData = value.replace('\"', '').replace('[', '').replace(']', '').replace(' ', '')
			value = arrayData.split(',')
		else:
			value = value.replace('\"', '')
		tmpDict[attr] = value
	return tmpDict

########################## ROUTES ##########################

@app.route('/')
def index():
	routes = [
		{'route':'getAllMoves', 'desc':'Returns all moves ids.'},
		{'route':'getAllAbilities', 'desc':'Returns all abilities ids.'},
		{'route':'getAllItems', 'desc':'Returns all items ids.'},
		{'route':'getAllPokemons', 'desc':'Returns all pokemons ids.'},
		{'route':'getLearnset/<pokemonId>', 'desc':'Returns pokemon learnset info.'},
		{'route':'getFormatsData/<pokemonId>', 'desc':'Returns pokemon formats-data info.'},
		{'route':'getPokedex/<pokemonId>', 'desc':'Returns pokemon pokedex info.'},
		{'route':'getMove/<moveId>', 'desc':'Returns move info.'},
		{'route':'getAbility/<abilityId>', 'desc':'Returns ability info.'},
		{'route':'getItem/<itemId>', 'desc':'Returns item info.'}
	]
	return render_template('routes.html', baseUrl=request.base_url, routes=routes)

@app.route('/getAllMoves',methods = ['GET'])
def getAllMoves():
	if request.method == 'GET':
		moveNames = []
		movesDataFile = open(TEXT_DATA_DIR + "moves.ts", "r", encoding='utf-8')
		movesData = movesDataFile.read()
		movesDataFile.close()
		moveBlocks = movesData.split("\n\t},\n\t")
		moveBlocks.pop(0)
		for moveBlock in moveBlocks:
			moveName = moveBlock.split(':')[0]
			moveNames.append(moveName)
		return jsonify(moveNames)
	return {}

@app.route('/getAllAbilities',methods = ['GET'])
def getAllAbilities():
	if request.method == 'GET':
		abilityNames = []
		abilitiesDataFile = open(TEXT_DATA_DIR + "abilities.ts", "r", encoding='utf-8')
		abilitiesData = abilitiesDataFile.read()
		abilitiesDataFile.close()
		abilityBlocks = abilitiesData.split("\n\t},\n\t")
		abilityBlocks.pop(0)
		for abilityBlock in abilityBlocks:
			abilityName = abilityBlock.split(':')[0]
			abilityNames.append(abilityName)
		return jsonify(abilityNames)
	return {}

@app.route('/getAllItems',methods = ['GET'])
def getAllItems():
	if request.method == 'GET':
		itemNames = []
		itemsDataFile = open(TEXT_DATA_DIR + "items.ts", "r", encoding='utf-8')
		itemsData = itemsDataFile.read()
		itemsDataFile.close()
		itemBlocks = itemsData.split("\n\t},\n\t")
		itemBlocks.pop(0)
		for itemBlock in itemBlocks:
			itemName = itemBlock.split(':')[0]
			itemNames.append(itemName)
		return jsonify(itemNames)
	return {}

@app.route('/getAllPokemons',methods = ['GET'])
def getAllPokemons():
	if request.method == 'GET':
		pokedexNames = []
		pokedexDataFile = open(DATA_DIR + "pokedex.ts", "r", encoding='utf-8')
		pokedexData = pokedexDataFile.read()
		pokedexDataFile.close()
		pokedexBlocks = pokedexData.split(",\n\t},")
		pokedexBlocks.pop(0)
		print(pokedexBlocks[0])
		for pokedexBlock in pokedexBlocks:
			pokedexName = pokedexBlock.split(':')[0].replace('\n', '').replace('\t', '')
			pokedexNames.append(pokedexName)
		return jsonify(pokedexNames)
	return {}

@app.route('/getLearnset/<pokemonId>',methods = ['GET'])
def getLearnset(pokemonId):
	if request.method == 'GET':
		learnset = {}
		learnsetsDataFile = open(DATA_DIR + "learnsets.ts", "r", encoding='utf-8')
		learnsetsData = learnsetsDataFile.read()
		learnsetsDataFile.close()
		learnsetsBlocks = learnsetsData.split(",\n\t},")
		learnsetsBlocks.pop(0)
		for learnsetsBlock in learnsetsBlocks:
			if pokemonId + ':' in learnsetsBlock:
				moveString = learnsetsBlock.split('learnset: {')[1].split('},')[0]
		moveBlocks = moveString.split('],')
		learnset = [moveBlock.strip().split(':')[0] for moveBlock in moveBlocks][:-1]
		return jsonify(learnset)
	return {}

@app.route('/getFormatsData/<pokemonId>',methods = ['GET'])
def getFormatsData(pokemonId):
	if request.method == 'GET':
		formatsDataFile = open(DATA_DIR + "formats-data.ts", "r", encoding='utf-8')
		formatsDataData = formatsDataFile.read()
		formatsDataFile.close()
		formatsBlocks = formatsDataData.split(",\n\t},")
		formatsBlocks.pop(0)
		for formatsBlock in formatsBlocks:
			if '\t' + pokemonId + ':' in formatsBlock:
				formatsString = formatsBlock.split(pokemonId + ': {')[1].replace('\t', '')
		formatsAttrs = formatsString.split(',\n')
		formatsAttrs = [formatsAttr.replace('\n', '') for formatsAttr in formatsAttrs]
		return getJSONResult(formatsAttrs)
	return {}

@app.route('/getPokedex/<pokemonId>',methods = ['GET'])
def getPokedex(pokemonId):
	if request.method == 'GET':
		pokedexDataFile = open(DATA_DIR + "pokedex.ts", "r", encoding='utf-8')
		pokedexData = pokedexDataFile.read()
		pokedexDataFile.close()
		pokedexBlocks = pokedexData.split(",\n\t},")
		pokedexBlocks.pop(0)
		for pokedexBlock in pokedexBlocks:
			if '\t' + pokemonId + ':' in pokedexBlock:
				pokedexString = pokedexBlock.split(pokemonId + ': {')[1].replace('\t', '')
		pokedexAttrs = pokedexString.split(',\n')
		pokedexAttrs = [pokedexAttr.replace('\n', '') for pokedexAttr in pokedexAttrs]
		return getJSONResult(pokedexAttrs)
	return {}

@app.route('/getMove/<moveId>',methods = ['GET'])
def getMove(moveId):
	if request.method == 'GET':
		attrs = []
		textAttrs = []
		usefulAttrs = ['num', 'accuracy', 'basePower', 'category', 'name', 'pp', 'priority', 'flags', 'type']
		usefulTextAttrs = ['desc']
		movesTextFile = open(TEXT_DATA_DIR + "moves.ts", "r", encoding='utf-8')
		movesDataFile = open(DATA_DIR + "moves.ts", "r", encoding='utf-8')
		movesData = movesDataFile.read()
		movesText = movesTextFile.read()
		movesTextFile.close()
		movesDataFile.close()
		movesTextBlocks = movesText.split(",\n\t},")
		movesTextBlocks.pop(0)
		movesBlocks = movesData.split(",\n\t},")
		movesBlocks.pop(0)
		for movesBlock in movesBlocks:
			if '\t' + moveId + ': {' in movesBlock:
				moveString = movesBlock.split(moveId + ': {', 1)[1].replace('\t', '')
		for movesTextBlock in movesTextBlocks:
			if '\t' + moveId + ': {' in movesTextBlock:
				moveTextString = movesTextBlock.split(moveId + ': {', 1)[1].replace('\t', '')
		moveAttrs = moveString.split(',\n')
		moveTextAttrs = moveTextString.split(',\n')
		for moveAttr in moveAttrs:
			for usefulAttr in usefulAttrs:
				if moveAttr.replace('\n', '').startswith(usefulAttr):
					attrs.append(moveAttr)
		moveAttrs = [moveAttr.replace('\n', '') for moveAttr in attrs]
		for moveTextAttr in moveTextAttrs:
			for usefulTextAttr in usefulTextAttrs:
				if moveTextAttr.replace('\n', '').startswith(usefulTextAttr):
					textAttrs.append(moveTextAttr)
		moveAttrs = [moveAttr.replace('\n', '') for moveAttr in attrs]
		moveTextAttrs = [moveTextAttr.replace('\n', '') for moveTextAttr in textAttrs]
		move = getJSONResult(moveAttrs)
		textAttrs = getJSONResult(moveTextAttrs)
		for textAttr in textAttrs:
			move[textAttr] = textAttrs[textAttr]
		return move
	return {}

@app.route('/getAbility/<abilityId>',methods = ['GET'])
def getAbility(abilityId):
	if request.method == 'GET':
		attrs = []
		textAttrs = []
		usefulAttrs = ['num', 'name', 'isNonStandard']
		usefulTextAttrs = ['desc']
		abilitiesTextFile = open(TEXT_DATA_DIR + "abilities.ts", "r", encoding='utf-8')
		abilitiesDataFile = open(DATA_DIR + "abilities.ts", "r", encoding='utf-8')
		abilitiesData = abilitiesDataFile.read()
		abilitiesText = abilitiesTextFile.read()
		abilitiesTextFile.close()
		abilitiesDataFile.close()
		abilitiesTextBlocks = abilitiesText.split(",\n\t},")
		abilitiesTextBlocks.pop(0)
		abilitiesBlocks = abilitiesData.split(",\n\t},")
		abilitiesBlocks.pop(0)
		for abilitiesBlock in abilitiesBlocks:
			if '\t' + abilityId + ': {' in abilitiesBlock:
				abilityString = abilitiesBlock.split(abilityId + ': {', 1)[1].replace('\t', '')
		for abilitiesTextBlock in abilitiesTextBlocks:
			if '\t' + abilityId + ': {' in abilitiesTextBlock:
				abilityTextString = abilitiesTextBlock.split(abilityId + ': {', 1)[1].replace('\t', '')
		abilityAttrs = abilityString.split(',\n')
		abilityTextAttrs = abilityTextString.split(',\n')
		for abilityAttr in abilityAttrs:
			for usefulAttr in usefulAttrs:
				if abilityAttr.replace('\n', '').startswith(usefulAttr):
					attrs.append(abilityAttr)
		abilityAttrs = [abilityAttr.replace('\n', '') for abilityAttr in attrs]
		for abilityTextAttr in abilityTextAttrs:
			for usefulTextAttr in usefulTextAttrs:
				if abilityTextAttr.replace('\n', '').startswith(usefulTextAttr):
					textAttrs.append(abilityTextAttr)
		abilityAttrs = [abilityAttr.replace('\n', '') for abilityAttr in attrs]
		abilityTextAttrs = [abilityTextAttr.replace('\n', '') for abilityTextAttr in textAttrs]
		ability = getJSONResult(abilityAttrs)
		textAttrs = getJSONResult(abilityTextAttrs)
		for textAttr in textAttrs:
			ability[textAttr] = textAttrs[textAttr]
		return ability
	return {}

@app.route('/getItem/<itemId>',methods = ['GET'])
def getItem(itemId):
	if request.method == 'GET':
		attrs = []
		textAttrs = []
		usefulAttrs = ['num', 'name', 'isNonStandard']
		usefulTextAttrs = ['desc']
		itemsTextFile = open(TEXT_DATA_DIR + "items.ts", "r", encoding='utf-8')
		itemsDataFile = open(DATA_DIR + "items.ts", "r", encoding='utf-8')
		itemsData = itemsDataFile.read()
		itemsText = itemsTextFile.read()
		itemsTextFile.close()
		itemsDataFile.close()
		itemsTextBlocks = itemsText.split(",\n\t},")
		itemsTextBlocks.pop(0)
		itemsBlocks = itemsData.split(",\n\t},")
		itemsBlocks.pop(0)
		for itemsBlock in itemsBlocks:
			if '\t' + itemId + ': {' in itemsBlock:
				itemString = itemsBlock.split(itemId + ': {', 1)[1].replace('\t', '')
		for itemsTextBlock in itemsTextBlocks:
			if '\t' + itemId + ': {' in itemsTextBlock:
				itemTextString = itemsTextBlock.split(itemId + ': {', 1)[1].replace('\t', '')
		itemAttrs = itemString.split(',\n')
		itemTextAttrs = itemTextString.split(',\n')
		for itemAttr in itemAttrs:
			for usefulAttr in usefulAttrs:
				if itemAttr.replace('\n', '').startswith(usefulAttr):
					attrs.append(itemAttr)
		itemAttrs = [itemAttr.replace('\n', '') for itemAttr in attrs]
		for itemTextAttr in itemTextAttrs:
			for usefulTextAttr in usefulTextAttrs:
				if itemTextAttr.replace('\n', '').startswith(usefulTextAttr):
					textAttrs.append(itemTextAttr)
		itemAttrs = [itemAttr.replace('\n', '') for itemAttr in attrs]
		itemTextAttrs = [itemTextAttr.replace('\n', '') for itemTextAttr in textAttrs]
		item = getJSONResult(itemAttrs)
		textAttrs = getJSONResult(itemTextAttrs)
		for textAttr in textAttrs:
			item[textAttr] = textAttrs[textAttr]
		return item
	return {}

	

if __name__ == '__main__':
	if DEBUG:
		app.run(port=5001, debug = DEBUG)
	else:
		app.run(host='0.0.0.0')
