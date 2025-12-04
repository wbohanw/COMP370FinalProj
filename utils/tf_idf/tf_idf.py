import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

CSV_FILE_NAME = r'C:\Users\Default\Desktop\COMP370FinalProj\utils\tf_idf\manual_annotation_all_movie_posts.csv' 
TITLE_COLUMN = 'title'
TEXT_COLUMN = 'selftext'

TOPIC_COLUMN = 'topics' 
N_WORDS = 10
COMBINED_TEXT_COLUMN = 'combined_text'



def get_top_tf_idf_words(df: pd.DataFrame, text_col: str, topic_col: str, n_top_words: int):

    topic_results = {}
    unique_topics = df[topic_col].unique()

    print(f"\n--- Starting TF-IDF Analysis for {len(unique_topics)} unique topics ---")

    for topic in unique_topics:
        #Filter the DataFrame to only include posts belonging to the current topic
        topic_df = df[df[topic_col] == topic]
        topic_documents = topic_df[text_col].tolist()

        #make custom stop words to include reddit lingo adn movie names and all + english disctionary stop words
        reddit_sw = ['op', 'redditor', 'post', 'comment', 'thread', 'subreddit', 'oc', 
                     'nsfw', 'spoiler', 'upvote','downvote', 'imho', 'tl;dr', 'edit',
                     'tldr', 'fwiw','nsfw']
        
        movie_sw = ['movie', 'film', 'release', 'theater', 'streaming', 'watch',
            'trailer', 'review', 'discussion', 'premiere', 'box office',
            'cast', 'director', 'actor', 'actress', 'imdb', 'cinema',
            'screening', 'dvd', 'blu-ray', 'netflix', 'hulu', 'disney',
            'amazon prime', 'plot', 'scene', 'ending', 'spoiler']
        
        movie_names = ["Kpop Demon Hunters", "Materialists", "Ballerina", "Bride Hard",
                       "F1 The Movie", "Jurassic World Rebirth", "How to Train Your Dragon",
                       "28 Years Later", "Elio", "M3GAN 2.0", "The Old Guard 2"]
        
        combined_stop_words = ENGLISH_STOP_WORDS.union(reddit_sw + movie_sw + movie_names)

        vectorizer = TfidfVectorizer(stop_words=combined_stop_words, token_pattern=r'\b[a-zA-Z]{3,}\b', smooth_idf=True)
        
        tfidf_matrix = vectorizer.fit_transform(topic_documents)
        feature_names = vectorizer.get_feature_names_out()
        sum_scores = tfidf_matrix.sum(axis=0) 
        
        #sort to find the top terms
        term_scores = pd.Series(sum_scores.tolist()[0], index=feature_names)
        top_n_terms = term_scores.sort_values(ascending=False).head(n_top_words)

        topic_results[topic] = top_n_terms.to_dict()

    return topic_results


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