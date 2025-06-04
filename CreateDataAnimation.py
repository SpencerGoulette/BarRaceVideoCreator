import sys
import pandas as pd
import Animator as anim

import ExampleGenerator as exGen
import BarRaceGenerator as barRace
import BarRaceGenerator2 as barRace2

import VideoFormats as video

'''
createVideo

Creates a Video based on a data folder
@param dataPath: Path to the directory containing data information
@return: A path to a video created in this function
'''
def createVideo(dataPath, videoPath, videoType, title, dpi, fps, length):
    print('Creating video from data in ' + dataPath + '...\n')

    # Data Info
    df = pd.read_csv(dataPath + "\\data.csv", index_col="Date")

    # Graph Generator Info
    title_kwargs = {
        'label': "\n" + str(title),
        'size': 48,
        'weight': 'bold',
        'pad': 50,
        'color': '#FFFFFF'
    }
    fig_kwargs = {
        'figsize': tuple(dim/int(dpi) for dim in video.VideoFormats[videoType]),
        'dpi': int(dpi),
        'facecolor': '#000000'
    }
    tick_label_font = {
        'size': 12,
        'color': '#FFFFFF',
        'horizontalalignment': 'center'
    }
    num_bars = 10
    bar_colors = [
            '#6ECBCE', '#FF2243', '#FFC33D', '#CE9673', '#FFA0FF', '#6501E5', '#F79522', '#699AF8', '#34718E', '#00DBCD',
            '#00A3FF', '#F8A737', '#56BD5B', '#D40CE5', '#6936F9', '#FF317B', '#0000F3', '#FFA0A0', '#31FF83', '#0556F3'
        ]

    #frameGenerator = barRace2._BarChartGenerator(title_kwargs, fig_kwargs, tick_label_font, num_bars, bar_colors)
    frameGenerator = barRace._BarChartGenerator(dataPath + "\\images", title_kwargs, fig_kwargs, tick_label_font, num_bars, bar_colors)
    #frameGenerator = exGen._ExampleGenerator("test")

    # Animation Info
    animator = anim._Animator(df, videoPath, frameGenerator, int(fps), int(length))
    animator.animate()

'''
printHelp

Prints how to use the Python Script
'''
def printHelp():
    print('')
    print('The following is how to use the BarRaceYoutubeScript script:')
    print('./CreateDataAnimation.py <pathToData> <videoPath> <videoType> <title> <dpi> <fps> <length>')
    print('')


'''
__main__

@param dataPath: path to the directory containing data 
videoPath: path and name to output video to
videoType: type of video to make, dictates 
title: video title
@return: A path to the bar racing video 
'''
if __name__ == '__main__':
    if (len(sys.argv) == 8):
        createVideo(sys.argv[1],
                    sys.argv[2], 
                    sys.argv[3], 
                    sys.argv[4],
                    sys.argv[5],
                    sys.argv[6],
                    sys.argv[7])
    else:
        printHelp()