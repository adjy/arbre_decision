import data_arbres
datas = data_arbres.load_data('tp_donnees.csv')

noeud= data_arbres.Noeud(10)
noeud.grow(datas)
precision = data_arbres.precision(noeud, datas)


# noeud.elagage(noeud, datas, 17)

data_arbres.stats(datas, 80, profondeur = 10)



