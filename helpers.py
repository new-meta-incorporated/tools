import os
from flask import Flask, request, render_template
import PIL
from PIL import Image
from git import Repo, Git

#User-defined config file
import conf

########################## CONF ##########################

DEBUG = conf.datasources["debug"]
DATA_DIR = conf.datasources["data_dir"]
LOCAL_SPRITES_GIT_REPO = conf.git_repo["rootdir"]

########################## MAIN ##########################
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
	carriageReturn = "<br/>"
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
	return spec

def saveSprite(sprite, type, orientation, filename, autoflip):
	filepaths = []
	if type == 'regular' and orientation == 'front':
		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["dex"] + filename)
		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5"] + filename)
	if type == 'regular' and orientation == 'back' and autoflip == 'no':
		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back"] + filename)
	if type == 'shiny' and orientation == 'front':
		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["dex-shiny"] + filename)
		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-shiny"] + filename)
	if type == 'shiny' and orientation == 'back' and autoflip == 'no':
		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back-shiny"] + filename)
	for filepath in filepaths:
		tmpSprite = Image.open(sprite)
		tmpSprite.save(filepath)
	if type == 'regular' and orientation == 'front':
		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["icons"] + filename)
		icon = Image.open(sprite)
		icon = icon.resize((40, 40))
		icon.save(LOCAL_SPRITES_GIT_REPO + conf.git_repo["icons"] + filename)
	if type == 'regular' and orientation == 'back' and autoflip == 'yes':
		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back"] + filename)
		autoflippedBacksprite = Image.open(sprite)
		autoflippedBacksprite = autoflippedBacksprite.transpose(PIL.Image.FLIP_LEFT_RIGHT)
		autoflippedBacksprite.save(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back"] + filename)
	if type == 'shiny' and orientation == 'back' and autoflip == 'yes':
		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back-shiny"] + filename)
		autoflippedBacksprite = Image.open(sprite)
		autoflippedBacksprite = autoflippedBacksprite.transpose(PIL.Image.FLIP_LEFT_RIGHT)
		autoflippedBacksprite.save(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back-shiny"] + filename)
	return filepaths

def uploadOnGithub(filepaths):
	message = "Added: "
	os.chdir(LOCAL_SPRITES_GIT_REPO)
	repo = Repo.init(LOCAL_SPRITES_GIT_REPO).git
	index = Repo.init(LOCAL_SPRITES_GIT_REPO).index
	g = Git(LOCAL_SPRITES_GIT_REPO)
	g.pull('origin','master')
	for filepath in filepaths:
		message += "\n" + filepath.split(LOCAL_SPRITES_GIT_REPO)[1]
		repo.add(filepath)
	index.commit(message)
	g.push('origin','master')

########################## ROUTES ##########################

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

@app.route('/addSprites',methods = ['POST', 'GET'])
def addSprites():
	if request.method == 'POST':
		if 'sprite' in request.files and request.form:
			if '.png' not in request.form['sprite-name']:
				return render_template('spritesHelper.html', error='malformed sprite name: missing .png')
			filepaths = saveSprite(
				request.files['sprite'], 
				request.form['sprite-type'], 
				request.form['sprite-orientation'], 
				request.form['sprite-name'], 
				request.form['autoflip']
			)
			uploadOnGithub(filepaths)
			return render_template('spritesHelper.html')
	return render_template('spritesHelper.html')

if __name__ == '__main__':
	if DEBUG:
		app.run(debug = DEBUG)
	else:
		app.run(host='0.0.0.0')
