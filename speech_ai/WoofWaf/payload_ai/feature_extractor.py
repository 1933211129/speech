import re

import numpy as np
from pandas import DataFrame


from typing import TypeVar

DataLoaderT = TypeVar("DataLoader")
FeatureExtT = TypeVar("FeatureExtractor")

class FeatureExtractor:
    def transform(self: FeatureExtT, data: DataFrame) -> DataFrame:
        """ Transform a raw dataset
            Parameters
            ----------
            self: FeatureExtractor instance
            data: Raw dataset as DataFrame

            Returns
            -------
            dataset: Extracted features
        """
        return self.get_features(data)

    def get_num_chars(self: FeatureExtT, payload: str) -> int:
        """ Get character count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of characters
        """
        return len(payload)

    def get_num_words(self: FeatureExtT, payload: str) -> int:
        """ Get word count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of words
        """
        return len(payload.split())

    def get_num_special_chars(self: FeatureExtT, payload: str) -> int:
        """ Get special char count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of special characters
        """
        return len(re.sub(r'[\w]+', '', payload))

    def get_num_ticks(self: FeatureExtT, payload: str) -> int:
        """ Get single quote count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of single quotes
        """
        return payload.count('\'')

    def get_num_dashes(self: FeatureExtT, payload: str) -> int:
        """ Get dash count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of dashes
        """
        return payload.count('-')

    def get_num_commas(self: FeatureExtT, payload: str) -> int:
        """ Get comma count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of commas
        """
        return payload.count(',')

    def get_num_pipes(self: FeatureExtT, payload: str) -> int:
        """ Get pipe count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of pipes
        """
        return payload.count('|')

    def get_num_equals(self: FeatureExtT, payload: str) -> int:
        """ Get equal count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of equal characters
        """
        return payload.count('=')

    def get_num_keywords(self: FeatureExtT, payload: str) -> int:
        """ Get SQL keyword count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of SQL keywords
        """
        keywords = ['select',
                    'from',
                    'where',
                    'union',
                    'sleep',
                    'or',
                    'and',
                    'like',
                    'order']
        count = 0

        word_list = payload.split()
        for word in word_list:
            if word.lower() in keywords:
                count += 1

        return count

    def get_num_parens(self: FeatureExtT, payload: str) -> int:
        """ Get parenthesis count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of parenthesis
        """
        return payload.count('(') + payload.count(')')

    def get_avg_word_len(self: FeatureExtT, payload: str) -> float:
        """ Get avg word length from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Average word length
        """
        words = payload.split()
        if len(words) > 0:
            return sum(len(word) for word in words) / len(words)
        else:
            return len(payload)

    def get_num_white_spaces(self: FeatureExtT, payload: str) -> int:
        """ Get white space count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of white spaces
        """
        return payload.count(' ')

    def get_num_comments(self: FeatureExtT, payload: str) -> int:
        """ Get SQL comment count from payload
            Parameters
            ----------
            self: FeatureExtractor instance
            payload: Single sample

            Returns
            -------
            Number of SQL comments
        """
        return payload.count('--')

    def get_features(self: FeatureExtT, data: DataFrame) -> DataFrame:
        """ Extract features from dataset
            Parameters
            ----------
            self: FeatureExtractor instance
            data: All samples

            Returns
            -------
            Features dataset
        """
        rows = []
        for i, row in data.iterrows():
            cols = []
            payload = str(row['payload'])
            label = row['label']

            cols.append(self.get_num_chars(payload))
            cols.append(self.get_num_words(payload))
            cols.append(self.get_num_special_chars(payload))
            cols.append(self.get_num_ticks(payload))
            cols.append(self.get_num_dashes(payload))
            cols.append(self.get_num_commas(payload))
            cols.append(self.get_num_pipes(payload))
            cols.append(self.get_num_equals(payload))
            cols.append(self.get_num_keywords(payload))
            cols.append(self.get_num_parens(payload))
            cols.append(self.get_avg_word_len(payload))
            cols.append(self.get_num_white_spaces(payload))
            cols.append(self.get_num_comments(payload))
            cols.append(label)
            rows.append(cols)

        df = DataFrame(rows, columns=['num_chars', 'num_words',
                                      'num_special_chars', 'num_ticks',
                                      'num_dashes', 'num_commas',
                                      'num_pipes', 'num_equals',
                                      'num_keywords', 'num_parens',
                                      'avg_word_len', 'num_white_spaces',
                                      'num_comments', 'label'])

        return df

    def payload_transform(self: FeatureExtT,payload:str):
        # 获取payload的特征
        new_data = np.array([[
            self.get_num_chars(payload),
            self.get_num_words(payload),
            self.get_num_special_chars(payload),
            self.get_num_ticks(payload),
            self.get_num_dashes(payload),
            self.get_num_commas(payload),
            self.get_num_pipes(payload),
            self.get_num_equals(payload),
            self.get_num_keywords(payload),
            self.get_num_parens(payload),
            self.get_avg_word_len(payload),
            self.get_num_white_spaces(payload),
            self.get_num_comments(payload)
 ]])

        return new_data

