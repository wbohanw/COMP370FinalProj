import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


CSV_FILE_NAME = r'C:\Users\Default\Desktop\COMP370FinalProj\utils\tf_idf\manual_annotation_all_movie_posts.csv' 
TITLE_COLUMN = 'title'
TEXT_COLUMN = 'selftext'

TOPIC_COLUMN = 'topics' 
N_WORDS = 10 # You specifically asked for the top 10 words

# The new column that will combine title and text for analysis
COMBINED_TEXT_COLUMN = 'combined_text'



def get_top_tf_idf_words(df: pd.DataFrame, text_col: str, topic_col: str, n_top_words: int):

    topic_results = {}
    unique_topics = df[topic_col].unique()

    print(f"\n--- Starting TF-IDF Analysis for {len(unique_topics)} unique topics ---")

    for topic in unique_topics:
        # 1. Filter the DataFrame to only include posts belonging to the current topic
        topic_df = df[df[topic_col] == topic]
        topic_documents = topic_df[text_col].tolist()

        # 2. Initialize the TF-IDF Vectorizer
        # We use standard English stop words and look for words of 3+ letters.
        vectorizer = TfidfVectorizer(stop_words='english', token_pattern=r'\b[a-zA-Z]{3,}\b', smooth_idf=False)
        
        # 3. Fit and Transform the documents
        tfidf_matrix = vectorizer.fit_transform(topic_documents)

        # 4. Get feature names and sum the scores for the topic
        feature_names = vectorizer.get_feature_names_out()
        sum_scores = tfidf_matrix.sum(axis=0) 
        
        # 5. Create a Series and sort to find the top terms
        term_scores = pd.Series(sum_scores.tolist()[0], index=feature_names)
        top_n_terms = term_scores.sort_values(ascending=False).head(n_top_words)

        # 6. Store the results
        topic_results[topic] = top_n_terms.to_dict()
        
        print(f"\nCompleted analysis for topic: **{topic}** (found {len(top_n_terms)} top words)")

    return topic_results

# --- 3. EXECUTE THE REVISED ANALYSIS WORKFLOW ---

# 3a. Load the data
try:
    # Load your actual data here
    df = pd.read_csv(CSV_FILE_NAME)
    print(f"Successfully loaded data from {CSV_FILE_NAME}.")
except FileNotFoundError:
    print(f"ERROR: The file '{CSV_FILE_NAME}' was not found. Please check the file name and path.")
    # Exiting here in the real script; using mock data for demonstration purposes
    # If using the code block above, you can skip this error since it created a mock file.
    pass

# 3b. Preprocessing: Combine title and text into a single column
# The .fillna('') handles cases where a post might be missing a title or body text.
df[COMBINED_TEXT_COLUMN] = df[TITLE_COLUMN].fillna('') + ' ' + df[TEXT_COLUMN].fillna('')
print(f"Combined '{TITLE_COLUMN}' and '{TEXT_COLUMN}' into '{COMBINED_TEXT_COLUMN}' column.")

# 3c. Run the function
# Replace 'df' here with your actual loaded DataFrame
top_words_by_topic = get_top_tf_idf_words(df, COMBINED_TEXT_COLUMN, TOPIC_COLUMN, N_WORDS)


# --- 4. DISPLAY FINAL OUTPUT (For your report) ---

print("\n" + "="*50)
print("✅ FINAL TF-IDF TOP WORDS BY TOPIC SUMMARY")
print("="*50)

for topic, words_scores in top_words_by_topic.items():
    # Sort the dictionary items by score in descending order for clean output
    sorted_scores = sorted(words_scores.items(), key=lambda item: item[1], reverse=True)
    
    print(f"\n## 📌 Topic: **{topic}**")
    # Convert the scores to a formatted string for display
    formatted_words = [
        f"'{word}' (Score: {score:.4f})"
        for word, score in sorted_scores
    ]
    print("* " + "\n* ".join(formatted_words))