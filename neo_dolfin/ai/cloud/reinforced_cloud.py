import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

# Download necessary NLTK data
nltk.download('stopwords')
nltk.download('wordnet')

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Tokenization
    words = text.split()
    # Remove stopwords and lemmatize
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stopwords.words('english')]
    return ' '.join(words)

class WordCloudGenerator:
    def __init__(self, width=800, height=400, background_color='white'):
        self.width = width
        self.height = height
        self.background_color = background_color

    def create_word_cloud(self, descriptions, amounts=None, mode='count', preprocess=False):
        if preprocess:
            descriptions = [preprocess_text(description) for description in descriptions]
        if mode == 'amount' and amounts is not None:
            frequency = Counter()
            for description, amount in zip(descriptions, amounts):
                frequency[description] += amount
        else:
            frequency = Counter(descriptions)
        wordcloud = WordCloud(width=self.width, height=self.height, background_color=self.background_color).generate_from_frequencies(frequency)
        return wordcloud

def visualize_word_clouds(word_clouds, titles, figsize=(20, 10)):
    if len(word_clouds) != len(titles):
        raise ValueError("The number of word clouds and titles must be the same.")

    num_clouds = len(word_clouds)
    fig, axs = plt.subplots(num_clouds, 1, figsize=figsize, squeeze=False)
    axs = axs.flatten()

    for idx, (word_cloud, title) in enumerate(zip(word_clouds, titles)):
        axs[idx].imshow(word_cloud, interpolation='bilinear')
        axs[idx].axis('off')
        axs[idx].set_title(title)

    plt.tight_layout()
    plt.show()

# Function to read data from a CSV file and extract the descriptions
def read_data_from_csv(csv_filename, text_column='description'):
    df = pd.read_csv(csv_filename)
    return df[text_column].dropna().tolist()  # Drop NaN values

# Main execution
if __name__ == "__main__":
    # Since the CSV file is in the same directory, we can just use the filename
    csv_filename = '../../static/data/cloud.csv'

    # Read descriptions from the CSV file
    descriptions = read_data_from_csv(csv_filename)

    # Generate and visualize the word cloud
    generator = WordCloudGenerator()
    wordcloud = generator.create_word_cloud(descriptions, preprocess=True)
    visualize_word_clouds([wordcloud], ['Word Cloud from CSV Data'])
