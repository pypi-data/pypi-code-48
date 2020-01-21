#!/usr/bin/env python
# coding: utf-8

# # Part 4 - Visualise

# In[1]:


import os


# In[2]:


import pandas as pd


# In[3]:


import folium


# In[4]:


import geopandas as gpd


# In[5]:


import webbrowser


# In[6]:


import geojson


# In[7]:


import json


# In[8]:


from IPython.display import display


# In[9]:


class Visualise:
    '''
    Class representing processed data from previous parts with attributes and methods to make geo-visualisations.
    '''
    def __init__(self, allowLog = True):
        '''
        Initilization of Downloader object. Storing objects from the webpage with self.qwe, self.rty and self.uio
        '''
        self.allowLog = allowLog
        if self.allowLog:
            print('Object of data initialized.')    
            
    def countriesPolygon(self, geoDf):
        '''
        Pandas GeoDataframe containing the (multi-)polygons of countries.
        '''
        self.geoDf = geoDf
    
    def foliumMap(self, m = folium.Map(location=[51.05, 5.86],zoom_start=3)):
        '''
        Map from library Folium.
        '''
        self.m = m         
    
    def countriesDict(self, dct):
        '''
        Dictionary for different naming conventions of countries in the World
        '''
        self.dct = {}
        for name, name2 in zip(dct['NAME'], dct['GEONAME']):
            self.dct[name] = name2
        #return self.dct
        # now the special care for a country with symbol ' in its name
        self.dct['Cote D\'Ivoire'] = 'Ivory Coast'
        self.data = self.data.replace(dct)
        
    def loadTheData(self, data, whatData = 'GeoTopArtist'):
        '''
        Loader of the data. First argument is the data provided, second is specification about what type of data it is.
        '''
        self.data = data
        self.whatData = whatData
        if whatData == 'GeoTopArtist':
            pass
        elif whatData == 'GeoTopTracks':
            pass
        elif whatData == 'ArtistInfo':
            pass
        else:
            return(print('I cannot recognize the type of data you want to pass. Select please from one of the following: \n\"GeoTopArtist\" \n\"GeoTopTracks\" \n\"ArtistInfo\" \nThank you very much!'))
        
    def showMeTopN(self, N = 10, whichOnes = 'Artists' ):
        '''
        Method which computes the top N artists for all countries contained in the scraped data.
        '''
        boundary = self.data['Rank'] <= N
        self.data = self.data.replace(self.dct)
        self.cols = ['Top ' + str(i+1) for i in range(N)]
        self.whichOnes = whichOnes
        if whichOnes == 'Artists':
            for i in range(N):
                self.geoDf['Top '+ str(i+1)] = str(None)
            self.topNArtists = self.data[boundary]
            for cntry in self.topNArtists['Country']:
                for i in range(N):
                    try:
                        self.geoDf['Top ' + str(i+1)][self.geoDf['ADMIN']==cntry] = self.topNArtists[self.topNArtists['Country']==cntry][self.topNArtists['Rank']==i+1]['Artist'].item()
                    except:
                        pass
            return self.geoDf                               
        elif whichOnes == 'Tracks':
            for i in range(N):
                self.geoDf['Top '+ str(i+1)] = str(None)
            self.topNTracks = self.data[boundary]    
            for cntry in self.topNTracks['Country']:
                for i in range(N):
                    try:
                        self.geoDf['Top ' + str(i+1)][self.geoDf['ADMIN']==cntry] = self.topNTracks[self.topNTracks['Country']==cntry][self.topNTracks['Rank']==i+1]['ArtistTrack'].item() 
                    except:
                        pass
            return self.geoDf
        else:
            return(print('I cannot show you what you want..probably. Select please from one of the following: \n"Artists" \n"Tracks" \nThank you very much!'))
    
    def saveAndShowMap(self, m, df):
        '''
        Method to save and show the map of top artists or tracks. The map is saved as 'plotTheMap.html' file which is shown in a new window.
        '''
        folium.GeoJson(
                df[['ADMIN', 'geometry'] + self.cols].to_json(),
                show=True,
                tooltip=folium.features.GeoJsonTooltip(
                fields=['ADMIN'] + self.cols,
                aliases=['Country'] + self.cols)
            ).add_to(m)
        if self.whichOnes == 'Tracks':
            self.m.save('plotTheTrackMap.html')
            webbrowser.open_new('plotTheTrackMap.html')
        else:
            self.m.save('plotTheArtistMap.html')
            webbrowser.open_new('plotTheArtistMap.html')


# In[10]:


with open('countries.geojson', 'r') as f:
    data = geojson.load(f)


# In[11]:


with open('countries_cut_two.csv', 'r') as c:
    cntrsDict = pd.read_csv(c, sep = ';')


# In[26]:


topArtists = pd.read_csv('geo_top_artists_101.csv', sep = ',')
topArtists = topArtists.drop(columns = ['Unnamed: 0'])
topArtists.head()


# In[13]:


artistViz = Visualise()
artistViz.foliumMap()
artistViz.countriesPolygon(gpd.GeoDataFrame.from_features(data))
artistViz.loadTheData(topArtists) 
artistViz.countriesDict(cntrsDict)


# Unfortunately the map cannot be displayed in Jupyter notebook, but with help of webbrowser library, we can save the output as html file and open it in a new window.

# In[14]:


artistViz.showMeTopN(N = 5, whichOnes = 'Artists')
artistViz.saveAndShowMap(artistViz.m,artistViz.geoDf)


# In[28]:


topTracks = pd.read_csv('geo_top_tracks_101.csv', sep = ',')
topTracks = topTracks.drop(columns = ['Unnamed: 0'])
topTracks['ArtistTrack'] = topTracks['Artist'] + ' - ' + topTracks['Track']
topTracks.head()


# In[16]:


tracksViz = Visualise()
tracksViz.foliumMap()
tracksViz.countriesPolygon(gpd.GeoDataFrame.from_features(data))
tracksViz.loadTheData(topTracks) 
tracksViz.countriesDict(cntrsDict)


# Similarily as above: the map cannot be displayed in Jupyter notebook, but with help of webbrowser library, we can save the output as html file and open it in a new window.

# In[17]:


tracksViz.showMeTopN(N = 5, whichOnes = 'Tracks')
tracksViz.saveAndShowMap(tracksViz.m,tracksViz.geoDf)


# ---
