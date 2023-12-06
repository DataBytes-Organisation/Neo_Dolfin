from wordcloud import WordCloud
from collections import Counter
import re
import base64
from io import BytesIO
from flask import jsonify


def generate_word_cloud(data_with_level, level, mode='default', preprocess=True, whether_jsonify=True):
    """
    Generates a word cloud from the provided data, filtered by a specified level,
    and returns it either as a WordCloud object or as a JSON response with a base64-encoded image.

    :param data_with_level: DataFrame containing the data to be used for generating the word cloud.
    :param level: The level to filter the data on (e.g., 'Expenditure Level').
    :param mode: The mode of frequency calculation ('default' or 'amount').
    :param preprocess: Boolean indicating whether to preprocess the data.
    :param whether_jsonify: Boolean indicating whether to return the word cloud as a JSON response.
    :return: WordCloud object or JSON response with the word cloud image.
    """
    def preprocess_data(data, data_level):
        """
        Preprocesses the data by filtering based on the specified level and cleaning the 'description' column.

        :param data: DataFrame containing the data to be preprocessed.
        :param data_level: The level to filter the data on.
        :return: Cleaned and filtered DataFrame.
        """
        cleaned_data = data[['Expenditure Level'] == data_level].copy()
        cleaned_data['description'] = cleaned_data['description'].lower()
        cleaned_data['description'] = re.sub(r'[^a-zA-Z\s]', '', cleaned_data['description'])
        return cleaned_data

    def default_frequency(data):
        """
        Calculates frequency of each description in the data.

        :param data: DataFrame containing the preprocessed data.
        :return: Counter object with frequencies of descriptions.
        """
        frequency = Counter(data['description'])
        return frequency

    def amount_frequency(data):
        """
        Calculates frequency of each description weighted by the 'amount' column.

        :param data: DataFrame containing the preprocessed data.
        :return: Counter object with weighted frequencies of descriptions.
        """
        frequency = Counter()
        for description, amount in zip(data['description'], data['amount']):
            frequency[description] += amount
        return frequency

    def convert_wordcloud_into_json(wordcloud_object):
        """
        Converts a WordCloud object into a JSON response with a base64-encoded image.

        :param wordcloud_object: The WordCloud object to be converted.
        :return: JSON response containing the word cloud image.
        """
        img = BytesIO()
        wordcloud_object.to_image().save(img, 'PNG')
        img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
        return jsonify({"image": img_base64})

    preprocessed_data = preprocess_data(data_with_level, level) if preprocess else data_with_level.copy()
    freq_dict = amount_frequency(preprocessed_data) if mode == 'amount' else default_frequency(preprocessed_data)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(freq_dict)
    return convert_wordcloud_into_json(wordcloud) if whether_jsonify else wordcloud
