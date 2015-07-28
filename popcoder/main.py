import json
import sys

from video import Video


class Popcoder:

    def process_popcorn(self, data, background_color='#000000'):
        video = Video(data, background_color)
        video.process()


def main():
    popcoder = Popcoder()

    # popcoder.trim('big.mp4', '00:01:00', '00:02:00', 'trim.mp4')
    # popcoder.skip('big.mp4', 20, 10, 'skip.mp4')
    # popcoder.draw_text('big.mp4', 'draw_text.mp4', 10, 50, 100, 50,
    #                    'hello world')
    # popcoder.draw_image('big.mp4', 'cat.gif', 'draw_image.mp4', 10, 50, 100,
    #                     100)
    # popcoder.loop('big.mp4', 'looped.mp4', '00:00:05', '3', 10, '00:18:16.24')

    data = None
    with open('popcorn.json', 'r') as f:
        data = json.loads(f.read())

    popcoder.process_popcorn(data['data'], data['background'])

if __name__ == '__main__':
    sys.exit(main() or 0)
