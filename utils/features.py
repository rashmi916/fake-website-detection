import re
from urllib.parse import urlparse

def extract_features(url):
    parsed = urlparse(url if '://' in url else 'http://' + url)
    hostname = parsed.netloc
    path = parsed.path or '/'
    features = {}
    features['url_length'] = len(url)
    features['hostname_length'] = len(hostname)
    features['count_dots'] = hostname.count('.')
    features['has_https'] = 1 if parsed.scheme == 'https' else 0
    features['has_at'] = 1 if '@' in url else 0
    features['count_hyphens'] = hostname.count('-')
    features['count_subdir'] = path.count('/')
    # IP in domain?
    features['is_ip'] = 1 if re.match(r'^\d+\.\d+\.\d+\.\d+$', hostname) else 0
    # suspicious tokens
    suspicious_tokens = ['login', 'verify', 'update', 'bank', 'secure', 'account']
    features['susp_token'] = sum(1 for t in suspicious_tokens if t in url.lower())
    return features
