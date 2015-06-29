from subprocess import call

class Popcoder:

    def __init__(self, ffmpeg_path='ffmpeg'):
        self.ffmpeg_path = ffmpeg_path

    """
    Trims a clip to be duration starting at start
    """
    def trim (self, video_name, start, duration, out):
        call(['ffmpeg', '-ss', start, '-i', video_name, '-t', duration, out])

    def skip (self, video_name, start, duration, out):
        cfilter = (r"[0:v]trim=duration={start}[av];"
            r"[0:a]atrim=duration={start}[aa];"
            r"[0:v]trim=start={offset},setpts=PTS-STARTPTS[bv];"
            r"[0:a]atrim=start={offset},asetpts=PTS-STARTPTS[ba];"
            r"[av][bv]concat[outv];[aa][ba]concat=v=0:a=1[outa]")\
        .format(start=start, offset=start + duration)\
        .replace(' ', '')

        print cfilter

        call(['ffmpeg', '-i', video_name,
            '-filter_complex', cfilter,
            '-map', '[outv]',
            '-map', '[outa]',
            out])

    """
    Draws text over a video
    @param video_name : name of video input file
    @param out : name of video output file
    @param start : start timecode to draw text hh:mm:ss
    @param end : end timecode to draw text hh:mm:ss
    @param text : text content to draw
    @param x : x position of text (px)
    @param y : y position of text (px)
    @param color : text color
    @param show_background : boolean to show a background box behind the text
    @param background_color : color of background box
    """
    def draw_text (self, video_name, out, start, end, x, y, text, color='#FFFFFF',
                show_background=0, background_color='#000000'):
        cfilter = (r"drawtext=fontfile=/Library/Fonts/AppleGothic.ttf: "
                r"x={x}: y={y}: fontcolor={font_color}: box={show_background}: "
                r" boxcolor={background_color}:"
                r"text={text}: enable='between(t, {start}, {end})'")\
            .format(x=x, y=y, font_color=color, show_background=show_background,
                    background_color=background_color, text=text, start=start,
                    end=end)

        call(['ffmpeg', '-i', video_name, '-vf', cfilter,  '-an', '-y', out])

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
    def draw_image (self, video_name, image_name, out, start, end, x, y):
        cfilter = (r"[0] [1] overlay=x={x}: y={y}:"
                "enable='between(t, {start}, {end}')")\
            .format(x=x, y=y, start=start, end=end)

        call(['ffmpeg', '-i', video_name, '-i', image_name,
            '-filter_complex', cfilter, out])

if __name__ == '__main__':
    popcoder = Popcoder()

    popcoder.trim('big.mp4', '00:01:00', '00:02:00', 'trim.mp4')
    popcoder.skip('big.mp4', 20, 10, 'skip.mp4')
    popcoder.draw_text('big.mp4', 'draw_text.mp4', 10, 50, 100, 50, 'hello world')
    popcoder.draw_image('big.mp4', 'cat.gif', 'draw_image.mp4', 10, 50, 100, 100)
