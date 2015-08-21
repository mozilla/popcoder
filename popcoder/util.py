def seconds_to_timecode(sec):
    seconds = int(sec % 60)
    minutes = int(sec / 60)
    hours = int(sec / 3600)

    if seconds < 10:
        strsec = '0' + str(seconds)
    else:
        strsec = str(seconds)

    if minutes < 10:
        strmin = '0' + str(minutes)
    else:
        strmin = str(minutes)

    if hours < 10:
        strhours = '0' + str(hours)
    else:
        strhours = str(hours)

    return strhours + ':' + strmin + ':' + strsec


def percent_to_px(percent, px):
    return px / 100.0 * percent
