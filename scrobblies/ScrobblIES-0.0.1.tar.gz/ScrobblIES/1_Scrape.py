#!/usr/bin/env python
# coding: utf-8

# In[437]:


import requests
import pandas as pd
import numpy as np
import json
import re


# In[17]:


from pathlib import Path
import requests_cache
import time
from IPython.core.display import clear_output


# In[18]:


## Please insert your API key into the configuration file in order to access LastFM public API
cwd = Path.cwd()
path_to_config = cwd / "Inputs/configpp.yml"


# In[412]:


#Loading config file

import yaml
with open(path_to_config, 'r') as ymlfile:
    config = yaml.load(ymlfile)


# In[413]:


#API key extraction
apikey = config['lastfm'].get('apikey')


# In[414]:


# Countries dataframe
countriesdf = pd.read_csv("countries_cut_one.csv", sep =";", encoding='latin-1')
countriesdf.columns = ['CountryName', 'CountryNameUrl']
countriesdf['CountryId'] = range(1, countriesdf.shape[0] + 1)
countriesdf = countriesdf[['CountryId', 'CountryName', 'CountryNameUrl']]


# # LastFMLink object

# In[417]:


# LastFMLink object

class LastFMLink:
    '''
    LastFM object working with LastFM API accessible links. API key has to be provided.
    '''
    
    
    def __init__(self, apikey, format = 'json', limit = 50):
        self.apikey = apikey
        self.limit = limit
        if format == 'json':
            self.format = 'json'
    
    
    def GeoGetTop(self, method = 'artist', countries = 'Czech+republic'):
        '''
        Obtain links containing info about most popular artists/tracks in given countries. 
        Countries: A list of country names, as defined by the ISO 3166-1 country names standard, multi-word names shall be seperated by '+'.
        Method: Either 'artist' or 'track' in order to obtain most popular artists or tracks in given countries.
        '''
        if method == 'artist':
            self.method = 'geo.gettopartists'
            if self.format == 'json':
                self.links = 'https://ws.audioscrobbler.com/2.0/?method=' + self.method + '&limit=' + str(self.limit) + '&country=' + countries + '&api_key=' + self.apikey + '&format=' + self.format
                return(self.links)
            
        elif method == 'track':
            self.method = 'geo.gettoptracks'
            if self.format == 'json':
                self.links = 'https://ws.audioscrobbler.com/2.0/?method=' + self.method + '&limit=' + str(self.limit) + '&country=' + countries + '&api_key=' + self.apikey + '&format=' + self.format
                return self.links  
            
        else:
            print('Choose either "artist" or "track" method, in order obtain most popular artists or tracks, respectively.')
    
    
    def ArtistGetInfo(self, artists = 'beach+house', autocorrect = 0):
        '''
        Obtain links containing info about given artists. Autocorrect transforms misspelled artist names into correct artist names, options are 1 for the enablement of autocorrect and 0 for otherwise.
        '''
        self.method = 'artist.getinfo'
        if self.format == 'json':
                self.links = 'https://ws.audioscrobbler.com/2.0/?method=' + self.method + '&limit=' + str(self.limit) + '&artist=' + artists + '&api_key=' + self.apikey + '&format=' + self.format + '&autocorrect=' + str(autocorrect)
                return self.links


# ## Creation of a dictionary containing links to jsonfiles

# In[418]:


# Links dictionary
last_fm_links = {'geo_top_artists': 0, 'geo_top_tracks': 0, 'artists_info': 0}


# In[419]:


# We would like 101 entries from each file
lnk = LastFMLink(apikey, limit = 101)


# In[420]:


# Creating links to access most popular artists and tracks on the country level
last_fm_links['geo_top_artists'] = lnk.GeoGetTop(countries = countriesdf['CountryNameUrl'], method = 'artist')
last_fm_links['geo_top_tracks'] = lnk.GeoGetTop(countries = countriesdf['CountryNameUrl'], method = 'track')


# In[436]:


