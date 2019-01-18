#!/usr/bin/env python2.4
# -*- coding: UTF-8 -*-

import sys
import os
import ftplib
import cx_Oracle
import time
import datetime as dt
from time import mktime
from dateutil.relativedelta import relativedelta
import elementtree.ElementTree as ET


#Parametres pour la connexion à la base de données Oracle
ORA = "RSDBA/RSDBA@172.16.29.33:1521/N"

#Parametres FTP
TARGET_URI = "62.210.152.84"
USER = "airbreizh"
PWD  = "pwA1v2~4"

#Correspondance Base XR <==> Nom de ville et polluants
VILLES = {'1':'Rennes', 
        '2':'Brest',
        '3':'Lorient', 
        '4':'Vannes',
        '5':'Quimper',
        '6':'Saint-Malo',
        '8':'Saint-Brieuc'
        }

INSEE = {'1':'35238', 
        '2':'29019',
        '3':'56121', 
        '4':'56260',
        '5':'29232',
        '6':'35288',
        '8':'22278'
        }

ID = {'1':'756', 
        '2':'748',
        '3':'752', 
        '4':'754',
        '5':'750',
        '6':'760',
        '8':'762'
        }

DEPARTEMENTS = {'21':"Cotes d'Armor", #IND22
            '22':'Finistere',         #IND29
            '23':'Ille-et-Vilaine',   #IND35
            '24':'Morbihan'           #IND56
            }

DEPARTEMENTS_BALISE = {'21':"cotes-armor", #IND22
            '22':'finistere',              #IND29
            '23':'ille-vilaine',           #IND35
            '24':'morbihan'                #IND56
            }


POLLUANT = {'01':'SO2',
        '03':'NO2',
        '08':'O3',
        '24':'PM10'}


#Paramètres du fichier xml
XML = "/home/xair/partage/ExportWEB/historique/export_indices_%s.xml"
FORMAT = "%Y-%m-%d"
GARDE = True #efface ou non le fichier local





def valid(indices):
    '''corrige les valeurs d'indices'''
    i = list()
    for ind in indices:
        if ind is None:
            i.append('0')
        else:
            i.append(str(ind))
    return i


