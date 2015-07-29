import urllib

from subprocess import call
from collections import namedtuple
from tempfile import NamedTemporaryFile

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
    def __init__(self, data, out, background_color, size=(1280, 720)):
        """
        Constructor
        @param data : The popcorn editor project json blob
        """
        self.DELETE_VIDEOS = True

        self.track_edits = []
        self.track_items = []
        self.track_videos = []
        self.current_video = NamedTemporaryFile(
            suffix='.avi',
            delete=self.DELETE_VIDEOS
        )
        self.background_color = background_color
        self.size = size
        self.editor = Editor()
        self.real_duration = data['media'][0]['duration']
        self.duration = data['media'][0]['duration']
        self.out = out

        self.preprocess(data)

    def process(self):
        self.draw_videos()
        self.draw_items()
        self.draw_edits()
        call(['ffmpeg', '-i', self.current_video.name, self.out])

    def draw_videos(self):
        i = 0
        for video in reversed(self.track_videos):
            overlay = NamedTemporaryFile(
                suffix='.avi',
                delete=self.DELETE_VIDEOS
            )

            # Trim the video if it needs to be
            if (video.options['from'] != 0 or
                video.options['end'] - video.options['from'] <
                    video.options['duration']):

                self.editor.trim(
                    video.options['title'].replace(' ', '-') + '.webm',
                    overlay.name,
                    seconds_to_timecode(video.options['from']),
                    seconds_to_timecode(video.options['duration'])
                )
            else:
                overlay.name = video.options['title'].replace(' ', '-') + \
                    '.webm'

            # Also scale the video down to size
            scaled_overlay = NamedTemporaryFile(
                suffix='.avi',
                delete=self.DELETE_VIDEOS
            )
            self.editor.scale_video(
                overlay.name,
                scaled_overlay.name,
                percent_to_px(video.options['width'], self.size[0]),
                percent_to_px(video.options['height'], self.size[1]),
            )
            overlay.close()

            out = NamedTemporaryFile(suffix='.avi', delete=self.DELETE_VIDEOS)

            self.overlay_videos(self.current_video.name, scaled_overlay.name,
                                video.options, out.name)
            scaled_overlay.close()

            self.current_video = out
            i += 1

    def overlay_videos(self, underlay_video, overlay_video, options, out):
        overlay1 = NamedTemporaryFile(suffix='.avi', delete=self.DELETE_VIDEOS)
        overlay2 = NamedTemporaryFile(suffix='.avi', delete=self.DELETE_VIDEOS)
        overlay3 = NamedTemporaryFile(suffix='.avi', delete=self.DELETE_VIDEOS)
        overlay4 = NamedTemporaryFile(suffix='.avi', delete=self.DELETE_VIDEOS)

        self.editor.trim(
            underlay_video,
            overlay1.name,
            '00:00:00',
            str(options['start'])
        )

        self.editor.trim(
            underlay_video,
            overlay2.name,
            str(options['start']),
            str(options['end'] - options['start']),
        )

        self.editor.trim(
            underlay_video,
            overlay3.name,
            str(options['end'] - options['start']),
            str(options['end'])
        )

        # Now draw it onto the screen
        self.editor.draw_video(
            overlay2.name,
            overlay_video,
            overlay4.name,
            percent_to_px(options['left'], self.size[0]),
            percent_to_px(options['top'], self.size[1])
        )

        with open('loop.txt', 'w') as f:
            if not options['start'] == 0:
                f.write('file {0}\n'.format(overlay1.name))
            f.write('file {0}\n'.format(overlay4.name))
            if not options['start'] == 0:
                f.write('file {0}\n'.format(overlay3.name))

        command = ['ffmpeg', '-f', 'concat', '-i', 'loop.txt', '-y',
                   '-c', 'copy', out]
        call(command)

    def draw_items(self):
        for item in self.track_items:
            item_file = NamedTemporaryFile(suffix='.avi',
                                           delete=self.DELETE_VIDEOS)
            if item.edit_type == 'text':
                self.editor.draw_text(
                    self.current_video.name,
                    item_file.name,
                    item.options['start_stamp'],
                    item.options['end_stamp'],
                    item.options['x_px'],
                    item.options['y_px'],
                    item.options['text'],
                    item.options['fontColor'].replace('#', '0x'),
                    size=percent_to_px(item.options['fontSize'], self.size[1])
                )
            elif item.edit_type == 'image':
                # TODO
                pass
            self.current_video = item_file

    def draw_edits(self):
        print
        print
        print
        print self.track_edits
        print
        print
        print
        for edit in self.track_edits:
            edit_file = NamedTemporaryFile(suffix='.avi',
                                           delete=self.DELETE_VIDEOS)
            if edit.edit_type == 'skip':
                self.editor.skip(
                    self.current_video.name,
                    edit_file.name,
                    edit.options['start'],
                    edit.options['end'] - edit.options['start'],
                )
            elif edit.edit_type == 'loopPlugin':
                print edit.options['loop']
                self.editor.loop(
                    self.current_video.name,
                    edit_file.name,
                    str(edit.options['start']),
                    str(edit.options['end'] - edit.options['start']),
                    int(edit.options['loop']),
                    str(self.real_duration),
                )

            self.current_video = edit_file

    def preprocess(self, data):
        """
        Processes popcorn JSON and builds a sane data model out of it
        @param data : The popcorn editor project json blob
        """

        print 'Beginning pre-process...'
        for url, video in data['media'][0]['clipData'].iteritems():
            print 'Downloading {0}.'.format(url)
            video['title'] = video['title'].replace(' ', '-') + '.webm'
            urllib.urlretrieve(url, video['title'])
            print 'Finished download!'
        print 'All videos downloaded.'

        events = [event for track in data['media'][0]['tracks']
                  for event in track['trackEvents']]

        for event in events:
            if event['type'] == 'skip' or event['type'] == 'loopPlugin':
                edit = TrackEdit(event['type'], event['popcornOptions'])

                self.track_edits.append(edit)

            if event['type'] == 'text' or event['type'] == 'image':
                item = TrackItem(event['type'], event['popcornOptions'])

                item.options['start_stamp'] = \
                    item.options['start']
                item.options['end_stamp'] = \
                    item.options['end']
                item.options['x_px'] = percent_to_px(
                    item.options['left'],
                    self.size[0]
                )
                item.options['y_px'] = percent_to_px(
                    item.options['top'],
                    self.size[1]
                )

                self.track_items.append(item)

            if event['type'] == 'sequencer':
                video = TrackVideo(
                    event['type'],
                    event['popcornOptions']['source'][0],
                    event['popcornOptions']
                )
                self.track_videos.append(video)

        self.parse_duration()

        cfilter = r'color=c={0}:s={1}x{2}:d={3};aevalsrc=0:d={4}'.format(
            self.background_color,
            self.size[0],
            self.size[1],
            self.duration,
            self.duration,
        )
        call(['ffmpeg', '-filter_complex', cfilter, '-y',
              self.current_video.name])

    def parse_duration(self):
        """
        Corrects for any offsets that may have been created by loop and skip
        events
        """
        for edit in self.track_edits:
            if edit.edit_type == 'loopPlugin':
                self.duration += (
                    (edit.options['end'] -
                     edit.options['start']) *
                    float(edit.options['loop'])
                )
