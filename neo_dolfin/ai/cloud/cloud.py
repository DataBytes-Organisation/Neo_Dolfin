import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

df = pd.read_csv('../../static/data/cloud.csv')


def create_word_cloud(descriptions):
    frequency = Counter(descriptions)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(frequency)
    return wordcloud


low_expenditure_df = df[df['Expenditure Level'] == 'Low Expenditure']
medium_expenditure_df = df[df['Expenditure Level'] == 'Medium Expenditure']
high_expenditure_df = df[df['Expenditure Level'] == 'High Expenditure']

low_word_cloud = create_word_cloud(low_expenditure_df['description'])
medium_word_cloud = create_word_cloud(medium_expenditure_df['description'])
high_word_cloud = create_word_cloud(high_expenditure_df['description'])

fig, axs = plt.subplots(3, 1, figsize=(20, 20))

axs[0].imshow(low_word_cloud, interpolation='bilinear')
axs[0].axis('off')
axs[0].set_title('Low Expenditure Word Cloud')

axs[1].imshow(medium_word_cloud, interpolation='bilinear')
axs[1].axis('off')
axs[1].set_title('Medium Expenditure Word Cloud')

axs[2].imshow(high_word_cloud, interpolation='bilinear')
axs[2].axis('off')
axs[2].set_title('High Expenditure Word Cloud')

plt.tight_layout()
plt.show()
