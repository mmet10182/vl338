from config import WEB_API_BACKEND
from requests import request
import json

url = WEB_API_BACKEND + 'subjects.json'


def get_subjects(url):
    req = request(method='get', url=url)
    req = json.loads(req.text)
    subjs = []
    for subj in req['posts']:
        subjs.append(subj['subject_name'])
    return subjs


if __name__ == '__main__':
    print(get_subjects(url))