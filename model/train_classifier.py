import sys
import pandas as pd
import numpy as np
import pickle
from sqlalchemy import create_engine

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
from nltk.stem.wordnet import WordNetLemmatizer

from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion

nltk.download('stopwords')

def load_data(database_filepath):
    engine = create_engine('sqlite:///' + database_filepath)
    df = pd.read_sql_table('disaster_messages',engine)
    X = df['message']
    y = df.drop(columns=['id', 'message', 'original', 'genre'])
    
    return X,y, list(y.columns)

def tokenize(text):
    
    text = text.lower()
    text = WordPunctTokenizer().tokenize(text)
    words = [word for word in text if word not in stopwords.words('english')]
    words=[word for word in words if word.isalpha()]
    lemmed = [WordNetLemmatizer().lemmatize(w) for w in words]
    text_preprocessed = ' '.join(lemmed)

    return text_preprocessed


def build_model():
    
    
    pipeline = Pipeline([('vectorizer', CountVectorizer(tokenizer=tokenize)),
                     ('tfidf-transformer', TfidfTransformer()),
                     ('clf', MultiOutputClassifier(RandomForestClassifier()))])
    
    
    parameters = {'clf__estimator__max_depth': [20, 50, 100, 200],
                  'clf__estimator__n_estimators': [20, 50, 100, 200]}

    model = RandomizedSearchCV(estimator = pipeline, param_distributions = parameters, cv =3)


    return model
    
    
def evaluate_model(model, X_test, Y_test, category_names):
    
    y_pred = model.predict(X_test)
    
    print(classification_report(Y_test, y_pred, target_names=category_names))


def save_model(model, model_filepath):
    
    pickle.dump(model, open(model_filepath, 'wb'))


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()