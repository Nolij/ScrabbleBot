import json as JSON
import re as RegExp
import multiprocessing as MultiProcessing
from time import time as tick

GLOBALEXCLUDE = "^.$"

BLANKVALUE = -0.01

WORDFILE = open("words.json", "r")
WORDLIST = tuple(JSON.loads(WORDFILE.read()))
WORDFILE.close()

def FindWords_SingleThread(Expression, Exclude = "^$"): # DEPRECATED
	Words = tuple()
	for WORD in WORDLIST:
		if (RegExp.search(Expression, WORD) and not RegExp.search(Exclude, WORD)): Words += ( WORD, )
	return Words

def Thread(Arguments):
	Word, Expression, Exclude = Arguments
	return RegExp.search("(?!(" + Exclude + "))" + Expression, Word) and Word or None

def FindWords(Expression, Exclude = "^$"):
	WordList = []
	for Word in WORDLIST:
		WordList.append((Word, Expression, Exclude))
	Pool = MultiProcessing.Pool(processes = MultiProcessing.cpu_count())
	FilteredWords = tuple([ Word for Word in Pool.map(Thread, WordList) if (Word != None) ])
	Pool.close()
	return FilteredWords

def FindWordsWithBank(LetterList, Filter = "^.*$"):
	Letters = "".join(LetterList)
	Include = ""
	Exclude = ""
	LetterMap = {}
	for Letter in LetterList:
		if (Letter == '.'): continue
		if (Letter not in LetterMap.keys()): LetterMap[Letter] = 0
		LetterMap[Letter] += 1
	Blanks = len(RegExp.findall("\\.", Letters))
#	Include += "^[" + "".join(LetterMap.keys()) + "]*"
#	if (Blanks > 0):
#		for i in range(Blanks, 0, -1):
#			Include += ".[" + "".join(LetterMap.keys()) + "]*"
#	Include += '$'
	Exclude += GLOBALEXCLUDE
#	if (Blanks == 0):
#		for Letter in LetterMap.keys():
#			# Exclude += "|(" + Letter + "(.*" + Letter + "){" + str(LetterMap[Letter] + Blanks) + "})"
#			Include = ("(?=(^([^%c]*%c){0,%d}[^%c]*$))" % (Letter, Letter, LetterMap[Letter], Letter)) + Include
#	elif (Blanks == 1):
#		for Blank in LetterMap.keys():
#			for Letter in LetterMap.keys():
#				n = LetterMap[Letter]
#				if (Blank == Letter): n += 1
#				Include = ("(?=(^([^%c]*%c){0,%d}[^%c]*$))" % (Letter, Letter, n, Letter)) + Include
#	elif (Blanks == 2):
#		for Blank1 in LetterMap.keys():
#			for Blank2 in LetterMap.keys():
#				for Letter in LetterMap.keys():
#					n = LetterMap[Letter]
#					if (Blank1 == Letter): n += 1
#					if (Blank2 == Letter): n += 1
#					Include = ("(?=(^([^%c]*%c){0,%d}[^%c]*$))" % (Letter, Letter, n, Letter)) + Include
#	else:
	def GenerateLookAheads(Include, BlankTiles = []):
		for Tile in LetterMap.keys():
			BlankTiles.append(Tile)
			Include = ")|" + Include
			for Letter in LetterMap.keys():
				n = LetterMap[Letter]
				for BlankTile in BlankTiles:
					if (BlankTile == Letter): n += 1
				Include = ("(?=(^([^%c]*%c){0,%d}[^%c]*$))" % (Letter, Letter, n, Letter)) + Include
			Include = ("(?=(^[%s]*(.[%s]*){%d}$))" % ("".join(LetterMap.keys()), "".join(LetterMap.keys()), Blanks - len(BlankTiles))) + Include
			Include = '(' + Include
			if (len(BlankTiles) < Blanks): Include = GenerateLookAheads(Include, BlankTiles)
			del BlankTiles[-1]
		if (len(LetterMap.keys()) == 0):
			Include = ")|" + Include
			Include += "(?=(^.{1,%d}$))" % Blanks
			Include = '(' + Include
		return Include
	Include = ')' + Include
	if (Blanks > 0):
		PreLen = len(Include)
		Include = GenerateLookAheads(Include)
		Include = Include[0 : len(Include) - PreLen - 1] + Include[len(Include) - PreLen : ]
		Include = '|' + Include
	for Letter in LetterMap.keys():
	#	Exclude += "|(" + Letter + "(.*" + Letter + "){" + str(LetterMap[Letter] + Blanks) + "})"
		Include = ("(?=(^([^%c]*%c){0,%d}[^%c]*$))" % (Letter, Letter, LetterMap[Letter], Letter)) + Include
	Include = ("(?=(^[%s]*(.[%s]*){%d}$))" % ("".join(LetterMap.keys()), "".join(LetterMap.keys()), Blanks)) + Include
	Include = '(' + Include
