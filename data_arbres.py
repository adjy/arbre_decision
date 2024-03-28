import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
class DataPoint:
    def __init__(self, x, y, cles):
        self.x = {}
        for i in range(len(cles)):
            self.x[cles[i]] = float(x[i])
        self.y = int(y)
        self.dim = len(self.x)
        
    def __repr__(self):
        return 'x: '+str(self.x)+', y: '+str(self.y)


def load_data(filelocation):
    with open(filelocation,'r') as f:
        data = []
        attributs = f.readline()[:-1].split(',')[:-1]
        for line in f:
            z = line.split(',')
            if z[-1] == '\n':
                z = z[:-1]
            x = z[:-1]
            y = int(z[-1])
            data.append(DataPoint(x,y,attributs))
    return data


def proba_empirique(dataPoint):
    #Separer les donnees en 2 classes selon les valeurs de y
    classe = {}
    for i in dataPoint:
        classe[i.y] = 1 if i.y not in classe else classe[i.y] + 1
        
    taille = len(dataPoint)
    for elem in classe:
        classe[elem] = classe[elem] / taille
    return classe

def question_inf(x, a, s):
    return x[a] < s

def split(dataPoint, a, s):
    #Separe les donnees selon la question  (a, s) 
    d1 = [] # appartient
    d2 = [] # n'appartient pas
    for data in dataPoint:
        if question_inf(data.x, a, s):
            d1.append(data)
        else:
            d2.append(data)
    return d1 ,d2


def list_separ_attributs(dataPoint, a):
    #cherche une ensemble de question, selon la formule (x + (x+1))/ 2
    questions = []
    listeVal = []
    
    for data in dataPoint:
        listeVal.append(data.x[a])
    
    listeVal = list(set(listeVal))
    listeVal.sort()
    
    for i in range(len(listeVal) - 1):
        questions.append( ( a, (listeVal[i] + listeVal[i + 1]) / 2))
        
    return questions
    
        
def liste_questions(dataPoint):
    #renvoie la liste de toutes les questions possibles
    questions = []

    for attribut in list(dataPoint[0].x.keys()):
        questions = questions + list_separ_attributs(dataPoint, attribut)
    return questions
    
def entropie(dataPoint):
    # l'incertitude, erreur
    entrop = 0
    probas = proba_empirique(dataPoint)
    
    for proba in probas.values():
        if proba != 0:
            entrop += proba * math.log(proba, 2)
    return -1 * entrop
  
def gain_entropie(dataPoint, question):
    #Mesure de la reduction d'un certitude
    d1, d2 = split(dataPoint, question[0], question[1])
    tailleDataPoint = len(dataPoint)
    r1 = len(d1) / tailleDataPoint
    r2 = len(d2) / tailleDataPoint
    
    return entropie(dataPoint) - r1 * entropie(d1) - r2 * entropie(d2)

def best_split(dataPoint):
    bestQuestion = 0
    best = None
    questions = liste_questions(dataPoint)    
    
    for question in questions:
        q = gain_entropie(dataPoint, question)
        if q > bestQuestion:
            bestQuestion = q
            best = question
                
    return best
         
    

class Noeud:
    def __init__(self, profondeur_max=np.infty, hauteur = np.infty):
        self.question = None
        self.enfants = {}
        self.profondeur_max = profondeur_max
        self.proba = None
        self.hauteur = hauteur
        
    def grow(self, data):
        entrop = entropie(data)
        bestQ = best_split(data)
        d1, d2 = [], []
        
        if bestQ != None:
            d1, d2 = split(data, bestQ[0], bestQ[1])

        if entrop > 0 and self.profondeur_max > 0 and len(d1) > 0 and len(d2) > 0:
            self.question = bestQ    
        
            self.enfants["true"] = Noeud(self.profondeur_max - 1)
            self.enfants["true"].grow(d1)
            
            self.enfants["false"] = Noeud(self.profondeur_max - 1)
            self.enfants["false"].grow(d2)
            
        else: 
            self.proba = proba_empirique(data)

    def prediction(self, x):
        if self == None or self.question == None :
            return self.proba
    
        if x[self.question[0]] < self.question[1]:
            return self.enfants["true"].prediction(x)
        else:
            return self.enfants["false"].prediction(x)
        
    # def elagage(self, noeud, alpha, dataPoint):
    #     if(noeud != None):
    #        if len(noeud.enfants) == 0:
    #            if()
    #         if gain_entropie(dataPoint, noeud.question) < alpha:
    #             noeud = None
    #     else:
    #         noeud.elagage(noeud.enfants["true"], alpha, dataPoint)
    #         noeud.elagage(noeud.enfants["false"], alpha, dataPoint)
        
        
# Ajoutez une m ́ethode elagage `a la classe Noeud, prenant un coefficient α, et `a 
# partir de la fin de l’arbre, retirant les noeuds jusqu’`a trouver des noeuds ayant eu un gain d’entropie sup ́erieur `a α.
    
def precision(noeud, datas):
    correct = 0
    taille = len(datas)
    if(taille == 0):
        pass
    for data in datas: 
        predi = noeud.prediction(data.x) 
        if(data.y  in predi and predi[data.y] > 0.5):
            correct += 1
    return (correct / taille) * 100

def subdivide(datas, pourcentage):
    taille = len(datas)
    nb = round(pourcentage * taille / 100)
    return datas[0:nb], datas[nb: taille]

def stats(datas, pourcentage, profondeur=10):
    prof = list(range(profondeur))
    precisionTest = []
    precisionApprentissage = []

    apprentissage, test = subdivide(datas, pourcentage)

    for i in range(profondeur):
        noeud = Noeud(i)
        noeud.grow(apprentissage)
        precisionTest.append(precision(noeud, test))
        precisionApprentissage.append(precision(noeud, apprentissage))

    graphique_double(prof, precisionTest, precisionApprentissage, "profondeur", "precision", "test", "apprentissage", "")



def graphique_double(x_values, y1_values, y2_values, xlabel, ylabel, label1, label2, title):
		fig, ax = plt.subplots()

		ax.plot(x_values, y1_values, label=label1)
		ax.plot(x_values, y2_values, label=label2)

		# Set the format of the y-axis ticks
		ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))

		ax.set_xlabel(xlabel)
		ax.set_ylabel(ylabel)
		ax.set_title(title)

		# Add a legend
		ax.legend()

		# Show the plot
		plt.show()
  