def ind2xml(date, indices, ssindices, fichier):
    '''Enregistre les indices fournis dans un fichier xml tel que :
    <indicesQA>
        <jour>
            <date>2018-02-19</date>
            <villes>
                <ville code_insee="56260" id="754" ind_j="0" nom="Vannes" ssind_j_NO2="2" ssind_j_O3="3" ssind_j_PM10="2" ssind_j_SO2="0"/>
                <ville code_insee="35288" id="760" ind_j="3" nom="Saint-Malo" ssind_j_NO2="2" ssind_j_O3="3" ssind_j_PM10="3" ssind_j_SO2="0"/>
                <ville code_insee="29019" id="748" ind_j="0" nom="Brest" ssind_j_NO2="1" ssind_j_O3="3" ssind_j_PM10="2" ssind_j_SO2="0"/>
                <ville code_insee="29232" id="750" ind_j="3" nom="Quimper" ssind_j_NO2="1" ssind_j_O3="3" ssind_j_PM10="3" ssind_j_SO2="0"/>
                <ville code_insee="35238" id="756" ind_j="0" nom="Rennes" ssind_j_NO2="0" ssind_j_O3="0" ssind_j_PM10="2" ssind_j_SO2="0"/>
                <ville code_insee="56121" id="752" ind_j="0" nom="Lorient" ssind_j_NO2="2" ssind_j_O3="3" ssind_j_PM10="2" ssind_j_SO2="0"/>
                <ville code_insee="22278" id="762" ind_j="0" nom="Saint-Brieuc" ssind_j_NO2="1" ssind_j_O3="3" ssind_j_PM10="1" ssind_j_SO2="0"/>
            </villes>
            <departements>
                <finistere ind_j="0" nom="Finistere"/>
                <morbihan ind_j="0" nom="Morbihan"/>
                <cotes-armor ind_j="3" nom="Cotes d'Armor"/>
                <ille-vilaine ind_j="0" nom="Ille-et-Vilaine"/>
            </departements>
        </jour>
        <jour>
            <date>2018-02-20</date>
            <villes>
                <ville code_insee="56260" id="754" ind_j="3" nom="Vannes"/>
                <ville code_insee="35288" id="760" ind_j="4" nom="Saint-Malo"/>
                <ville code_insee="29019" id="748" ind_j="3" nom="Brest"/>
                <ville code_insee="29232" id="750" ind_j="3" nom="Quimper"/>
                <ville code_insee="35238" id="756" ind_j="4" nom="Rennes"/>
                <ville code_insee="56121" id="752" ind_j="4" nom="Lorient"/>
                <ville code_insee="22278" id="762" ind_j="4" nom="Saint-Brieuc"/>
            </villes>
            <departements>
                <finistere ind_j="0" nom="Finistere"/>
                <morbihan ind_j="0" nom="Morbihan"/>
                <cotes-armor ind_j="0" nom="Cotes d'Armor"/>
                <ille-vilaine ind_j="0" nom="Ille-et-Vilaine"/>
            </departements>
        </jour>
    </indicesQA>
 
    '''
    root = ET.Element('indicesQA')
        
    # XML pour la date du jour : term 0 (aujourd'hui)
    jour = ET.SubElement(root,'jour')
    term = ET.SubElement(jour,'date')
    villes  = ET.SubElement(jour,'villes')
    departs = ET.SubElement(jour,'departements')
    term.text  = date

    for v in VILLES.keys():
        n = VILLES[v]
        c = INSEE[v]
        id = ID[v]
    	try: 
            a, d = valid(indices[v])
            aSO2 = valid(ssindices[v+'_01'])[0]
            aNO2 = valid(ssindices[v+'_03'])[0]
            aO3 = valid(ssindices[v+'_08'])[0]
            aPM10 = valid(ssindices[v+'_24'])[0]
            ville = ET.SubElement(villes, "ville")
            ville.set('nom', n)
            ville.set('id', id)
            ville.set('code_insee', c)
            ville.set('ind_j', a)
            ville.set('ssind_j_%s'%POLLUANT['01'], aSO2)
            ville.set('ssind_j_%s'%POLLUANT['03'], aNO2)
            ville.set('ssind_j_%s'%POLLUANT['08'], aO3)
            ville.set('ssind_j_%s'%POLLUANT['24'], aPM10) 
        except:
            pass


    for v in DEPARTEMENTS.keys():
        n = DEPARTEMENTS[v]
        nb = DEPARTEMENTS_BALISE[v]
    	try: 
            a, d = valid(indices[v])
            aSO2 = valid(ssindices[v+'_01'])[0]
            aNO2 = valid(ssindices[v+'_03'])[0]
            aO3 = valid(ssindices[v+'_08'])[0]
            aPM10 = valid(ssindices[v+'_24'])[0]
            depart = ET.SubElement(departs, nb)
            depart.set('nom', n)
            depart.set('ind_j', a)
        except:
            pass

    # XML pour la date du jour : term +1 (demain)
    jour = ET.SubElement(root,'jour')
    term = ET.SubElement(jour,'date')
    villes  = ET.SubElement(jour,'villes')
    departs = ET.SubElement(jour,'departements')
    today = time.strptime(date,FORMAT)
    demain = dt.datetime.fromtimestamp(mktime(today))+dt.timedelta(days=1)
    term.text = demain.strftime(FORMAT)
    # demain = dt.datetime(*time.strptime(date,"%Y-%m-%d")[0:6]) + relativedelta(days=1)
    # term.text = demain.strftime('%Y-%m-%d')

    for v in VILLES.keys():
        n = VILLES[v]
        c = INSEE[v]
        id = ID[v]
    	try: 
            a, d = valid(indices[v])
            ville = ET.SubElement(villes, "ville")
            ville.set('nom', n)
            ville.set('id', id)
            ville.set('code_insee', c)
            ville.set('ind_j', d)
        except:
            pass

    for v in DEPARTEMENTS.keys():
        n = DEPARTEMENTS[v]
        nb = DEPARTEMENTS_BALISE[v]
    	try: 
            a, d = valid(indices[v])
            depart = ET.SubElement(departs, nb)
            depart.set('nom', n)
            depart.set('ind_j', d)  
        except:
            pass


    tree = ET.ElementTree(root)

    try:
        tree.write(fichier)
        return fichier
    except Exception, e:
        print("Erreur sur enregistrement xml : %s"%e)
        return None


