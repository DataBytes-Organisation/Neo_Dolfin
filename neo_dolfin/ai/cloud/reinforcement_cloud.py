import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

df = pd.read_csv('../../static/data/cloud.csv')

def create_word_cloud(descriptions, amounts=None, mode='count'):
    if mode == 'amount' and amounts is not None:
        frequency = Counter()
        for description, amount in zip(descriptions, amounts):
            frequency[description] += amount
    else:
        frequency = Counter(descriptions)

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(frequency)
    return wordcloud

low_expenditure_df = df[df['Expenditure Level'] == 'Low Expenditure']
medium_expenditure_df = df[df['Expenditure Level'] == 'Medium Expenditure']
high_expenditure_df = df[df['Expenditure Level'] == 'High Expenditure']

low_word_cloud_count = create_word_cloud(low_expenditure_df['description'], mode='count')
medium_word_cloud_count = create_word_cloud(medium_expenditure_df['description'], mode='count')
high_word_cloud_count = create_word_cloud(high_expenditure_df['description'], mode='count')

low_word_cloud_amount = create_word_cloud(low_expenditure_df['description'], low_expenditure_df['amount'], mode='amount')
medium_word_cloud_amount = create_word_cloud(medium_expenditure_df['description'], medium_expenditure_df['amount'], mode='amount')
high_word_cloud_amount = create_word_cloud(high_expenditure_df['description'], high_expenditure_df['amount'], mode='amount')


fig, axs = plt.subplots(6, 1, figsize=(20, 40))  

axs[0].imshow(low_word_cloud_count, interpolation='bilinear')
axs[0].axis('off')
axs[0].set_title('Low Expenditure Word Cloud (Count)')

axs[1].imshow(medium_word_cloud_count, interpolation='bilinear')
axs[1].axis('off')
axs[1].set_title('Medium Expenditure Word Cloud (Count)')

axs[2].imshow(high_word_cloud_count, interpolation='bilinear')
axs[2].axis('off')
axs[2].set_title('High Expenditure Word Cloud (Count)')

axs[3].imshow(low_word_cloud_amount, interpolation='bilinear')
axs[3].axis('off')
axs[3].set_title('Low Expenditure Word Cloud (Amount)')

axs[4].imshow(medium_word_cloud_amount, interpolation='bilinear')
axs[4].axis('off')
axs[4].set_title('Medium Expenditure Word Cloud (Amount)')

axs[5].imshow(high_word_cloud_amount, interpolation='bilinear')
axs[5].axis('off')
axs[5].set_title('High Expenditure Word Cloud (Amount)')

plt.tight_layout()
plt.show()

