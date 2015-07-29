import json
import sys

from popcoder import process_json


def main():
    data = None
    with open('popcorn.json', 'r') as f:
        data = json.loads(f.read())

    process_json(data['data'], './out.webm', data['background'])

if __name__ == '__main__':
    sys.exit(main() or 0)
