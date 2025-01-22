# project: p5
# submitter: apierrelouis
# partner: none
# hours: 5
import pandas as pd
import sklearn
import numpy as np
import sklearn.linear_model
import sklearn.metrics
import sklearn.feature_extraction.text as sktext

class UserPredictor:   
    def __init__(self):
        self.model = None
    
    def fit(self, users, logs, y):
        self.model = sklearn.linear_model.LogisticRegression()
        numerical_df = users[['user_id','past_purchase_amt']]
        #badge_df = pd.DataFrame(sktext.CountVectorizer().fit_transform(users['badge']).todense()).rename(columns={0: "bronze", 1: "gold", 2:"silver"})
        seconds_df = logs[['user_id','seconds']].groupby('user_id').sum()
        
        #x = pd.concat([numerical_df, badge_df], axis=1)
        x = numerical_df
        x = x.join(seconds_df, on='user_id')
        x['seconds'] = x['seconds'].fillna(0)
        
        self.model.fit(x, y['y'])
        
    def predict(self, users, logs):
        numerical_df = users[['user_id','past_purchase_amt']]
        #badge_df = pd.DataFrame(sktext.CountVectorizer().fit_transform(users['badge']).todense()).rename(columns={0: "bronze", 1: "gold", 2:"silver"})
        seconds_df = logs[['user_id','seconds']].groupby('user_id').sum()
        
        #x = pd.concat([numerical_df, badge_df], axis=1)
        x = numerical_df
        x = x.join(seconds_df, on='user_id')
        x['seconds'] = x['seconds'].fillna(0)
        
        return self.model.predict(x)
    
    def conf_matrix(self, y_lab, y_pred):
        return sklearn.metrics.confusion_matrix(y_lab, y_pred)