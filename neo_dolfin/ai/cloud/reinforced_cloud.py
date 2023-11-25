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
    """
    Preprocesses the given text by converting to lowercase, removing punctuation,
    removing stopwords, and lemmatizing the words.

    Args:
    text (str): The text to preprocess.

    Returns:
    str: The preprocessed text.
    """
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
        """
        Initializes the WordCloudGenerator.

        Args:
        width (int): Width of the word cloud image. Default is 800.
        height (int): Height of the word cloud image. Default is 400.
        background_color (str): Background color of the word cloud image. Default is white.
        """
        self.width = width
        self.height = height
        self.background_color = background_color

    def create_word_cloud(self, descriptions, amounts=None, mode='count', preprocess=False):
        """
        Generates a word cloud image from the given descriptions.

        Args:
        descriptions (list of str): Descriptions to include in the word cloud.
        amounts (list of int/float, optional): Amounts corresponding to each description.
        mode (str): Mode of word cloud generation ('count' or 'amount').
        preprocess (bool): Whether to preprocess descriptions. Default is False.

        Returns:
        WordCloud: A WordCloud object.
        """
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
    """
    Visualizes a list of word clouds with their respective titles.

    Args:
    word_clouds (list of WordCloud): WordCloud objects to be visualized.
    titles (list of str): Titles for each WordCloud object.
    figsize (tuple): Size of the figure (width, height). Default is (20, 10).
    """
    if len(word_clouds) != len(titles):
        raise ValueError("The number of word clouds and titles must be the same.")

    num_clouds = len(word_clouds)
    fig, axs = plt.subplots(num_clouds, 1, figsize=figsize)
    
    for idx, (word_cloud, title) in enumerate(zip(word_clouds, titles)):
        axs[idx].imshow(word_cloud, interpolation='bilinear')
        axs[idx].axis('off')
        axs[idx].set_title(title)

    plt.tight_layout()
    plt.show()

# Example usage:
# generator = WordCloudGenerator()
# descriptions = ['your text data here']
# wordcloud = generator.create_word_cloud(descriptions, preprocess=True)
# visualize_word_clouds([wordcloud], ['Sample Word Cloud'])
