import warnings
import math

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.colors import Colormap

from matplotlib.offsetbox import OffsetImage,AnnotationBbox,TextArea
from PIL import Image

import datetime

import os
import sys

class _BarChartGenerator():
    def __init__(self, img_label_folder, title, fig_kwargs, tick_label_font, num_bars, bar_colors):
        self.img_label_folder = img_label_folder
        self.title = title
        default_fig_kwargs = {'figsize': (6, 6), 'dpi': 144}
        default_font_dict = {'size': 7, 'ha': 'right'}
        self.fig_kwargs = {**default_fig_kwargs, **fig_kwargs}
        self.num_bars = num_bars
        self.fig = self.create_figure()
        self.tick_label_font = {**default_font_dict, **tick_label_font}
        self.bar_colors = bar_colors
        self.df_values = None
        self.df_ranks = None
        self.xticks = None
        self.extra_pixels = 0
        self.img_label_artist = []

    def prepare_axes(self, ax):
        ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

        ax.grid(True, axis='x', color='#3d3d3d', linewidth=2, zorder=0)

        # ax.tick_params(labelsize=self.tick_label_font['size'], length=0, pad=2)
        ax.tick_params(axis='x', length=1, labelsize=27, pad=1, color='#F8FAFF')
        ax.tick_params(axis='y', length=1, labelsize=27, pad=1, color='#ffffff00')
        ax.set_facecolor('#000000')

        ax.minorticks_off()
        ax.set_axisbelow(True)

        ax.set_title(**self.title, wrap=True)

        for spine in ax.spines.values():
            spine.set_visible(True)

        limit = (0, self.num_bars + 1)
        ax.set_ylim(limit)
        ax.set_xscale('linear')

        ax.spines['left'].set_linewidth(1)
        ax.spines['left'].set_color('#D3DCE6')
        ax.spines['right'].set_linewidth(0)
        ax.spines['top'].set_linewidth(0)
        ax.spines['bottom'].set_linewidth(0)
        

    def create_figure(self):
        fig = plt.Figure(**self.fig_kwargs, tight_layout=False)

        ax = fig.add_subplot()

        self.prepare_axes(ax)
        return fig
    
    def getFig(self):
        return self.fig
    

    def setDataFrame(self, df_values, df_ranks):
        df_ranks = df_ranks.clip(upper=self.num_bars + 1)
        df_ranks = self.num_bars + 1 - df_ranks
        self.df_values = df_values
        self.df_ranks = df_ranks


    def get_bar_colors(self, bar_colors):
        n = len(bar_colors)
        if self.df_values.shape[1] > n:
            bar_colors = bar_colors * (self.df_values.shape[1] // n + 1)
        bar_colors = np.array(bar_colors[:self.df_values.shape[1]])
        return bar_colors


    def get_bar_info(self, i):
        bar_location = self.df_ranks.iloc[i].values
        top_filt = (bar_location > 0.5) & (bar_location < self.num_bars + 1)
        bar_location = bar_location[top_filt]
        bar_length = self.df_values.iloc[i].values[top_filt]
        names = self.df_values.columns[top_filt]
        colors = self.get_bar_colors(self.bar_colors)[top_filt]
        return bar_location, bar_length, names, colors


    def adjust_limits_labels(self, ax, bar_lengths):
        ax.set_yticklabels(ax.get_yticklabels(), **self.tick_label_font, wrap=True)
        max_bar = bar_lengths.max()
        max_bar_pixels = ax.transData.transform((max_bar, 0))[0]
        new_max_pixels = max_bar_pixels + self.extra_pixels
        new_xmax = ax.transData.inverted().transform((new_max_pixels, 0))[0]
        ax.set_xlim(ax.get_xlim()[0], new_xmax)

        # Divide or Multiply x ticks by a power of 2^
        tickLimit = 5
        if self.xtickInterval * tickLimit / 2.0 > new_xmax:
            self.xtickInterval = self.xtickInterval / 2.0
        tickScaler = 2.0 if self.xtickInterval * (tickLimit + 0.25) < new_xmax else 1.0
        
        tickPositions = self.xtickInterval * tickScaler * range(math.ceil(new_xmax / (self.xtickInterval * tickScaler)))
        self.xtickInterval = tickPositions[1]
        ax.set_xticks(tickPositions)

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_visible(False)
            tick.label2.set_visible(True)
            tick.label2.set_color('#FFFFFF')
            tick.label2.set_horizontalalignment('center')
            tick.label2.set_fontsize(self.tick_label_font['size'])
            tickLoc = ax.transData.transform((tick.get_loc(), 0))[0]
            halfWidth = tick.label2.get_window_extent().width / 2
            if (tickLoc + halfWidth + 50 > new_max_pixels):
                tick.label2.set_visible(False)
        if len(ax.xaxis.get_major_ticks()) > self.past_num_ticks:
            ax.xaxis.get_major_ticks()[-1].label2.set_visible(False)
        self.past_num_ticks = len(ax.xaxis.get_major_ticks())


    def add_images(self, ax, bar_locations, bar_lengths, bar_names):
        zipped = zip(bar_locations, bar_lengths, bar_names)
        for bar_loc, bar_len, bar_name in zipped:
            #split_name = bar_name.split('.')
            #if len(split_name) > 1:
            #    img_name = split_name
            #else:
            img_name = bar_name + '.jpg'
            path          = os.path.join(self.img_label_folder, img_name)
            img           = Image.open(path)
            img.thumbnail((200,200),Image.Resampling.LANCZOS)
            im            = OffsetImage(img,zoom=.28)
            im.image.axes = ax

            ab = AnnotationBbox(im,(1,bar_loc,),xybox=(-25,0.),frameon=False,xycoords='data',
                                    boxcoords='offset points',pad=0)
            self.img_label_artist.append(ab)
            ax.add_artist(ab)


    def set_major_formatter(self, ax):
        ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))


    def add_period_label(self, ax, i):
        period_label={
            'x': 0.95, 
            'y': 0.1,
            'ha': 'right',
            'va': 'center',
            'size': 64,
            'weight': 'semibold',
            'color': '#FFFFFF'
        }
        period_template='{x:.0f}'
        date = self.df_values.index[i]
        year_percent = date.item() % 1
        month = int(year_percent * 12 + 1)
        s = datetime.date(int(date.item()), month, 1).strftime('%b\n%Y')

        ax.text(s=s, transform=ax.transAxes, **period_label)

    
    #def add_period_summary(self, ax, i):
        


    def add_bar_labels(self, ax, bar_locations, bar_lengths, bar_names):
        zipped = zip(bar_lengths, bar_locations, bar_names)
        valDelta = 0.02
        labelDelta = 0.01
        vertDelta = 0.008
        bar_label_font={
            'size': 14,
            'weight': 'semibold',
            'color':'#FFFFFF'
        }
        for x1, y1, name in zipped:
            xtext, ytext = ax.transLimits.transform((x1, y1))
            ytext -= vertDelta

            val = x1
            bar_texttemplate='{x:.0f}'
            val = bar_texttemplate.format(x=val)
            val = f'{int(val):,}'

            xVal = xtext + valDelta
            yVal = ytext
            xVal, yVal = ax.transLimits.inverted().transform((xVal, yVal))
            xLabel, yLabel = ax.transLimits.inverted().transform((labelDelta, ytext))
            ax.text(xVal, yVal, val, clip_on=True, **bar_label_font)
            labelText = ax.text(xLabel, yLabel, name, clip_on=True, **bar_label_font)
            xLim = ax.transData.inverted().transform((labelText.get_window_extent().x1, 0))[0]

            # Binary search
            if xLim > x1:
                upperLimit = len(name)
                lowerLimit = 0
                middle = (upperLimit - lowerLimit) // 2 
                while upperLimit - lowerLimit > 1:
                    labelText.remove()
                    nameShort = name[:middle + 1]
                    labelText = ax.text(xLabel, yLabel, nameShort, clip_on=True, **bar_label_font)
                    xLim = ax.transData.inverted().transform((labelText.get_window_extent().x1, 0))[0]
                    if xLim > x1:
                        upperLimit = middle
                        middle = middle - math.ceil((upperLimit - lowerLimit) / 2)
                    else:
                        lowerLimit = middle
                        middle = middle + math.ceil((upperLimit - lowerLimit) // 2)
                labelText.remove()
                nameShort = name[:middle + 1]
                labelText = ax.text(xLabel, yLabel, nameShort, clip_on=True, **bar_label_font)
                xLim = ax.transData.inverted().transform((labelText.get_window_extent().x1, 0))[0]
                if xLim > x1:
                    labelText.remove()            


    #def add_perpendicular_bars(self):
    

    def plot_bars(self, ax, i):
        # Create horizontal bar plot
        bar_locations, bar_lengths, bar_names, bar_colors = self.get_bar_info(i)
        bar_kwargs = {
            'height':0.8,
            'alpha':0.99,
            'lw':0,
            'ec':'white'
        }
        ax.barh(bar_locations, bar_lengths, tick_label="", color=bar_colors, **bar_kwargs)

        if (not bool(i)):
            self.xtickInterval = ax.get_xticks()[1]
            self.past_num_ticks = len(ax.xaxis.get_major_ticks())

        # Add other things to plot
        self.set_major_formatter(ax)
        self.adjust_limits_labels(ax, bar_lengths)
        self.add_bar_labels(ax, bar_locations, bar_lengths, bar_names)
        self.add_images(ax, bar_locations, bar_lengths, bar_names)
        self.add_period_label(ax, i)
        #self.add_period_summary(ax, i)
        #self.add_perpendicular_bars()


    def init_func(self):
        # Setup initial plot here
        ax = self.fig.axes[0]
        
        # Get extra pixels
        bar_label_font={
            'size': 16,
            'weight': 'semibold',
            'color':'#FFFFFF'
        }
        max = self.df_values.to_numpy().max()
        self.extra_pixels = ax.text(0, 1, max, clip_on=True, **bar_label_font).get_window_extent().width

        self.plot_bars(ax, 0)


    def anim_func(self, i):
        # Setup each plot frame here
        if i is None:
            return
        self.fig.tight_layout(pad=6)
        ax = self.fig.axes[0]

        # Remove plot stuff
        for bar in ax.containers:
            bar.remove()
        for text in ax.texts[0:]:
            text.remove()

        # Images
        for artist in self.img_label_artist:
            artist.remove()
        self.img_label_artist = []

        # Plot bars
        self.plot_bars(ax, i)