class LastFMDownloader: 
    '''
    Downloader class for collection of data and storage of results.
    '''
    
    
    def __init__(self, allowLog = True):
        '''
        Initilization of Downloader object. API key has to be provided. 
        '''
        self.allowLog = allowLog
        self.limit = 50
        self.jsonlist = []
        if self.allowLog:
            print('Downloader initialized.')
    
    
    def LoadCountryList(self, countryid = 0, countryname = 'Czech Republic'):
        '''
        Specifies country id and country names of GetDfGeo methods.
        '''
        self.countryid = countryid
        self.countryname = countryname
    
    
    def RequestJson(self, links):
        '''
        Requests JSON files from given links and returns a list of JSON files stored in jsonlist attribute of the downloader.
        '''
        ## dodelat provide 1 link only
        requests_cache.install_cache() # storing previous requests
        number_of_files = len(links)
        self.jsonlist = []
        if len(links) >= 2:
            file = 1
            for link in links:
                print('Requesting file number {} out of {}'.format(file, number_of_files))
                clear_output(wait = True)
                jsonfile = requests.get(link).json()
                self.jsonlist.append(jsonfile)
                if not getattr(jsonfile, 'from_cache', False):
                    print('File has not been requested yet. Please wait half a second.')
                    time.sleep(0.25)
                file = file + 1
            clear_output(wait = True)
            print("All requested files are now available and stored in the 'jsonlist' attribute. Use one of the 'GetDf' methods to obtain the relevant data.")
        
    
    def GetDfGeoTopArtists(self): 
        '''
        Provides data concerning most popular artists in given countries stored in a pandas dataframe. 
        LoadCountryList() method has to be called before-hand, in order to specify id of countries and country names.
        '''
        ListGeoTopArtists = []
        for country in range(len(self.countryid)): # x number of countries range len countries
            bad_entry = 0
            for ranking in range(self.limit): # z number of ranks
                try:
                    row = []
                    rank = ranking + 1
                    countryid = self.countryid[country]
                    countryname = self.countryname[country]
                    artist = self.jsonlist[country]['topartists']['artist'][ranking]['name']
                    artistid = self.jsonlist[country]['topartists']['artist'][ranking]['mbid']
                    listeners = self.jsonlist[country]['topartists']['artist'][ranking]['listeners']
                    row.extend([countryid, countryname, rank, artist, artistid, listeners])
                    ListGeoTopArtists.append(row)
                except:
                    if bad_entry > 0:
                        break
                    else:
                        countryid = self.countryid[country]
                        countryname = self.countryname[country]
                        row = [countryid, countryname]
                        row.extend([None] * 4)
                        ListGeoTopArtists.append(row)
                        bad_entry = bad_entry + 1
        self.DfGeoTopArtists = pd.DataFrame.from_records(ListGeoTopArtists)
        self.DfGeoTopArtists.columns = ['CountryId', 'Country', 'Rank', 'Artist', 'ArtistId', 'Listeners']
        print("Data concerning most popular artists in given countries are now available and stored in 'DfGeoTopArtists' attribute as a pandas dataframe.")
        print("Here are last 5 entries of the dataframe:")
        return self.DfGeoTopArtists.tail()
    
    
    def GetDfGeoTopTracks(self): 
        '''
        Provides data concerning most popular tracks in given countries stored in a pandas dataframe. 
        LoadCountryList() method has to be called before-hand, in order to specify id of countries and country names.
        '''
        ListGeoTopTracks = []
        for country in range(len(self.countryid)): # x number of countries range len countries
            bad_entry = 0
            for ranking in range(self.limit): # z number of ranks
                try:
                    row = []
                    rank = ranking + 1
                    countryid = self.countryid[country]
                    countryname = self.countryname[country]
                    track = self.jsonlist[country]['tracks']['track'][ranking]['name']
                    duration = self.jsonlist[country]['tracks']['track'][ranking]['duration']
                    artist = self.jsonlist[country]['tracks']['track'][ranking]['artist']['name']
                    artistid = self.jsonlist[country]['tracks']['track'][ranking]['artist']['mbid']
                    row.extend([countryid, countryname, rank, track, duration, artist, artistid])
                    ListGeoTopTracks.append(row)
                except:
                    if bad_entry > 0:
                        break
                    else:
                        countryid = self.countryid[country]
                        countryname = self.countryname[country]
                        row = [countryid, countryname]
                        row.extend([None] * 5)
                        ListGeoTopTracks.append(row)
                        bad_entry = bad_entry + 1
        self.DfGeoTopTracks = pd.DataFrame.from_records(ListGeoTopTracks)
        self.DfGeoTopTracks.columns = ['CountryId', 'Country', 'Rank', 'Track', 'Duration', 'Artist', 'ArtistId']
        print("Data concerning most popular artists in given countries are now available and stored in 'DfGeoTopTracks' attribute as a pandas dataframe.")
        print("Here are last 5 entries of the dataframe:")
        return self.DfGeoTopTracks.tail()
    
    
    def GetDfArtistInfo(self): 
        '''
        Provides data concerning artists stored in a pandas dataframe. 
        '''
        ListArtistInfo = []
        for artist in range(len(self.jsonlist)): # x number of countries range len countries
            try:
                row = []
                artistname = self.jsonlist[artist]['artist']['name']
                listeners = self.jsonlist[artist]['artist']['stats']['listeners']
                playcount = self.jsonlist[artist]['artist']['stats']['playcount']
                tag1 = self.jsonlist[artist]['artist']['tags']['tag'][0]['name']
                tag2 = self.jsonlist[artist]['artist']['tags']['tag'][1]['name']
                tag3 = self.jsonlist[artist]['artist']['tags']['tag'][2]['name']
                tag4 = self.jsonlist[artist]['artist']['tags']['tag'][3]['name']
                tag5 = self.jsonlist[artist]['artist']['tags']['tag'][4]['name']
                try:
                    artistid = self.jsonlist[artist]['artist']['mbid']
                except:
                    artistid = ''
                row.extend([artistid, artistname, listeners, playcount, tag1, tag2, tag3, tag4, tag5])
                ListArtistInfo.append(row)
            except:
                pass
        self.DfArtistInfo = pd.DataFrame.from_records(ListArtistInfo)
        self.DfArtistInfo.columns = ['ArtistId', 'Artist', 'Listeners', 'Scrobbles', 'Tag1', 'Tag2', 'Tag3', 'Tag4', 'Tag5']
        print("Data concerning most popular artists in given countries are now available and stored in 'DfArtistInfo' attribute as a pandas dataframe.")
        print("Here are last 5 entries of the dataframe:")
        return self.DfArtistInfo.tail()