def indices(date):
    '''Recupère les indices et sous-indices ATMO à la date demandée
    return: liste de valeurs d'indices 

    @date (str): format "YYYY-MM-DD"
    '''
    #Connexion à la base XAIR
    try:
        conn = cx_Oracle.connect(ORA)
        cursor = conn.cursor()
    except cx_Oracle.Error, e:
        print("Echec de connection à la base : %s"%e)
        return None

    #Gestion des dates d'aujourd'hui et d'hier
    today = time.strptime(date,FORMAT)
    #hier =  dt.datetime.fromtimestamp(mktime(today)) - dt.timedelta(days=1)
    #hier = hier.strftime(FORMAT)

    #Récupération des numéros de ville (champ nom_court_group)
    grp = []
    for num_grp in VILLES.keys():
        grp.append( 'nom_court_grp=' + num_grp )
    for num_grp in DEPARTEMENTS.keys():
        grp.append( 'nom_court_grp=' + num_grp )
    grp = ' OR '.join( grp )
    
    
    #Requêtes SQL
    sql_ad = ''' SELECT nom_court_grp, p_ind_diffuse, p_ind_prv_j1
    FROM resultat_indice
    WHERE ( %s )
    AND j_date=TO_DATE('%s', 'YYYY-MM-DD') ''' % (grp, date)
    
    sql_ss_ind = ''' SELECT nom_court_grp, nopol, p_ss_indice_diff
    FROM resultat_ss_indice
    WHERE ( %s )
    AND j_date=TO_DATE('%s', 'YYYY-MM-DD') ''' % (grp, date)

    #Récupération des indices
    try:
        cursor.execute( sql_ad )
        vals_ad = cursor.fetchall()
        cursor.execute( sql_ss_ind )
        vals_ssind_a = cursor.fetchall()

        vals_ind = {}
        vals_ssind = {}
        
	for data in vals_ad:
            vals_ind[data[0]] = [data[1]]
            vals_ind[data[0]].extend([data[2]])
        for data in vals_ssind_a:
            vals_ssind[data[0]+'_'+data[1]] = [data[2]]

        return vals_ind, vals_ssind

    except Exception, e:
        print("Erreur sur obtention des valeurs : %s"%e)
        return None

    cursor.close()
    conn.close()


def upload(fichier):
    '''
    Envoi du fichier xml sur un serveur FTP Netlim
    '''
    path, name = os.path.split(fichier)
    try:
        ftp = ftplib.FTP(TARGET_URI, USER, PWD)
        fi = open(fichier, 'rb')
        ftp.storbinary('STOR ' + name[0:14]+'.xml', fi)
        fi.close()
        ftp.close()
        return fichier
    except Exception, e:
        print("Erreur sur envoi du fichier : %s" %e)
        return None



#-------------------------------------------------------------------#
#------------------------ MAIN -------------------------------------#
#-------------------------------------------------------------------#


if __name__ == "__main__":
    
    # Initialisation
    date = dt.datetime.today().strftime(FORMAT)
    fichier = XML%date
    
    # Extraction des indices
    ind, ssind = indices(date)
    if ind is None: sys.exit(1)

    # Création du xml
    fichier = ind2xml(date, ind, ssind, fichier)
    if fichier is None: sys.exit(1)
    
    # # Dépose du xml sur ftp
    fichier = upload(fichier)
    if fichier is None: sys.exit(1)

    print("INFO - %s - Export des indices sur FTP : OK" %date)

    # Suppression du xml si GARDE = False
    if GARDE is False:
        os.remove(fichier)
        print('INFO - Suppression du fichier XML après dépose sur le FTP')
    
    sys.exit(0)

