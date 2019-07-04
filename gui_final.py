# ===========================================================================
''' 
    BARR SYSTEM 
    User Interface
'''
# ===========================================================================

''' import gui libraries '''
import tkinter as tk
import threading
from PIL import ImageTk, Image, ImageSequence
import time
import json
from random import randint
''' make sure import threading before matplotlib ''' 
from threading import Thread
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style
''' import BARR-SYSTEM libraries '''
import os
import database_gui as db
from record_safe import record 
from analyze_safe import analysis
import numpy as np

#====================================================================
# Written by Arjun Pawar @ asp191@rutgers.edu on December 7, 2018
#====================================================================

class Page(tk.Frame):
	def __init__(self, *args, **kwargs):
		tk.Frame.__init__(self, *args, **kwargs)
		self.next_page = None
		self.previous_page = None

	def show(self):
		self.lift()

	def set_next_page(self, page):
		self.next_page = page

	def set_previous_page(self, page):
		self.previous_page = page

	def on_next_button(self):
		print("[INFO] Results button pressed!")
		try:
			self.next_page.lift()
		except:
			print("[ERROR] There's no next page registered.")

	def on_previous_button(self):
		print("[INFO] Previous button pressed!")
		try:
			self.previous_page.lift()
		except:
			print("[ERROR] There's no previous page registered.")


class InfoPage(Page):
	def __init__(self, *args, **kwargs):
		global config
		Page.__init__(self, *args, **kwargs)
		fields = ["Name", "Age", "Height", "Weight", "Injury", "First Time User?"]

		tk.Label(self, text = config["info_page"]["title"]).pack(pady = 10, side = "top")

		self.frames = dict()
		self.entries = dict()

		for field in fields:
			self.frames[field] = tk.Frame(self)
			tk.Label(self.frames[field], text = field, width = 15, anchor = "w", justify = "left").\
					pack(padx = 200, side = "left", fill = "both", anchor = "w")

			if field is fields[len(fields) - 1]:
				self.entries[field] = tk.StringVar(self.frames[field])
				self.entries[field].set("yes")
				tk.OptionMenu(self.frames[field], self.entries[field], "yes", "no").\
					pack(side = "left", fill = "x")

			else:
				self.entries[field] = tk.Entry(self.frames[field], \
									bg = config["universal"]["entry_color"], justify = "left")
				self.entries[field].pack(side = "left", fill = "x")

			self.frames[field].pack(side = "top", fill = "both", expand = True)


		self.submit_button = tk.Button(self, text = "Submit", \
							command = self.on_submit_button).pack(pady = 20, side = "top")

# ===========================================================================
   # When 'Submit' button is pressed,
   # Aggregate the information entered by user in output database
   # Then, go to Page 2
# ===========================================================================

	def on_submit_button(self):
		''' get entry and setup database on submit button 
		''' 
		print("[INFO] Submit button pressed! Collecting information entered by user.")

		data = dict()
		data["name"] = self.entries["Name"].get()
		data["injury"] = self.entries["Injury"].get()
		data["first_time"] = (self.entries["First Time User?"].get() == "yes")

		try:
			data["age"] = int(self.entries["Age"].get())
			data["height"] = int(self.entries["Height"].get())
			data["weight"] = int(self.entries["Weight"].get())

		except:
			print(' ')

		''' setup database '''
		# ===========================================================================
		conn = db.setup(directory + 'output/') # create registration page if not exist
		if not len(data["name"].replace(' ', '')) == 0: 
			db.create_session(conn, data["name"], 1)
		# ===========================================================================
		
		''' push command to comm center '''
		# ===========================================================================
		comm_center = open(directory + 'comm_center/gui.txt', 'w')
		comm_center.writelines(data["name"])
		comm_center.close()
		# ===========================================================================

		print(data)
		print("[INFO] Proceeding to Page 2.")
		self.next_page.lift()


