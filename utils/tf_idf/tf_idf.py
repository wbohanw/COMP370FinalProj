import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import re

CSV_FILE_NAME = r'C:\Users\Default\Desktop\COMP370FinalProj\data\open_coding\manual_annotation_all_movie_posts.csv' 
TITLE_COLUMN = 'title'
TEXT_COLUMN = 'selftext'

TOPIC_COLUMN = 'topics' 
N_WORDS = 10
COMBINED_TEXT_COLUMN = 'combined_text'



def get_top_tf_idf_words(df: pd.DataFrame, text_col: str, topic_col: str, n_top_words: int):

    topic_results = {}
    unique_topics = df[topic_col].unique()

    print(unique_topics)

    print(f"\n--- Starting TF-IDF Analysis for {len(unique_topics)} unique topics ---")

    for topic in unique_topics:
        #Filter the DataFrame to only include posts belonging to the current topic
        topic_df = df[df[topic_col] == topic]
        topic_documents = topic_df[text_col].tolist()

        #make custom stop words to include reddit lingo adn movie names and all + english disctionary stop words
        reddit_sw = ['op', 'redditor', 'post', 'comment', 'thread', 'subreddit', 'oc', 
                     'nsfw', 'spoiler', 'upvote','downvote', 'imho', 'tl;dr', 'edit',
                     'tldr', 'fwiw','nsfw', "https", "http", "www", "com", "reddit", "sub", "url",
                     "img", "jpg", "gif", "png", "like", "just", "did"]
        
        movie_sw = ['movie', 'film', 'release', 'theater', 'streaming', 'watch',
            'trailer', 'review', 'discussion', 'premiere', 'box office',
            'cast', 'director', 'actor', 'actress', 'imdb', 'cinema',
            'screening', 'plot', 'scene', 'ending', 'spoiler', "reviews", "movies", "scenes", "title"]
        
        movie_names = ["Kpop Demon Hunters", "Materialists", "Ballerina", "Bride Hard",
                       "F1 The Movie", "Jurassic World Rebirth", "How to Train Your Dragon",
                       "28 Years Later", "Elio", "M3GAN 2.0", "The Old Guard 2"]
        
        raw_stop_words = list(ENGLISH_STOP_WORDS) + reddit_sw + movie_sw + movie_names
        combined_stop_words = tokenize_stopword_list(raw_stop_words)


        vectorizer = TfidfVectorizer(
        stop_words=combined_stop_words,
        token_pattern=r'\b[a-zA-Z]{3,}\b',
        smooth_idf=True
        )
        
        tfidf_matrix = vectorizer.fit_transform(topic_documents)
        feature_names = vectorizer.get_feature_names_out()
        sum_scores = tfidf_matrix.sum(axis=0) 
        
        #sort to find the top terms
        term_scores = pd.Series(sum_scores.tolist()[0], index=feature_names)
        top_n_terms = term_scores.sort_values(ascending=False).head(n_top_words)

        topic_results[topic] = top_n_terms.to_dict()

    return topic_results

def tokenize_stopword_list(words):
    token_pattern = re.compile(r'\b[a-zA-Z]{3,}\b')
    tokens = []
    for w in words:
        tokens.extend(token_pattern.findall(w.lower()))
    return tokens


df = pd.read_csv(CSV_FILE_NAME)
print(f"Successfully loaded data from {CSV_FILE_NAME}.")

df[COMBINED_TEXT_COLUMN] = df[TITLE_COLUMN].fillna('') + ' ' + df[TEXT_COLUMN].fillna('')
print(f"Combined '{TITLE_COLUMN}' and '{TEXT_COLUMN}' into '{COMBINED_TEXT_COLUMN}' column.")

top_words_by_topic = get_top_tf_idf_words(df, COMBINED_TEXT_COLUMN, TOPIC_COLUMN, N_WORDS)

print("\n" + "="*50)
print("✅ FINAL TF-IDF TOP WORDS BY TOPIC SUMMARY")
print("="*50)

for topic, words_scores in top_words_by_topic.items():
    # Sort the dictionary items by score in descending order for clean output
    sorted_scores = sorted(words_scores.items(), key=lambda item: item[1], reverse=True)
    
    print(f"\nTopic: **{topic}**")
    # Convert the scores to a formatted string for display
    formatted_words = [
        f"'{word}' (Score: {score:.4f})"
        for word, score in sorted_scores
    ]
    print("* " + "\n* ".join(formatted_words))

    #save to text file
    with open(r"C:\Users\Default\Desktop\COMP370FinalProj\data\tf_idf\tf_idf_results.txt", "a", encoding="utf-8") as f:
        f.write(f"\nTopic: **{topic}**\n")
        f.write("* " + "\n* ".join(formatted_words) + "\n")