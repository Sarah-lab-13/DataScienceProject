## Classes and functions

import difflib as dl
import pandas as pd
from thefuzz import process, fuzz 


class Extractor:
    def __init__(self, start_string, start_tag, end_string, end_tag, place_tag):
        self.start_string = start_string
        self.start_tag = start_tag
        self.end_string = end_string
        self.end_tag = end_tag
        self.place_tag = place_tag
        self.should_start_parsing = False
        self.text_list = list()
        self.tag_list = list()

    def extract_text_and_tags(self, soup):
        for line in soup.find_all('l'):
            if line.string == self.start_string and line.string.parent.name == self.start_tag:
                self.should_start_parsing = True  

            if self.should_start_parsing:
                text = line.get_text()
                self.text_list.append(text)
                for child in line.descendants:
                    if child.name == self.place_tag:
                        for place in child.strings:
                            self.tag_list.append(place)          

            if line.string == self.end_string and line.string.parent.name == self.end_tag:
                self.should_start_parsing = False  
                break 

def structure(tag_list):
    while(" " in tag_list):
        tag_list.remove(" ")

    clean_places = []
    for e in tag_list:
        if clean_places and clean_places[-1].endswith('='):
            clean_places[-1] = clean_places[-1][:-1] + e
        elif clean_places and (clean_places[-1].endswith('des ') or clean_places[-1].endswith('des')):
            clean_places[-1] = clean_places[-1] + ' ' + e
        elif clean_places and (clean_places[-1].endswith('der ') or clean_places[-1].endswith('der')): 
            clean_places[-1] = clean_places[-1] + ' ' + e     
        elif clean_places and clean_places[-1].endswith('den '): 
            clean_places[-1] = clean_places[-1] + ' ' + e 
        elif clean_places and (clean_places[-1].endswith('Fürsten ') or clean_places[-1].endswith('.')):
            clean_places[-1] = clean_places[-1] + ' ' + e         
        else:
            clean_places.append(e)
    return clean_places


def matcher(clean_places):
    similiar_words = []
    place_list = []

    while len(place_list) != len(clean_places):
        for word in clean_places:
            close_words = dl.get_close_matches(word, clean_places, cutoff= 0.9)     
            similiar_words.append(close_words)                                      
        
        for sublist in similiar_words:     
            sublist = sorted(sublist)
            place = sublist[0]
            place_list.append(place)  
    if len(place_list) == len(clean_places):
        return place_list
    

def Kulturwiki_comparer(place_list): 
    usecolumns = ['OBJECTID', 'SHAPE', 'ADRESSE', 'SEITENNAME']
    coordinates = pd.read_csv("../Data/KULTURWIKIOGD.csv",  index_col="OBJECTID", usecols=usecolumns)  
 
    coordinates['MATCH_SCORE'] = coordinates['SEITENNAME'].apply(lambda x: process.extractOne(x, place_list, scorer=fuzz.ratio)[1]) 
    coordinates['NEUE_NAMEN'] = coordinates['SEITENNAME'].apply(lambda x: process.extractOne(x, place_list, scorer=fuzz.ratio)[0])

    coordinates = coordinates.sort_values('MATCH_SCORE', ascending=False) 
    return coordinates


def Kulturwiki_indexer(coordinates_choice, place_list):
    coordinates_choice = coordinates_choice.drop_duplicates(subset=['NEUE_NAMEN']) 
    place_coord  = coordinates_choice.drop(columns = ['SEITENNAME', 'MATCH_SCORE']) 

    place_coord = place_coord.set_index('NEUE_NAMEN')  
    place_coord = place_coord.reindex(index=place_list) 
    place_coord = place_coord.reset_index() 
    place_coord.reset_index(inplace=True)
    place_coord = place_coord.drop(columns=['index'])
    return place_coord    


def Steinhausen_comparer(place_list):
    usecolumns = ['ID_neu', 'Toponym', 'Longitude', 'Latitude']
    Steinhausen_coordinates = pd.read_excel("../Data/Gazetteer_Steinhausenplan_V5.xlsx", usecols=usecolumns, index_col=0)  

    Steinhausen_coordinates['MATCH_SCORE'] = Steinhausen_coordinates['Toponym'].apply(lambda x: process.extractOne(x, place_list, scorer=fuzz.ratio)[1])
    Steinhausen_coordinates['NEUE_NAMEN'] = Steinhausen_coordinates['Toponym'].apply(lambda x: process.extractOne(x, place_list, scorer=fuzz.ratio)[0])
    Steinhausen_coordinates = Steinhausen_coordinates.sort_values('MATCH_SCORE', ascending=False)
    return Steinhausen_coordinates


def Steinhausen_indexer(Steinhausen_coordinates, place_list):
    Steinhausen_choice = Steinhausen_coordinates.drop_duplicates(subset=['NEUE_NAMEN'])

    Steinhausen_choice = Steinhausen_choice.set_index('NEUE_NAMEN')
    Steinhausen_choice = Steinhausen_choice.reindex(index=place_list)
    Steinhausen_choice = Steinhausen_choice.reset_index()
    Steinhausen_choice.reset_index(inplace=True)
    Steinhausen_choice = Steinhausen_choice.drop(columns=['index', 'MATCH_SCORE', 'Toponym'])
    return Steinhausen_choice
              

def table_comparer(coord_table):
    Sunday_gold_table = pd.read_excel("../Data/Sonntag/joined_Sonntag_coord_nn.xlsx", index_col=0)   
    Monday_gold_table = pd.read_excel("../Data/Montag/joined_Montag_coord_nn.xlsx", index_col=0)
    Tuesday_gold_table = pd.read_excel("../Data/Dienstag/joined_Dienstag_coord_nn.xlsx", index_col=0)
    Thursday_gold_table = pd.read_excel("../Data/Donnerstag/joined_Donnerstag_coord_nn.xlsx", index_col=0)

    matches_sun = coord_table.merge(Sunday_gold_table, left_on='NEUE_NAMEN_x', right_on='NEUE_NAMEN').drop('NEUE_NAMEN', axis='columns')
    matches_mon = coord_table.merge(Monday_gold_table, left_on='NEUE_NAMEN_x', right_on='NEUE_NAMEN').drop('NEUE_NAMEN', axis='columns')
    matches_tues = coord_table.merge(Tuesday_gold_table, left_on='NEUE_NAMEN_x', right_on='NEUE_NAMEN').drop('NEUE_NAMEN', axis='columns')
    matches_thur = coord_table.merge(Thursday_gold_table, left_on='NEUE_NAMEN_x', right_on='NEUE_NAMEN').drop('NEUE_NAMEN', axis='columns')

    return matches_sun, matches_mon, matches_tues, matches_thur