class ExercisePage1(Page):
	def __init__(self, *args, **kwargs):
		Page.__init__(self, *args, **kwargs)

		tk.Label(self, text= config["exercise_page_1"]["title"]).pack(pady = 10, side = "top")
		tk.Label(self, text= config["exercise_page_1"]["test_name"]).pack(pady = 10, side = "top")

		self.test_running = False
		self.image_plot_frame = tk.Frame(self)
		
		# insert gif
		self.image_description_frame = tk.Frame(self.image_plot_frame)
		self.image_canvas = tk.Canvas(self.image_description_frame, width = 400, height = 300)
		self.gif_sequences = [ImageTk.PhotoImage(img.resize((400, 300),Image.ANTIALIAS)) \
							for img in ImageSequence.Iterator(Image.open(config["exercise_page_1"]["graphic"]))]
		self.image = self.image_canvas.create_image(0, 0, anchor="nw", image = self.gif_sequences[0])
		self.image_canvas.pack(side = "top")
		
		# insert message 
		self.gif_thread = Thread(target = self.animate_gif, args = ())
		self.gif_thread.start()
		self.exercise_description = tk.Message(self.image_description_frame, width = 500, \
									text = config["exercise_page_1"]["message"])
		self.exercise_description.pack(side = "top", fill = "both", expand = True)

		self.image_description_frame.pack(side = "left", padx = 50, fill = "x", expand = True)

		self.image_plot_frame.pack(side = "top", fill = "both", expand = True)
		
		# pack buttons 
		button_frame = tk.Frame(self)
		self.start_stop_button = tk.Button(button_frame, text = "Start Exercise", \
								command = self.on_start_stop_button)
		self.start_stop_button.pack(padx = 50, pady = 20, side = "left")

		tk.Button(button_frame, text = "See Results", \
			command = self.on_next_button).pack(padx = 50, pady = 20, side = "left")
		button_frame.pack(side = "top")

	def animate_gif(self):
		number_of_frames = len(self.gif_sequences)
		counter = 1
		while True:
			self.image_canvas.itemconfig(self.image, image = self.gif_sequences[counter])
			counter += 1
			if counter >= len(self.gif_sequences):
				counter = 0
			time.sleep(0.03)

	# modify this function to change plot result
	# def update_plot(self):
	# 	while self.test_running:			
	# 		self.sub_plot.clear()
	# 		self.sub_plot.plot([randint(0, 30) for i in range(0,10)], [randint(0, 30) for i in range(0,10)])
	# 		self.plot_canvas.draw()
	# 		time.sleep(1)

	def on_start_stop_button(self):
		''' change button text on clicks 
		'''
		print("[INFO] {} button pressed!".format(self.start_stop_button["text"]))
		
		# Start Test. Put different thread here to collect test result, 
		# Then, call self.update_plot to update the plot in real-time
		if self.start_stop_button["text"] == "Start Exercise":

			''' call record on a different thread '''
			# ===========================================================================
			thread = threading.Thread(target=record, args=())
			thread.daemon = True                            # Daemonize thread
			thread.start()                                  # Start the execution
			# ===========================================================================

			''' write the last name to comm center '''
			# ===========================================================================
			conn = db.setup(directory+'output/')
			last_name = db.data_read(conn, 'Registration', '*', '', '')[-1,2]
			comm_center = open(directory + 'comm_center/gui.txt', 'w')
			comm_center.writelines(last_name)
			comm_center.close()
			# ===========================================================================

			self.start_stop_button["text"] = "Stop Exercise"
			# self.test_running = True
			# update_plot_thread = Thread(target = self.update_plot, args = ())
			# update_plot_thread.daemon = True
			# update_plot_thread.start()

		# Stop Test
		else:
			''' push command to comm center '''
			# ===========================================================================
			comm_center = open(directory + 'comm_center/gui.txt', 'w')
			comm_center.writelines('stop')
			comm_center.close()
			# ===========================================================================
			self.start_stop_button["text"] = "Start Exercise"
			print("Test stopping")
			self.test_running = False


