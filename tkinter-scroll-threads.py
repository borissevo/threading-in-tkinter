import datetime
import threading
import time
import tkinter as tk

class TaskGenerator(threading.Thread):
  def __init__(self, master):
    super().__init__()
    self.master = master
    self.force_quit = False
    self.stop = False
    self.stopped = False
  
  def run(self):
    while True:
      if self.force_quit:
        # if quit is requested, delete worker
        del self.master.worker
      elif self.stop:
        # if stop is requested, show Start button and hide Stop button, if that isn't already done
        if self.stopped is False:
          self.stopped = True
          self.master.start_button.pack(side=tk.BOTTOM, fill=tk.X)
          self.master.stop_button.pack_forget()
        continue
      else:
        # force a pause of 1s in task generation
        time.sleep(1)
        self.add_task()

  def add_task(self, event=None):
    # create label displaying current time
    new_task = self.create_label(str(datetime.datetime.now()))
    new_task.pack(side=tk.TOP, fill=tk.X)
  
  def create_label(self, label_text):
    return tk.Label(self.master.tasks_frame, text=label_text, pady=10, bg="yellow")
  
  def stop_generating(self):
    self.stopped = False
    self.stop = True


class Todo(tk.Tk):
  def __init__(self):
    super().__init__()

    self.tasks = []
    
    self.title("Todo.v.3")
    self.geometry("300x400")
    self.standard_font = (None, 16)

    # canvas which will hold scrollable frame
    self.tasks_canvas = tk.Canvas(self)

    # frame to display tasks
    self.tasks_frame = tk.Frame(self.tasks_canvas)

    # make canvas scrollable
    self.scrollable = tk.Scrollbar(self.tasks_canvas, orient="vertical", command=self.tasks_canvas.yview)
    self.tasks_canvas.configure(yscrollcommand=self.scrollable.set)

    # display canvas and frame
    self.tasks_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    self.scrollable.pack(side=tk.RIGHT, fill=tk.Y)
    self.tasks_canvas_frame = self.tasks_canvas.create_window((0, 0), window=self.tasks_frame, anchor="n")

    # create start button and display it
    self.start_button = tk.Button(self, text="Start", bg="lightgrey", fg="black", command=self.start, font=self.standard_font)
    self.start_button.pack(side=tk.BOTTOM, fill=tk.X)
    
    # create pause button
    self.stop_button = tk.Button(self, text="Stop", bg="lightgrey", fg="black", command=self.stop, font=self.standard_font)
    
    # event binding
    self.bind("<Configure>", self.on_frame_configure)
    self.bind_all("<MouseWheel>", self.mouse_scroll)
    self.tasks_canvas.bind("<Configure>", self.task_width)

    self.protocol("WM_DELETE_WINDOW", self.safe_destroy)
  
  def start(self):
    if not hasattr(self, "worker"):
      self.worker = TaskGenerator(self)
      self.worker.start()
    
    self.worker.stop = False
    self.start_button.pack_forget()
    self.stop_button.pack(side=tk.BOTTOM, fill=tk.X)
    self.worker.stopped = False
  
  def stop(self):
    if hasattr(self, "worker"):
      self.worker.stop_generating()
  
  def on_frame_configure(self, event=None):
    self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all"))

  def task_width(self, event):
    self.tasks_canvas.itemconfig(self.tasks_canvas_frame, width = event.width)

  def mouse_scroll(self, event):
    self.tasks_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
  
  def safe_destroy(self):
    if hasattr(self, "worker"):
      self.worker.force_quit = True
      self.after(1000, self.safe_destroy)
    else:
      self.destroy()

if __name__ == "__main__":
  todo = Todo()
  todo.mainloop()