#	Exclude += "|^(.){" + str(len(LetterList)) + "}.+$"
	Include += Filter
	return (Include, Exclude)

LETTERS = {
	'a': 9,
	'b': 2,
	'c': 2,
	'd': 4,
	'e': 12,
	'f': 2,
	'g': 3,
	'h': 2,
	'i': 9,
	'j': 1,
	'k': 1,
	'l': 4,
	'm': 2,
	'n': 6,
	'o': 8,
	'p': 2,
	'q': 1,
	'r': 6,
	's': 4,
	't': 6,
	'u': 4,
	'v': 2,
	'w': 2,
	'x': 1,
	'y': 2,
	'z': 1
}

BLANKS = 2

for LETTER in LETTERS.keys():
	GLOBALEXCLUDE += "|(" + LETTER + "([^" + LETTER + "]*" + LETTER + "){" + str(LETTERS[LETTER] + BLANKS) + "})"

VALUES = {
	'a': 1,
	'b': 3,
	'c': 3,
	'd': 2,
	'e': 1,
	'f': 4,
	'g': 2,
	'h': 4,
	'i': 1,
	'j': 8,
	'k': 5,
	'l': 1,
	'm': 3,
	'n': 1,
	'o': 1,
	'p': 3,
	'q': 10,
	'r': 1,
	's': 1,
	't': 1,
	'u': 1,
	'v': 4,
	'w': 4,
	'x': 8,
	'y': 4,
	'z': 10
}

def WordValue(Word):
	Value = 0
	for i in range(len(Word)):
		Value += VALUES[Word[i]]
	#	Value += (100 - ord(Word[i])) / (100 * (100 ** i))
	return Value

def WordValueWithBank(Letters):
	Letters = tuple(Letters[:])
	def WordValue(Word):
		_Letters = []
		for Letter in Letters:
			_Letters.append(Letter)
		Value = 0
		for i in range(len(Word)):
			if (Word[i] in _Letters):
				Value += VALUES[Word[i]]
				_Letters.remove(Word[i])
			else:
				Value += BLANKVALUE
		#	Value += (100 - ord(Word[i])) / (100 * (100 ** i))
		return Value
	return WordValue

if (__name__ == "__main__"):
	while (True):
		print()
		print("1 - Word Finder")
		print("2 - RegExp Search")
		print("3 - Letter Checker")
		print()
		print("0 - Exit")

		try:
			Option = int(input(": "))
		except:
			continue
		if (Option == 1):
			Letters = input("Letters: ").strip().lower()
			Filter = input("Filter: ").strip()
			LetterList = list(Letters)
			LetterList.sort()
			Include, Exclude = FindWordsWithBank(LetterList, Filter)
			print(Include)
			print(Exclude)
			Words = list(FindWords(Include, Exclude))
			Words.sort()
			Words.sort(key = WordValueWithBank(LetterList), reverse = True)
			print(Words)
		elif (Option == 2):
			Include = input("Include: ").strip()
			Exclude = input("Exclude: ").strip()
			Words = list(FindWords(Include, Exclude or "^$"))
			Words.sort()
			Words.sort(key = WordValue, reverse = True)
			print(Words)
		elif (Option == 3):
			Letter = input("Letter: ").strip()
			Letter = Letter[0].lower()
			print("%d %s%s; %d point%s each" % (LETTERS[Letter], Letter.upper(), LETTERS[Letter] > 1 and "'s" or "", VALUES[Letter], VALUES[Letter] > 1 and 's' or ""))
		elif (Option == 0):
			break
		else:
			continue