class ResultPage(Page):
	''' each button imports an analysis result figure from local and display 
		analysis function is called in the analysis button
	'''
	def __init__(self, *args, **kwargs):
		Page.__init__(self, *args, **kwargs)
		tk.Frame.__init__(self, *args, **kwargs)
		
		tk.Label(self, text= config["result_page"]["title"]).pack(pady = 10, side = "top")

		self.frames = dict()
		self.entries = dict()
		self.entries_messages = dict()
		
		image1 = os.path.dirname(os.path.realpath(__file__)) + '/gui_final/resources/result.png'
		image2 = os.path.dirname(os.path.realpath(__file__)) + '/gui_final/resources/result_angle.png'
		image3 = os.path.dirname(os.path.realpath(__file__)) + '/gui_final/resources/result_form.png'
		
		self.kneeplot = tk.Button(self, text = "Analyze", width = 10, command = lambda: \
						self.ImageShow(image1))
		self.kneeplot.place(x = 50, y = 50)

		self.kneeangle = tk.Button(self, text = "Mobility", width = 10, command = lambda: \
						self.ImageShow1(image2))
		self.kneeangle.place(x = 50, y = 75)

		self.kneeform = tk.Button(self, text = "Technique", width = 10, command = lambda: \
						self.ImageShow2(image3))
		self.kneeform.place(x = 50, y = 100)
		
		self.image_plot_frame = tk.Frame(self)

		self.end_button = tk.Button(self, text = "End Program", \
						command = self.on_end_button).pack(pady = 20, side = "top")
		
	def ImageShow(self, path):
		''' analyze '''
		analysis()
		''''''
		image = Image.open(path)
		photo = ImageTk.PhotoImage(image)
		label = tk.Label(self, image = photo, bg = "black")
		label.image = photo
		label.place(x = 340, y = 90)

	def ImageShow1(self, path):

		image = Image.open(path)
		photo = ImageTk.PhotoImage(image)

		label = tk.Label(self, image = photo, bg = "black")
		label.image = photo
		label.place(x = 100, y = 150)

	def ImageShow2(self, path):

		image = Image.open(path)
		photo = ImageTk.PhotoImage(image)

		label = tk.Label(self, image = photo, bg = "black")
		label.image = photo
		label.place(x = 100, y = 250)

	def on_end_button(self):
		global root
		root.destroy()
	

class MainView(tk.Frame):
	def __init__(self, *args, **kwargs):
		global config

		tk.Frame.__init__(self, *args, **kwargs)
		p1 = InfoPage(self)
		p2 = ExercisePage1(self)
		p3 = ResultPage(self)

		p1.set_next_page(p2)
		p2.set_next_page(p3)
		p2.set_previous_page(p1)
		p3.set_previous_page(p2)

		tk.Label(self, text= config["main_view"]["title"], anchor = "w", justify = "left").\
							pack(padx = 5, pady = 2, side = "top", anchor = "w")
		tk.Label(self, text= config["main_view"]["subtitle"], anchor = "w", justify = "left").\
							pack(padx = 5,side = "top", anchor = "w")

		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)

		p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

		p1.show()


if __name__ == "__main__": 
	''' initial settings '''
	# change directory in settings.json
	directory = os.path.dirname(os.path.realpath(__file__)) + '/gui_final/'
	config = json.load(open(directory + 'settings.json', "r"))
	root = None

	''' plot styling '''
	# matplotlib.use("TkAgg") # error
	# style.use("ggplot")

	''' delete entry in comm center '''
	comm_center = open(directory + 'comm_center/gui.txt', 'r+')
	comm_center.truncate(0)

	''' GUI '''
	root = tk.Tk()
	root.option_add("*Font", config["universal"]["default_font"])
	root.option_add("*Background", config["universal"]["background"])
	root.option_add("*Foreground", config["universal"]["text_color"])
	root.title("{}: {}".format(config["main_view"]["title"], config["main_view"]["subtitle"]))
	main = MainView(root)
	main.pack(side="top", fill="both", expand=True)
	root.wm_geometry("1000x600")
	root.resizable(True, True)
	root.mainloop()