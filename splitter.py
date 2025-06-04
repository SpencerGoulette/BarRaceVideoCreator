import sys
import subprocess


def splitVideo(inputFile, outputFile1, length1, outputFile2, length2):
    split_cmd = ["ffmpeg", "-i", inputFile, "-vcodec", "copy",
                     "-acodec", "copy", "-y"]
    
    # First Video
    split_args = ["-ss", str(00:00:00), "-t", , outputFile1]
    subprocess.check_output(split_cmd + split_args)

    # Second Video
    split_args = ["-ss", str(), "-t", , outputFile2]
    subprocess.check_output(split_cmd + split_args)

'''
printHelp

Prints how to use the Python Script
'''
def printHelp():
    print('')
    print('The following is how to use the splitter script:')
    print('./splitter.py <videoPath> <video1> <length1> <video2> <length2>')
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
    if (len(sys.argv) == 6):
        splitVideo(sys.argv[1],
                    sys.argv[2], 
                    sys.argv[3], 
                    sys.argv[4],
                    sys.argv[5])
    else:
        printHelp()