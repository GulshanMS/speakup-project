# core/nlp_utils.py

import re
from collections import Counter

def extract_keywords(text, top_n=3):
    """
    Extract top N keywords from a single string of text.
    """
    words = re.findall(r'\b\w{4,}\b', text.lower())  # only words with 4+ characters
    common = Counter(words).most_common(top_n)
    return [word for word, count in common]

def extract_keywords_and_groups(text_list, top_n_keywords=10):
    """
    Given a list of messages, extract top keywords and group messages by keyword.

    Returns:
        issue_chart_data: dict with 'labels' and 'data' for bar chart
        keyword_to_messages: dict mapping keyword -> list of related messages
    """
    all_text = " ".join(text_list).lower()
    all_words = re.findall(r'\b\w{4,}\b', all_text)
    common_keywords = Counter(all_words).most_common(top_n_keywords)

    keywords = [word for word, count in common_keywords]
    frequencies = [count for word, count in common_keywords]

    keyword_to_messages = {
        keyword: [msg for msg in text_list if re.search(rf'\b{keyword}\b', msg, re.IGNORECASE)]
        for keyword in keywords
    }

    issue_chart_data = {
        'labels': keywords,
        'data': frequencies,
    }

    return issue_chart_data, keyword_to_messages