# tady pouzivam ty fajnovy veci co jsem si definoval nahore
# <br>
# <br>
# <br>
# <br>
# <br>
# <br>
# <br>

# In[422]:


dwn = LastFMDownloader(apikey)


# In[423]:


# Setting number of inputs per jsonfile to be the very same
dwn.limit = lnk.limit


# In[424]:


dwn.LoadCountryList(countryid = countriesdf['CountryId'], countryname = countriesdf['CountryName'])


# In[425]:


dwn.RequestJson(links = last_fm_links['geo_top_artists'])


# In[426]:


dwn.GetDfGeoTopArtists()


# In[427]:


dwn.RequestJson(links = last_fm_links['geo_top_tracks'])


# In[428]:


dwn.GetDfGeoTopTracks()


# In[ ]:





# In[429]:


# Creating links to access info about most popular artists on the global level
ArtistsArray = np.append(dwn.DfGeoTopArtists.Artist.unique().astype(str), dwn.DfGeoTopTracks.Artist.unique().astype(str))
ArtistsArray = np.unique(ArtistsArray)
ListOfArtistsUrl = [re.sub('\s+', '+', str(x)) for x in ArtistsArray]
last_fm_links['artists_info'] = LastFMLink(apikey).ArtistGetInfo(artists = pd.Series(ListOfArtistsUrl))


# In[431]:


dwn.RequestJson(links = last_fm_links['artists_info'])


# In[432]:


dwn.GetDfArtistInfo()


# In[434]:


# Saving all dataframes to csv
dwn.DfGeoTopTracks.to_csv('geo_top_tracks.csv', encoding='utf-8-sig')
dwn.DfGeoTopArtists.to_csv('geo_top_artists.csv', encoding='utf-8-sig')
dwn.DfArtistInfo.to_csv('artist_info.csv', encoding='utf-8-sig')


# In[ ]:




