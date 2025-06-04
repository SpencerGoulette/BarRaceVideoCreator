# BarRaceVideoCreator
A script that creates a bar race video based on the data and images provided to it.

To use the script you need to make sure that you have ffmpeg installed so that the media can be created.

Example data has been provided to use for testing and show that all you need is a formatted csv and images:
./CreateDataAnimation.py <pathToData> <videoPath> <videoType> <title> <dpi> <fps> <length in seconds>

In the case of the example data you might run something like the following:
./CreateDataAnimation.py ./ExampleData ./ TikTok Colleges 144 120 60

The script works by building both a frame generator and an animator. The frame generator creates a plot of the bars for a frame and the animator puts the frames together into a video. Additionally I have included a script for splitting video.
