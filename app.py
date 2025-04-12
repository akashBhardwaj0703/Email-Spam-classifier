from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
from sklearn.base import BaseEstimator, TransformerMixin
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import email
import re
import string
from bs4 import BeautifulSoup
import nltk

# nltk.download('stopwords')
# nltk.download('punkt')

# Initialize Flask app
app = Flask(__name__)
CORS(app)


stemmer = PorterStemmer()


class email_to_clean_text(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None): 
        return self
    
    def transform(self, X):
        text_list = []
        for mail in X:
            # Convert each email string to an email object
            b = email.message_from_string(mail)
            body = ""

            # Check if email is multipart (with attachments)
            if b.is_multipart():
                for part in b.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))
                    # Skip attachments; only get 'text/plain' part
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        body = part.get_payload(decode=True)
                        break
            else:
                # Single-part email, just get payload
                body = b.get_payload(decode=True)

            # Use BeautifulSoup to get plain text from HTML
            soup = BeautifulSoup(body, "html.parser")
            text = soup.get_text().lower()  # Convert to lowercase

            # Remove links
            text = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', text, flags=re.MULTILINE)
            # Remove email addresses
            text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text, flags=re.MULTILINE)
            # Remove punctuation
            text = text.translate(str.maketrans('', '', string.punctuation))
            # Remove digits
            text = ''.join([i for i in text if not i.isdigit()])

            # Remove stop words
            stop_words = stopwords.words('english')
            words_list = [w for w in text.split() if w not in stop_words]

            # Apply stemming
            words_list = [stemmer.stem(w) for w in words_list]

            # Join words back into a single string
            text_list.append(' '.join(words_list))
        
        return text_list


model = joblib.load('./spam_classifier_model.pkl')
vectorizer = joblib.load('./tfidf_vectorizer.pkl')

email_cleaner = email_to_clean_text()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    try:
        data = request.get_json()
        email_content = data.get('email')
        

        
        #email clean
        
        clean_email = email_cleaner.transform([email_content])

        
        email_vector = vectorizer.transform(clean_email)

        
        prediction = model.predict(email_vector)[0]
        classification = 'Spam' if prediction == 1 else 'Ham'

        return jsonify({'classification': classification})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
