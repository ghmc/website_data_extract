
import webbrowser,random,time,re,requests,os,zipfile,shutil
from pathlib import Path
from datetime import datetime,timedelta
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from threading import Thread
from multiprocessing import Process
import traceback

url = 'https://www.pass-education.fr/auth_telechargement.php?archive_id=165766&type_mime=application/zip&parent_id=165766'
# r= requests.get('https://www.pass-education.fr/lois-et-modeles-physique-chimie-premiere-s-1ere-s/')
# print (r.content.decode("utf-8",errors='ignore'))
# AAA (3 loops) --> 5eme --> mathematiques-5eme --> problemes-mathematiques-5eme
# download: #article\nid="post-YYYY"

'''
1- class="menu-arbo-sous-mat" href="/(xxxxx)-AAA/" --> xxxxx except: 
'''
exceptions = ['tdm', 
'clc-cours-lecons', 
'exo-exercice', 
'evb-evaluation-bilan', 
'evalcpt-evaluation-competence', 
'qcm-quiz',
'sfp-sequence-fiche-preparation',
'vid-video', 
'sdec-seance-decouverte',
'rtl-rituel',
'aff-affiche-classe',
'tss-question-reponse',
'ssc-soutien-scolaire',
'rcv-cahier-vacance', 
'clm-coloriage-magique',
'rcv-cahier-vacance-revision', 
'my-english-pass',  
'ief-ecole-a-la-maison-enseignement-a-distance-BBB',
'ctm-carte-mentale', 
'jeux-educatifs-en-ligne-AAA-jpd',
'themes/coloriage-gratuit-pdf-a-imprimer',
'AAA-jeux-educatifs-jpd']
 

 

#classes = ['ce2']
regex = re.compile("class\=\"menu-arbo-sous-mat\" href\=\"\/(.*)\/\"")
regexdwl = re.compile('article\nid\=\"post\-([0-9]{1,10})\".*\nhref\=\"https\:\/\/www\.pass\-education\.fr\/(.*)\/\"')


def filtering(exception:str, tobefiltered:list, classes:tuple):
    for classe in classes: 
        #print (f'classe {classe}, exception {exception}')
        if classe in tobefiltered:
            tobefiltered.remove(classe)  
        
    e=exception+'-'+classes[-1]
    if e in tobefiltered:
        tobefiltered.remove(e) 
     
    a_ = exception.replace('AAA', classes[-1])
    if a_ in tobefiltered:
        tobefiltered.remove(a_) 

    b_ =exception.replace('BBB', classes[0])
    if b_ in tobefiltered:
        tobefiltered.remove(b_) 

            
url = 'https://www.pass-education.fr/AAA/'        
urldwl = 'https://www.pass-education.fr/auth_telechargement.php?archive_id=AAA&type_mime=application/zip&parent_id=AAA'

def createfolderandgoin(hierarchy):
    p = Path('/'.join(hierarchy))
    p.mkdir(parents=True,  exist_ok=True) 
    return p.absolute()


hierarchy = []


def download(url):
 try:
    webbrowser.open(url, autoraise=True)   
 except:
    traceback.print_exc()
  


def sethierarchy(classe, subclasse, hierarchy):
    if not subclasse:
        hierarchy = [classe]
    else:
        index = hierarchy.index(subclasse)
        for _n in range(index,len(hierarchy)):
            hierarchy.pop(index)
        hierarchy = hierarchy+[subclasse, classe, ]

    return hierarchy



classes = ['ce2','cm1','cm2', '6eme', '5eme', '4eme', '3eme', 'seconde-2nde', 'premiere-1ere-s']

classes = ['5eme']

def unitloop(classes:list, subclasse:str=None, hierarchy=[]):
    for classe in classes:
        print (f'\nstart new theme {classe}')
        hierarchy = sethierarchy(classe, subclasse, hierarchy)
        #print (f'hierarchy {hierarchy}')
        dst = createfolderandgoin(hierarchy)
        #print (f'destination folder {dst}')
        urlloop = url.replace('AAA', classe)
        print (f'url {urlloop}')
        time.sleep(2)
        r = requests.get(urlloop)
        newclasses = regex.findall(r.content.decode("utf-8",errors='ignore'))
        #print (f'all sublinks without filter {newclasses}')
        for exception in exceptions : filtering(exception, newclasses, hierarchy)
        print (f'\nall sublinks with filter {newclasses}')
        if len(newclasses) == 0: 
            ccontent = r.content.decode("utf-8",errors='ignore')
            dwls = regexdwl.findall(ccontent)
            print (f'\nall downloads {dwls} ')
            for dwn in dwls:
                uur = urldwl.replace('AAA', str(dwn[0]))  
                download(uur)  
                length = 0
                starttime = time.time()
                while length == 0:
                    timespent = time.time() - starttime
                    time.sleep(1)
                    src = Path('c:/Users/bilel.benmakhlouf/Downloads').glob(dwn[1]+'.zip') 
                    lii = list(src)
                    length = len(lii)
                    if timespent > 5.0:
                        print (f'timeout zip download {uur}')
                        break
                
                else:
                    time.sleep(1)
                    zipfil = lii[0]
                    print (f'download ok, zip: {lii}')
                    with zipfile.ZipFile(zipfil, 'r') as zip_ref:
                        zip_ref.extractall(path=dst,members=list(filter(lambda x: x[-4::] == '.pdf', zip_ref.namelist())))
                        zip_ref.close()
                        length2 = 0
                        starttime = time.time()
                        while length2 == 0:
                            timespent = time.time() - starttime
                            time.sleep(1)
                            pdfs = dst.glob('*.pdf') 
                            lpdfs =list(pdfs)
                            length2 = len(lpdfs)
                            if timespent > 5.0:
                                print (f'timeout extract zip {zipfil} into {dst}')
                                break 
                        else:
                            nl = Path('c:/Users/bilel.benmakhlouf/Downloads').glob(dwn[1]+'.zip')
                            for l in list(nl):
                                try:
                                    os.remove(l)
                                    print (f'file {l} removed')
                                except:
                                    traceback.print_exc()
                
        
        else:
            unitloop(newclasses, classe, hierarchy)


unitloop(classes,None, hierarchy)
