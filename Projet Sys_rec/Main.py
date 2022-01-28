# -*- coding: utf-8 -*-
"""
Created on Wed May 12 23:16:30 2021

@author: geekl
"""
import numpy
import math
from scipy import spatial
matriceBinary=numpy.zeros((0,0))
import nltk
from nltk.corpus import stopwords
import mysql.connector
from nltk.stem.snowball import EnglishStemmer
def SimilariteCosinus(a,b):
    return (1-spatial.distance.jaccard(matriceBinary[a],matriceBinary[b]))
connexion=mysql.connector.connect(host='localhost', user="root",password='',database='projet')
curseur=connexion.cursor()
#print("connexion etablie")
curseur.execute('select * from produit')
produit=curseur.fetchall()
StopList=list(stopwords.words('English'))
StopList.extend([".",",",":","/","!","?"])
dicProduits={}
ListTotalMots=set()
for p in produit:
         id_prod=p[0]
         Description=p[2]
         Mots=nltk.word_tokenize(Description)
         #print(Mots)
         stemer=EnglishStemmer()
         MotsStemes=[]
         for m in Mots:
            MotsStemes.append(stemer.stem(m))
         #print(MotsStemes)
         ListFinalMots=[]
         for m in MotsStemes :
           if m not in StopList:
              ListFinalMots.append(m)
         ListUniqueMots=set(ListFinalMots)
         for m in ListUniqueMots:
             ListTotalMots.add(m)
         dicProduits[id_prod]=ListUniqueMots
#
#print(dicProduits)
#print("matrice de ",len(dicProduits),"sur",len(ListTotalMots))
curseur.close()
matriceBinary=numpy.zeros((len(dicProduits),len(ListTotalMots)))
ListTotalMots= list(ListTotalMots)
for i in range(len(dicProduits)):
    j=0
    for m in ListTotalMots:
        if m in dicProduits[str("prod"+str(i+1))]:
            matriceBinary[i][j]=1
        j+=1
#print(matriceBinary)
matriceSimilarite=numpy.zeros((len(dicProduits),len(dicProduits)))
for i in range(len(dicProduits)):
    for j in range(len(dicProduits)):
        matriceSimilarite[i][j]=SimilariteCosinus(i, j)
#print(matriceSimilarite) 
mat_binaire=numpy.zeros((len(dicProduits),len(ListTotalMots)))
ListTotal=list(ListTotalMots)
k=0
for list in dicProduits.values() :
    j=0
    for m in ListTotalMots :
        y = 0
        if m in list :
            for n in list :
                if n==m :
                    y=y+1

            tf= y/len(list)
            x=0
            for n in dicProduits.keys() :
                for t in dicProduits[n]:
                    if m == t:
                        x = x + 1

            idf=math.log(len(dicProduits)/x)

    mat_binaire[k][j]= tf*idf
    #print(mat_binaire[k][j])
    j=j+1
    k=k+1        
#print(mat_binaire)
#Top Products in our web site
# function TOP
curseur = connexion.cursor()
for i in range(len(dicProduits)):
    max1=0
    max2=0
    max3=0
    for j in range(len(dicProduits)):
        if (matriceSimilarite[i][j]>max1) and (matriceSimilarite[i][j]!=1):
            max1=matriceSimilarite[i][j]
            p1=j+1
    for j in range(len(dicProduits)):
        if (matriceSimilarite[i][j]>max2) and (matriceSimilarite[i][j]!=1)and (matriceSimilarite[i][j]!=max1):
            max2=matriceSimilarite[i][j]
            p2=j+1
    for j in range(len(dicProduits)):
        if (matriceSimilarite[i][j]>max3) and (matriceSimilarite[i][j]!=1)and(matriceSimilarite[i][j]!=max1)and(matriceSimilarite[i][j]!=max2):
            max3=matriceSimilarite[i][j]
            p3=j+1        
    w="prod"+str(i+1)
    sql = "UPDATE produit SET top1=%s, top2=%s ,top3=%s WHERE Id_prod=%s"
    value = (p1,p2,p3,w)
    curseur.execute(sql, value)
    connexion.commit()
#Partie 2
connexion = mysql.connector.connect(host="localhost",user="root",password="",database="projet")
curseur = connexion.cursor()
curseur.execute("SELECT * FROM user")
user=curseur.fetchall()
matricenote=numpy.zeros((len(user),len(produit)))
curseur =connexion.cursor()
curseur.execute("SELECT * FROM note ")
note=curseur.fetchall()
#print(note) 
     
for row in range(len(note)):
    userindex=-1
    prodindex=-1
    nom=note[row][0]
    Id_prod=note[row][1]
    rate=note[row][2]
    #print(rate)
    for i in range(len(user)):
         if nom==user[i][0]:
             userindex=i
             break
    for i in range(len(produit)):
         if produit[i][0]==Id_prod:
             prodindex=i
             break
    matricenote[userindex][prodindex]=rate
    #print(int(matricenote[userindex][prodindex]))
print(matricenote)
#recherche des users voisins
matricesimilariteUser=numpy.zeros((len(user),len(user)))
for L in range(len(user)):
   for c in range(len(user)):
       matricesimilariteUser[L][c]=SimilariteCosinus(L,c)
#print(matricesimilariteUser)
for i in range(len(user)):
    for j in range(len(user)):
        matricesimilariteUser[i,j]=SimilariteCosinus(i,j)  
for i in range(len(user)):
 for j in range(len(dicProduits)):
     if matricenote[i][j]==0:
       voisin1=0
       voisin2=0
       sim1=0
       Z=0
       for sim in matricesimilariteUser[i]:
                if sim>sim1 and sim!=1:
                    sim1=sim
                    voisin1=Z
                Z+=1
       sim2=0
       N=0
       for sim in matricesimilariteUser[i]:
                 if sim>sim2 and sim!=1 and sim!=sim1:
                    sim2=sim
                    voisin2=N
                 N+=1 
       pre=(sim1*matricenote[voisin1][j]+sim2*matricenote[voisin2][j])/(sim1+sim2)
       matricenote[i][j]=pre
print(matricenote)
