from subprocess import call




class Popcoder:



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


if __name__ == '__main__':
    popcoder = Popcoder()

    # popcoder.trim('big.mp4', '00:01:00', '00:02:00', 'trim.mp4')
    # popcoder.skip('big.mp4', 20, 10, 'skip.mp4')
    # popcoder.draw_text('big.mp4', 'draw_text.mp4', 10, 50, 100, 50,
    #                    'hello world')
    # popcoder.draw_image('big.mp4', 'cat.gif', 'draw_image.mp4', 10, 50, 100,
    #                     100)
    # popcoder.loop('big.mp4', 'looped.mp4', '00:00:05', '3', 10, '00:18:16.24')
