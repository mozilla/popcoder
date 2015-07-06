import urllib

from subprocess import call
from collections import namedtuple

from editor import Editor
from util import seconds_to_timecode, percent_to_px

TrackItem = namedtuple('TrackItem', ['edit_type', 'options'])
TrackEdit = namedtuple('TrackEdit', ['edit_type', 'options'])
TrackVideo = namedtuple('TrackVideo', ['edit_type', 'url', 'options'])


class Video:

    """
    This class represents the data model of the rendered video. It manages the
    parsing of the popcorn json blob and calling the editing functions in the
    correct order
    """
    def __init__(self, data, background_color, size=(1280, 720)):
        """
        Constructor
        @param data : The popcorn editor project json blob
        """
        self.track_edits = []
        self.track_items = []
        self.track_videos = []
        self.video_name = 'blank.nut'
        self.background_color = background_color
        self.size = size
        self.editor = Editor()
        self.duration = data['media'][0]['duration']

        self.preprocess(data)

    def process(self):
        self.draw_videos()

    def draw_videos(self):
        i = 0
        for video in self.track_videos:
            # Trim the video if it needs to be
            if (video.options['from'] == 0 or
                video.options['end'] - video.options['from'] <
                    video.options['duration']):

                overlay = 'trimmed_' + str(i) + '.nut'

                self.editor.trim(
                    video.options['title'],
                    overlay,
                    seconds_to_timecode(video.options['from']),
                    seconds_to_timecode(video.options['duration'])
                )

                scaled_overlay = 'scaled_' + str(i) + '.nut'

                self.editor.scale_video(
                    overlay,
                    scaled_overlay,
                    percent_to_px(video.options['width'], self.size[0]),
                    percent_to_px(video.options['height'], self.size[1]),
                )

                out = 'video_' + str(i) + '.nut'

                # Now draw it onto the screen
                self.editor.draw_video(
                    self.video_name,
                    scaled_overlay,
                    out,
                    video.options['start'],
                    video.options['end'],
                    percent_to_px(video.options['left'], self.size[0]),
                    percent_to_px(video.options['top'], self.size[1]),
                    video.options['width'],
                    video.options['height']
                )

                self.video_name = out
                i += 1

    def draw_edits(self):
        i = 0
        for edit in self.track_edits:
            if i == 0:
                name = self.video_name
            else:
                name = str(i)

            if edit.edit_type == 'text':
                self.editor.draw_text(
                    name + '.nut',
                    'edit_' + str(++i) + '.nut',
                    edit.options['start_stamp'],
                    edit.options['end_stamp'],
                    edit.options['x_px'],
                    edit.options['y_px'],
                    edit.options['text'],
                    edit.options['color']
                )
            elif edit.edit_type == 'image':
                # TODO
                pass

    def preprocess(self, data):
        """
        Processes popcorn JSON and builds a sane data model out of it
        @param data : The popcorn editor project json blob
        """
        print 'Beginning pre-process...'
        for url, video in data['media'][0]['clipData'].iteritems():
            print 'Downloading {0}.'.format(url)
            urllib.urlretrieve(url, video['title'])
            print 'Finished download!'
        print 'All videos downloaded.'
        events = [event for track in data['media'][0]['tracks']
                  for event in track['trackEvents']]
        for event in events:
            if event['type'] == 'skip' or event['type'] == 'loop':
                edit = TrackEdit(event['type'], event['popcornOptions'])

                edit.options['start_stamp'] = \
                    seconds_to_timecode(edit.options['start'])
                edit.options['end_stamp'] = \
                    seconds_to_timecode(edit.options['start'])
                edit.options['x_px'] = percent_to_px(
                    edit.options['left'],
                    self.size[0]
                )
                edit.options['y_px'] = percent_to_px(
                    edit.options['top'],
                    self.size[1]
                )

                self.track_edits.append(edit)

            if event['type'] == 'text' or event['type'] == 'image':
                item = TrackItem(event['type'], event['popcornOptions'])
                self.track_items.append(item)
            if event['type'] == 'sequencer':
                video = TrackVideo(
                    event['type'],
                    event['popcornOptions']['source'][0],
                    event['popcornOptions']
                )
                self.track_videos.append(video)

        self.parse_duration()

        cfilter = r'color=c={0}:s={1}x{2}:d={3}'.format(
            self.background_color,
            self.size[0],
            self.size[1],
            self.duration
        )
        call(['ffmpeg', '-filter_complex', cfilter, self.video_name])

    def parse_duration(self):
        """
        Corrects for any offsets that may have been created by loop and skip
        events
        """
        for edit in self.track_edits:
            if edit.edit_type == 'skip':
                self.duration -= (edit.options['end'] -
                                  edit.options['start'])
            if edit.edit_type == 'loop':
                self.duration += (
                    (edit.options['end'] -
                     edit.options['start']) *
                    edit.options['loop']
                )
