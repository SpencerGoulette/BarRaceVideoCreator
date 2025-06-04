import math
import sys

import matplotlib.pyplot as plt

import pandas as pd
from matplotlib import rcParams
from matplotlib import animation

class _Animator():
    def __init__(self, df, filename, frame_generator, fps, length):
        self.filename = filename
        self.df = df
        self.writer = plt.rcParams['animation.writer']
        self.frame_generator = frame_generator
        self.fps = fps
        self.length = length
        self.df_values, self.df_ranks = self.prepareData()
        self.frame_generator.setDataFrame(self.df_values, self.df_ranks)


    def prepareData(self):
        # Calculate total number of frames needed
        period_length = math.ceil(self.length / (len(self.df) - 1))
        steps_per_period = self.fps * period_length
        print("Desired Length: " + str(self.length))
        print("Number of data points: " + str(len(self.df) - 1))
        print("Time per data point: " + str(period_length))
        print("Steps between data points: " + str(steps_per_period))
        print("Total time: " + str(steps_per_period * (len(self.df) - 1) / self.fps))

        # Replace NaN with minimum value in row
        self.df_values = self.df.T.fillna(self.df.min(axis=1) - 1).T

        self.df_values = self.df_values.reset_index()
        self.df_values.index = self.df_values.index * 10
        new_index = range(self.df_values.index[-1] + 1)
        self.df_values = self.df_values.reindex(new_index)
        
        if self.df_values.iloc[:, 0].dtype.kind == 'M': # Check for DateTime
            first, last = self.df_values.iloc[[0, -1], 0]
            daterange = pd.date_range(first, last, periods=len(self.df_values))
            self.df_values.iloc[:, 0] = daterange
        else:
            self.df_values.iloc[:, 0] = self.df_values.iloc[:, 0].interpolate()
        self.df_values = self.df_values.set_index(self.df_values.columns[0])
        self.df_values = self.df_values.interpolate()
        self.df_ranks = self.df_values.rank(axis=1, method='first', ascending=False)
        self.df_ranks = self.df_ranks.interpolate()

        #print(self.df_values)
        #print(self.df_ranks)

        self.df_values = self.df_values.reset_index()
        self.df_values.index = self.df_values.index * steps_per_period // 10
        new_index = range(self.df_values.index[-1] + 1)
        self.df_values = self.df_values.reindex(new_index)
        
        if self.df_values.iloc[:, 0].dtype.kind == 'M': # Check for DateTime
            first, last = self.df_values.iloc[[0, -1], 0]
            daterange = pd.date_range(first, last, periods=len(self.df_values))
            self.df_values.iloc[:, 0] = daterange
        else:
            self.df_values.iloc[:, 0] = self.df_values.iloc[:, 0].interpolate()
        self.df_ranks = self.df_ranks.reindex(self.df_values.iloc[:, 0]).interpolate()
        self.df_values = self.df_values.set_index(self.df_values.columns[0])
        self.df_values = self.df_values.interpolate()
        self.df_ranks[self.df_ranks > 11] = 11

        print(self.df_values)
        print(self.df_ranks)

        # Interpolate
        #self.df_values = self.df_values.reset_index()
        #self.df_values.index = self.df_values.index * steps_per_period
        #new_index = range(self.df_values.index[-1] + 1)
        #self.df_values = self.df_values.reindex(new_index)
        
        #if self.df_values.iloc[:, 0].dtype.kind == 'M': # Check for DateTime
        #    first, last = self.df_values.iloc[[0, -1], 0]
        #    daterange = pd.date_range(first, last, periods=len(self.df_values))
        #    self.df_values.iloc[:, 0] = daterange
        #else:
        #    self.df_values.iloc[:, 0] = self.df_values.iloc[:, 0].interpolate()
        #self.df_values = self.df_values.set_index(self.df_values.columns[0])
        #self.df_values = self.df_values.interpolate()
        #self.df_ranks = self.df_values.rank(axis=1, method='first', ascending=False)
        #self.df_ranks = self.df_ranks.interpolate()
        return self.df_values, self.df_ranks


    def progress_bar(self, count_value, total, suffix=''):
        bar_length = 10
        filled_up_Length = int(round(bar_length* count_value / float(total)))
        percentage = round(100.0 * count_value/float(total),1)
        bar = '=' * filled_up_Length + '-' * (bar_length - filled_up_Length)
        sys.stdout.write('[%s] %s%s ...%s\r' %(bar, percentage, '%', suffix))
        sys.stdout.flush()


    def getFig(self):
        return self.frame_generator.getFig()


    def getFrames(self):
        frames = []
        for i in range(len(self.df_values)):
            frames.append(i)
        return frames


    def init_func(self):
        self.frame_generator.init_func()


    def anim_func(self, i):
        self.frame_generator.anim_func(i)
        self.progress_bar(i, len(self.df_values))


    def animate(self):
        anim = animation.FuncAnimation(self.getFig(), 
                                       self.anim_func, 
                                       self.getFrames(), 
                                       self.init_func, 
                                       interval = 1.0 / self.fps)

        try:
            fc = self.frame_generator.getFig().get_facecolor()
            savefig_kwargs = {'facecolor': fc}

            ret_val = anim.save(self.filename, fps=self.fps, writer=self.writer, savefig_kwargs=savefig_kwargs)

        except Exception as e:
            message = str(e)
            raise Exception(message)
        #finally:
        #    plt.rcParams = self.orig_rcParams

        return ret_val
