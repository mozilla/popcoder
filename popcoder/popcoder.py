from video import Video


def process_json(data, out, background_color='#000000'):
    video = Video(data, out, background_color)
    video.process()
