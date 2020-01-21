#!/usr/bin/env python
# coding: utf-8

# # Part 3 - Analyse

# In[77]:


import pandas as pd


# In[216]:


import matplotlib as mpl


# In[219]:


from matplotlib import pyplot


# In[270]:


class Analyzer:
    '''
    Class representing analyzed data attained from previous parts with attributes and methods used for analysis.
    '''
    def __init__(self, allowLog = True):
        '''
        Initilization of Downloader object. Storing objects from the webpage with self.qwe, self.rty and self.uio
        '''
        self.allowLog = allowLog
        if self.allowLog:
            print('Analyzer initialized.')    
    
    def dataLoader(self, df, whatData = 'GeoTopArtists'):
        '''
        Loads the processed data from previous parts.
        '''
        self.df = df        
        if whatData == 'GeoTopArtists':
            print('Data loaded.')
        elif whatData == 'GeoTopTracks':
            self.whatData = 'GeoTopTracks'
            print('Data loaded.')
        elif whatData == 'ArtistInfo':
            self.whatData = 'ArtistInfo'
            print('Data loaded.')
        else:
            print('I cannot recognize the type of data you want to pass. Select please from one of the following: \n\"GeoTopArtists\" \n\"GeoTopTracks\" \n\"ArtistInfo\" \nThank you very much!')
                 
    
    def showMeTheTopArtists(self, N, sortBy  = 'Scrobbles'):
        '''
        Shows the most N scrobbled artist, or the artist with the highest number of listeners.
        '''
        self.df['Scrobbles per Listener'] = self.df['Scrobbles'] / self.df['Listeners']
        
        if sortBy == 'Listeners':
            return self.df.sort_values(by = ['Listeners'], ascending = False)[['Artist', 'Listeners', 'Scrobbles', 'Scrobbles per Listener']].head(N)
        elif sortBy == 'Scrobbles':
            return self.df.sort_values(by = ['Scrobbles'], ascending = False)[['Artist', 'Listeners', 'Scrobbles', 'Scrobbles per Listener']].head(N)
        elif sortBy=='SpL':                
            return self.df.sort_values(by = ['Scrobbles per Listener'], ascending = False)[['Artist', 'Listeners', 'Scrobbles', 'Scrobbles per Listener']].head(N)
        else:
            return print('Unfortunately couldn\'t sorted the dataframe as you wish. Please choose one of the following:\n"Scrobbles"\n"Listeners"\n"SpL"\nThank you!')
    
    def plotIt(self, whatToPlot, byWhat = 'Scrobbles'):
        '''
        Creates the basic Bar plot of listeners for a given set.
        '''
        if byWhat == 'SpL':
            byWhat = 'Scrobbles per Listener'
        plot1 = whatToPlot.sort_values(by = byWhat)
        return pyplot.barh(plot1['Artist'], width = plot1[byWhat], align = 'center')
        
    def showMeCountrySpecifics(self, cntry, typ = 'Artist'):
        '''
        Shows the specific values (Artist or Tracks) which appear in Top 100 only in one country.
        '''
        cA = self.df[self.df['Country'] == cntry ][typ]
        nonCA = self.df[self.df['Country'] != cntry ][typ]
        for a in list(cA):
            if a in list(nonCA):
                pass
            else:
                print(a)
        


# In[271]:


df = pd.read_csv('artist_info.csv', sep = ',')
df = df.drop(columns = ['Unnamed: 0'], axis = 1)
df.head()


# In[272]:


newA = Analyzer()
newA.dataLoader(df,'ArtistInfo')


# ## Some of the basic statistics and interesting results

# In previous parts we processed the data of approximately 1200 most listened artists on the platform. We are going to use them for some basic analysis.

# We firstly introduce the chart of the top 20 artist based on the scrobbles (i.e. number of played songs from the artists by users of Last.fm).

# In[273]:


newA.showMeTheTopArtists(20)


# In[274]:


newA.plotIt(whatToPlot = newA.showMeTheTopArtists(20), byWhat = 'Scrobbles')


# The Beatles are the winners in the category of most scrobbled artist with over the half of a billion scrobbled tracks, followed by Radiohead and Coldplay. Interesting result is that The Beatles have approximately 3.75 million listeneres whereas Coldplay on the third place have almost 5.5 million listeners. We will see that Coldplay is the winner in the second category where the ranking follows from the number of listeners.

