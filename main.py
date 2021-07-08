import numpy as np
import amfm_decompy.pYAAPT as pYAAPT
import amfm_decompy.basic_tools as basic
import matplotlib.pyplot as plt
import dtwalign


# Read in recorded wav file

filename1 = "Karen_44100.wav"
filename2 = "Daniel.wav"
hop_s = 512

signal = basic.SignalObj(filename1)
pitches = pYAAPT.yaapt(signal, f0_min=50.0, f0_max=500.0, frame_length=40, tda_frame_length=40, frame_space=5)
pitches = pitches.samp_values
start = np.argmax(pitches > 0) # find index of first >0 sample
pitches = pitches[start:] # remove anything before that index
m_pitches = np.ma.masked_where(pitches <= 0, pitches) # mask 0 pitches (confidence was too low)
m_times = [(t * hop_s) / 1000 for t in range(len(pitches))]

signal = basic.SignalObj(filename2)
pitches = pYAAPT.yaapt(signal, f0_min=50.0, f0_max=500.0, frame_length=40, tda_frame_length=40, frame_space=5)
pitches = pitches.samp_values
start = np.argmax(pitches > 0)
pitches = pitches[start:]
r_times = [(t * hop_s) / 1000 for t in range(len(pitches))]
r_pitches = np.ma.masked_where(pitches <= 0, pitches)


plt.figure(figsize=(25, 3))
res = dtwalign.dtw(m_pitches, r_pitches, step_pattern="symmetricP2")

# dtw distance
print("dtw distance: {}".format(res.distance))
print("dtw normalized distance: {}".format(res.normalized_distance))

# # warp r_pitches to m_pitches
r_pitches_warping_path = res.get_warping_path(target="reference")
# plt.xlabel('time (ms)', fontsize=18)
# plt.ylabel('pitch (Hz)', fontsize=18)
# plt.plot(m_pitches, linewidth=2.5, label="Model")
# plt.plot(r_pitches[r_pitches_warping_path], linewidth=2.5, label="Mircophone", color="orange")
# plt.legend()
# plt.show()

###############################   GUI   #########################################

from dearpygui.dearpygui import *
import dearpygui.dearpygui as dpg
from dearpygui.core import *
from playsound import playsound

##### Global theme and setup #####

dpg.enable_docking()
dpg.setup_viewport()
dpg.set_viewport_title(title='Welcome')
dpg.set_viewport_width(1600)
dpg.set_viewport_height(900)

with dpg.font_registry():
    dpg.add_font("PlayfairDisplay-VariableFont_wght.ttf", 30, default_font=True)
    secondary_font = dpg.add_font("PlayfairDisplay-VariableFont_wght.ttf", 22)

with dpg.theme(default_theme=True) as series_theme:
    dpg.add_theme_color(dpg.mvThemeCol_Button, (207, 238, 250), category=dpg.mvThemeCat_Core)
    dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (137, 207, 240), category=dpg.mvThemeCat_Core)
    dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 3, category=dpg.mvThemeCat_Plots)

##### Required functions ######

def play_model(sender, data):
    playsound('Karen_44100.wav')

def open_file(sender, data):
    dpg.open_file_dialog()
    
def select_directory(sender, data):
    dpg.select_directory_dialog()

xaxis = dpg.generate_uuid()
yaxis = dpg.generate_uuid()

###### GUI for user nav bar ######

with dpg.window(label="User NavBar", width=300, height=900, pos=[0,0]) as user_nav_bar:
    dpg.add_text("Welcome!")
    instructions = dpg.add_text("To start, please upload an audio file.")
    # dpg.add_button(label="Play File", callback = play_model)
    upload_button = dpg.add_button(label='Upload File', callback=open_file)
    # dpg.add_button(label='Select Directory', callback=select_directory)

    with dpg.theme() as theme_id:
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (137, 207, 240), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core)
            

    dpg.set_item_theme(user_nav_bar, theme_id)
    dpg.set_item_font(instructions, secondary_font)
    dpg.set_item_font(upload_button, secondary_font)

###### GUI for plot ######

with dpg.window(label="Plot", width=1300, height=900, pos=[301,0]):

    # dpg.add_button(label="Play File", callback = play_model)
    # dpg.add_button(label='Open File', callback=open_file)
    # dpg.add_button(label='Select Directory', callback=select_directory)

    with dpg.plot(label="Intonation Plot", height=700, width=1300):

        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="x")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="y")

        dpg.fit_axis_data(x_axis)
        dpg.fit_axis_data(y_axis)

        m_pitches_list = m_pitches.tolist(fill_value=0)
        dpg.add_line_series(m_times, m_pitches_list, parent=y_axis)

        r_pitches_list = r_pitches[r_pitches_warping_path].tolist(fill_value=0)
        len_m = len(m_pitches_list)
        r_times_short = r_times[0:len_m] # Resize because array size has to be the same
        dpg.add_line_series(r_times_short, r_pitches_list, parent=y_axis)

dpg.start_dearpygui()
