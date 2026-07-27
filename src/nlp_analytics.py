import pandas as pd
import numpy as np
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer

class NLPTextAnalytics:
    def __init__(self, df):
        self.df = df.copy()
        try:
            import nltk
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
            try:
                nltk.data.find('sentiment/vader_lexicon.zip')
            except LookupError:
                nltk.download('vader_lexicon', quiet=True)
            self.sia = SentimentIntensityAnalyzer()
            self.has_vader = True
        except Exception:
            self.has_vader = False

    def clean_text(self, text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _fallback_sentiment(self, text):
        pos_words = {'excellent', 'smooth', 'comfortable', 'on time', 'punctual', 'friendly', 'clean', 'great', 'polite'}
        neg_words = {'delay', 'delayed', 'damaged', 'queue', 'frustrating', 'uncomfortable', 'glitch', 'horrible'}
        words = set(text.lower().split())
        pos_count = len(words.intersection(pos_words))
        neg_count = len(words.intersection(neg_words))
        if pos_count > neg_count:
            return 0.5
        elif neg_count > pos_count:
            return -0.5
        return 0.0

    def analyze_sentiments(self):
        """Perform VADER Sentiment Analysis or Fallback Sentiment on customer survey text feedback."""
        print("Extracting sentiment scores from passenger feedback text...")
        self.df['cleaned_feedback'] = self.df['feedback_text'].apply(self.clean_text)
        
        if self.has_vader:
            scores = self.df['cleaned_feedback'].apply(lambda x: self.sia.polarity_scores(x)['compound'])
        else:
            scores = self.df['cleaned_feedback'].apply(self._fallback_sentiment)
            
        self.df['compound_sentiment'] = scores
        self.df['sentiment_class'] = np.where(
            self.df['compound_sentiment'] >= 0.05, 'Positive',
            np.where(self.df['compound_sentiment'] <= -0.05, 'Negative', 'Neutral')
        )
        return self.df

    def extract_top_keywords(self, category=None, top_n=10):
        """Extract top N-gram key phrases using TF-IDF text mining (SPSS Text Mining equivalent)."""
        target_df = self.df if category is None else self.df[self.df['nps_category'] == category]
        corpus = target_df['feedback_text'].apply(self.clean_text).tolist()
        corpus = [doc for doc in corpus if len(doc) > 3]
        
        if not corpus:
            return pd.DataFrame()
            
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=top_n)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        scores = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
        features = vectorizer.get_feature_names_out()
        
        df_keywords = pd.DataFrame({'keyword_phrase': features, 'tfidf_score': scores})
        return df_keywords.sort_values(by='tfidf_score', ascending=False).reset_index(drop=True)

    def generate_nlp_summary(self):
        """Generate high-level text analytics executive summary."""
        df_sent = self.analyze_sentiments()
        sentiment_dist = df_sent['sentiment_class'].value_counts(normalize=True).round(4) * 100
        
        detractor_keywords = self.extract_top_keywords(category='Detractor', top_n=5)
        promoter_keywords = self.extract_top_keywords(category='Promoter', top_n=5)
        
        return {
            'sentiment_distribution_pct': sentiment_dist.to_dict(),
            'top_detractor_drivers': detractor_keywords.to_dict(orient='records'),
            'top_promoter_drivers': promoter_keywords.to_dict(orient='records')
        }

if __name__ == '__main__':
    from src.data_loader import IndigoDataLoader
    df = IndigoDataLoader().load_from_db()
    nlp = NLPTextAnalytics(df)
    summary = nlp.generate_nlp_summary()
    print("\n=== SENTIMENT DISTRIBUTION (%) ===")
    print(summary['sentiment_distribution_pct'])
    print("\n=== TOP DETRACTOR COMPLAINT DRIVERS (TF-IDF) ===")
    print(pd.DataFrame(summary['top_detractor_drivers']))