# We follow by top 20 artists sorted by number of listeners (i.e. the number of users of Last.fm, who had at least once listened to a song from this artist).

# In[275]:


newA.showMeTheTopArtists(N = 20, sortBy = 'Listeners')


# In[276]:


newA.plotIt(whatToPlot = newA.showMeTheTopArtists(20, sortBy = 'Listeners'), byWhat = 'Listeners')


# Coldplay, Radiohead and Red Hot Chili Peppers are on the first three positions, but The Beatles dropped to 18th position. As we can see they have much higher Scrobble per (average) Listener ratio than the rest of the Top 20 (only them and Radiohead reached over the 100 Scrobbles per Listener).

# Motivated by these differences we started looking for the bands with the most "devoted" fans, i.e. we plot the Top 20 artists with highest scrobbles per listener ratio.

# In[277]:


newA.showMeTheTopArtists(N = 20, sortBy = 'SpL')


# In[278]:


newA.plotIt(whatToPlot = newA.showMeTheTopArtists(20, sortBy = 'SpL'), byWhat = 'SpL')


# From the first two charts only Beatles, Radiohead and Lana Del Rey stayed in a Top 20 Scrobbles per Listener artist. The band BTS on the first position has extremely large value indicating that great portion of the listeners of BTS listens to this band quite a lot.
# 
# It is worth mentioning that these statistics don't fully describe the mentioned property of "devoted" fans, since the unit measured (scrobbles) is highly influenced by length of songs of the interpret. The outlier in the last statistic (band BTS) has in average much shorter songs than e.g. Pink Floyd which are (at the time of writing this note) on the 22nd position. Since one scrobble of a song is typically assigned if a listener has listened through at least half of the song or at least 4 minutes of the track, if one song is approximately 3 or 4 minutes long, it suffices to get a scrobble after listening through approximately minute and a half or 2 minutes, whereas if the lenght of songs is on average longer (as is for Pink Floyd or most of the post-rock, classical etc. interprets), one scrobble is counted after longer period of time. Shorter/longer songs also plays a role in a number of songs on the album, and hence the number of songs overall.
# 
# __Interesting notes__: 
# * The Slovakian band Horkýže Slíže is on the 9th position in the overall list.
# * Four of the Top 5 bands originate in Southeast Asia.

# ## Which interpret is in Top 100 in only one (chosen) country?

# In[157]:


df2 = pd.read_csv('geo_top_artists_101.csv', sep = ',')
df2.head()
geoArt = Analyzer()
geoArt.dataLoader(df2, 'GeoTopArtists')


# We use the method _showMeCountrySpecifics_ to see the country specific artists, i.e. these which appear only in top chart for a given country.

# In[158]:


geoArt.showMeCountrySpecifics('Czechia')


# In[159]:


geoArt.showMeCountrySpecifics('Slovakia')


# In[160]:


geoArt.showMeCountrySpecifics('Viet Nam')


# In[281]:


geoArt.showMeCountrySpecifics('Iraq')


# In[282]:


geoArt.showMeCountrySpecifics('Greenland')


# # Which song is in Top 100 in only one (chosen) country?

# In[163]:


df3 = pd.read_csv('geo_top_tracks_101.csv', sep = ',')
df3 = df3.drop(columns = ['Unnamed: 0'], axis = 1)
df3['ArtistTrack'] = df3['Artist'] + ' - '+ df3['Track']
geoTrack = Analyzer()
geoTrack.dataLoader(df3, 'GeoTopTracks')
df3.head()


# In[170]:


geoTrack.showMeCountrySpecifics('Czechia', typ = 'ArtistTrack')


# In[171]:


geoTrack.showMeCountrySpecifics('Slovakia', typ = 'ArtistTrack')


# Unfortunately no specific song is either for Czech Republic or for Slovakia.

# In[173]:


geoTrack.showMeCountrySpecifics('Viet Nam', typ = 'ArtistTrack')


# In[184]:


geoTrack.showMeCountrySpecifics('Iraq', typ = 'ArtistTrack')


# In[280]:


geoTrack.showMeCountrySpecifics('Greenland', typ = 'ArtistTrack')

