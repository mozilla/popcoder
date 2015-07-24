from subprocess import call


class Editor:

    def __init__(self, ffmpeg_path='ffmpeg'):
        self.ffmpeg_path = ffmpeg_path

    def trim(self, video_name, out, start, duration):
        """
        Trims a clip to be duration starting at start
        @param video_name : name of the input video
        @param out : name of the output video
        @param start : starting position after the trim
        @param duration : duration of video after start
        """
        call(['ffmpeg', '-ss', start, '-i', video_name, '-t', duration, out])

    def skip(self, video_name, start, duration, out):
        """
        Skips a section of the clip
        @param video_name : name of video input file
        @param start : start time of the skip (seconds)
        @param duration : duration of the skip (seconds)
        @param out : name of output file
        """
        cfilter = (r"[0:v]trim=duration={start}[av];"
                   r"[0:a]atrim=duration={start}[aa];"
                   r"[0:v]trim=start={offset},setpts=PTS-STARTPTS[bv];"
                   r"[0:a]atrim=start={offset},asetpts=PTS-STARTPTS[ba];"
                   r"[av][bv]concat[outv];[aa][ba]concat=v=0:a=1[outa]")\
            .format(start=start, offset=start + duration)\
            .replace(' ', '')

        call(['ffmpeg', '-i', video_name,
              '-filter_complex', cfilter,
              '-map', '[outv]',
              '-map', '[outa]',
              out])

    def draw_video(self, underlay, overlay, out, x, y):
        """
        Draws one video over another
        @param underlay : video file on bottom
        @param overlay : video file to render on top
        @param out : output file
        @param start : starting position of overlay
        @param end : end position of overlay
        @param x : x position of overlay
        @param y : y position of overlay
        @param w : width of overlay
        @param h : height of overlay
        """
        cfilter = r"overlay=x={0}:y={1}:".format(x, y)
        call(['ffmpeg', '-i', underlay, '-i', overlay,
              '-filter_complex', cfilter, out])

    def draw_text(self, video_name, out, start, end, x, y, text,
                  color='#FFFFFF', show_background=0,
                  background_color='#000000'):
        """
         Draws text over a video
         @param video_name : name of video input file
         @param out : name of video output file
         @param start : start timecode to draw text hh:mm:ss
         @param end : end timecode to draw text hh:mm:ss
         @param x : x position of text (px)
         @param y : y position of text (px)
         @param text : text content to draw
         @param color : text color
         @param show_background : boolean to show a background box behind the
                                  text
         @param background_color : color of background box
         """
        cfilter = (r"drawtext=fontfile=/Library/Fonts/AppleGothic.ttf: "
                   r"x={x}: y={y}: fontcolor={font_color}:"
                   r"box={show_background}: "
                   r" boxcolor={background_color}:"
                   r"text={text}: enable='between(t, {start}, {end})'")\
            .format(x=x, y=y, font_color=color,
                    show_background=show_background,
                    background_color=background_color, text=text, start=start,
                    end=end)
        call(['ffmpeg', '-i', video_name, '-vf', cfilter,  '-an', '-y', out])

    def scale_video(self, video_name, out, width, height):
        scale = "scale={0}:{1}".format(width, height)
        call(['ffmpeg', '-i', video_name, '-vf', scale, out])

    def draw_image(self, video_name, image_name, out, start, end, x, y):
        """
        Draws an image over the video
        @param video_name : name of video input file
        @param image_name: name of image input file
        @param out : name of video output file
        @param start : when to start overlay
        @param end : when to end overlay
        @param x : x pos of image
        @param y : y pos of image
        """
        cfilter = (r"[0] [1] overlay=x={x}: y={y}:"
                   "enable='between(t, {start}, {end}')")\
            .format(x=x, y=y, start=start, end=end)

        call(['ffmpeg', '-i', video_name, '-i', image_name,
              '-filter_complex', cfilter, out])

    def loop(self, video_name, out, start, duration, iterations, video_length):
        """
        Loops a section of a video
        @param video_name : name of video input file
        @param out : name of video output file
        @param start : start time of loop (timestamp hh:mm:ss)
        @param duration : duration of loop section (seconds)
        @param iterations : amount of times to loop
        @param video_length : length of video
        """
        beginning = 'beginning.mp4'
        loop_section = 'loop.mp4'  # section of video that will be looped
        loops = 'loops.mp4'  # collection of looped sections
        end = 'end.mp4'

        self.trim(video_name, '0', start, beginning)
        self.trim(video_name, start, duration, loop_section)
        self.trim(video_name, '00:00:08', video_length, end)

        # Open text file it and write the loop clip  n times
        with open('loop.txt', 'w') as f:
            for i in range(1, iterations):
                line = 'file {0}\n'.format(loop_section)
                f.write(line)

        # concat the loop clip upon itself n times
        call(['ffmpeg', '-f', 'concat',
              '-i', 'loop.txt',
              '-c', 'copy', loops])

        # concat the beginning clip, combo of loops, and end clip
        cfilter = (r"[0:0] [0:1] [1:0] [1:1] [2:0] [2:1]"
                   r"concat=n=3:v=1:a=1 [v] [a1]")
        call(['ffmpeg', '-i', beginning, '-i', loops, '-i', end,
              '-filter_complex', cfilter,
              '-map', '[v]', '-map', '[a1]', out])
