#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re


# In[55]:


from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image


# # Visualising the frequency of tags
# 
# We were able to gather more than 10 000 tags of 2135 most popular artists around the globe (5 tags per artist). With these tags, we have decided to visualise the frequency of the tags by constructing a word cloud. Rock, pop & hip-hop artists seem to be the favourites of the LastFM community.
# 

# In[4]:


df = pd.read_csv('artist_info_101.csv')


# In[9]:


tags = pd.concat([df.Tag1, df.Tag2, df.Tag3, df.Tag4, df.Tag5])


# In[68]:


# Lower case all tags and replace '-' with a space in case of duplicated tags, e.g. hip-hop vs. hip hop
tags = [x.lower() for x in tags]
tags = [re.sub('\-', ' ', str(x)) for x in tags]


# In[29]:


text = ','.join(tag for tag in tags)


# In[66]:


# Creation of a word cloud
mask = np.array(Image.open(r'lastfmlogo.png'))
image_colors = ImageColorGenerator(mask)

wordcloud = WordCloud(max_font_size=60, scale = 3, background_color="white").generate(text)
plt.figure(figsize=(50,30))#
plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
plt.axis("off")
plt.show()

