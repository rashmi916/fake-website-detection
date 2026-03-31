import joblib
import os
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models_store', 'model_v1.pkl')

def load_model(path=None):
    p = path or MODEL_PATH
    model = joblib.load(p)
    return model

def predict(model, features_dict):
    # convert dict to feature vector in correct order
    keys = ['url_length','hostname_length','count_dots','has_https','has_at','count_hyphens','count_subdir','is_ip','susp_token']
    x = [features_dict.get(k,0) for k in keys]
    prob = model.predict_proba([x])[0][1]  # assuming label 1 => phishing
    verdict = 'phishing' if prob >= 0.5 else 'legitimate'
    return float(prob), verdict
