import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
import glob

class App:
    def __init__(self, window, window_title, video_source=0, class_list=None):
        self.window = window
        self.window.title(window_title)

        self.video_loader = Load_Movie()
        self.video_source = video_source
        self.video_id = 0
        self.frame_set_num=0
        self.vid = self.video_loader.video_capture(self.video_id)
        self.canvas = tk.Canvas(window, width = 640, height = 360)
        self.canvas.grid(rowspan=len(class_list)+5)
        self.btn_previous=tk.Button(window, text="Previous", width=20, command=self.previous_set)
        self.btn_previous.grid(sticky=tk.W, row = 0, column = 1, columnspan=2)
        self.btn_next=tk.Button(window, text="Next", width=20, command=self.next_set)
        self.btn_next.grid(sticky=tk.E, row = 0, column = 3, columnspan=2)
        self.jump_box_label=tk.Label(text="Jump to")
        self.jump_box_label.grid(sticky=tk.E, row = 1, column = 1)
        self.jump_box=tk.Entry(width=10)

        self.movie_text = tk.StringVar()
        self.video_id_text = tk.StringVar()
        self.movie_text_setter()

        self.jump_box.grid( row=1, column=2)
        self.btn_jump=tk.Button(window, text="Go", width=20, height = 1 ,command=self.jump_button)
        self.btn_jump.grid(sticky=tk.W, row=1, column=3, columnspan=2)
        self.video_label = tk.Label(self.window, textvariable=self.video_id_text)
        self.video_label.grid(row = 2, column = 2, columnspan=2)
        self.movie_label = tk.Label(self.window, textvariable=self.movie_text)
        self.movie_label.grid(row = 3, column = 1, columnspan=4)
        self.btn_saver=tk.Button(window, text="Save", width=20, height = 2 ,command=self.saver)
        self.btn_saver.grid(row = 4, column=2, columnspan=2)
        self.btn_refresh=tk.Button(window, text="Refresh", width = 20, command=self.refresh)
        self.btn_refresh.grid(row=len(class_list)+5, column=0)
        self.delay = 15

        self.class_list_name = []
        for cl_l in class_list:
            idx = class_list.index(cl_l)
            cln = cl_l.lstrip("label_data/").rstrip("_class.txt")
            self.class_list_name.append(cln)
            self.class_list_name[idx] = MakePulldown(window, window_title, cl_l, idx, cln)

        self.update()
        self.window.mainloop()

    def saver(self):
        labels = []
        for cln in self.class_list_name:
            labels.append(cln.variable.get())
        print(" ".join(labels))
    #def previous_frame()
    def refresh(self):
        self.vid.framen=0
    def next_set(self):
        if self.frame_set_num>=(len(self.vid.frames)-90)//75:
            self.video_id+=1
            self.jump_movie()
        else:
            self.frame_set_num+=1
        print(self.frame_set_num)
        self.vid.framen=self.frame_set_num*75
        self.movie_text_setter()

    def previous_set(self):
        if self.frame_set_num<=0:
            self.video_id-=1
            self.jump_movie()
        else:
            self.frame_set_num-=1
        print(self.frame_set_num)
        self.vid.framen=self.frame_set_num*75
        self.movie_text_setter()

    def jump_button(self):
        if self.video_id == int(self.jump_box.get())-1:

            pass
        else:
            self.video_id = int(self.jump_box.get())-1
            self.jump_movie()

    def jump_movie(self):
        self.video_id =  self.video_id % len(self.video_loader.movie_files)
        self.frame_set_num=0
        self.movie_text_setter()
        self.vid = self.video_loader.video_capture(self.video_id)

    def movie_text_setter(self):
        self.movie_text.set("{0} from {1} to {2} frames".format(self.video_loader.get_movie_name(self.video_id), self.frame_set_num*75, (self.frame_set_num+2)*75))
        self.video_id_text.set("{} / {} movies".format(self.video_id+1, len(self.video_loader.movie_files)))

    def update(self):
        ret, frame = self.vid.get_frame()
        if self.frame_set_num*75<=self.vid.framen<(self.frame_set_num+2)*75:
            try:
                frame = cv2.resize(frame, (640, 360))
                #frame = cv2.resize(frame, (self.vid.width, self.vid.height))
            except:
                self.vid.framen=self.frame_set_num*75
                ret, frame = self.vid.get_frame()
                frame = cv2.resize(frame, (640, 360))
            finally:
                if ret:
                    self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
                    self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
                self.window.after(self.delay, self.update)
        #elif ret:
        #    self.vid = MyVideoCapture(self.video_source)
        else:
            self.window.after(0, self.update)


class MakePulldown:
    def __init__(self, window, window_title, class_text, numb=0, cln="None"):
        self.window = window
        self.window.title(window_title)
        open_file = open(class_text, "r")
        lines = open_file.read().splitlines()
        open_file.close()
        self.name=cln
        self.item =lines
        self.attribution = tk.Label(text = self.name)
        self.attribution.grid(column = 1, row =numb+5)
        self.variable = tk.StringVar(window)
        self.variable.set(self.item[0])
        self.pulldown = tk.OptionMenu(window, self.variable, *self.item)
        self.pulldown.config(width=20, font=('Helvetica', 12))
        self.pulldown.grid(column=2, row = numb+5, pady=1, columnspan=2)


class Saver:
    def __init__(self):
        defaults = Default_Configure()
        self._defaults = defaults._defaults
        self.export_path = self._defaults["export_path"]

    def save(self, movie_name, class_list_name, labels):
        for cln in class_list_name:
            a=[]



class MyVideoCapture:
    def __init__(self, video_source=0, ):
        self.defaults = Default_Configure()
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)*0.5)
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)*0.5)
        ret = True
        self.frames=[]
        self.framen =0
        while True:
            ret, frame = self.vid.read()
            if ret:
                self.frames.append([ret, frame])
                now = int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))
                self.total = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
                perc = int(100*now//self.total)
                print("\r",video_source.lstrip(self.defaults._defaults["import_path"]),"[{0}] {1}%: {2}/{3}frames".format("="*(int(perc//10))+"."*(10-int(perc//10)), perc, now, self.total), end='')
            else:
                break
        print("")

    def get_frame(self):
        if self.vid.isOpened():
            try:
                ret = self.frames[self.framen][0]
            except:
                return(False, None)
            else:
                frame = self.frames[self.framen][1]
                self.framen+=1
                if ret:
                    return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                else:
                    return (ret, None)
        else:
            return (ret, None)
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

class Load_Movie:
    def __init__(self):
        self.defaults = Default_Configure()
        self.movie_files = glob.glob(self.defaults._defaults["import_path"]+"/*.MOV")
        self.movie_files.sort()
        print(self.defaults._defaults["import_path"])
        """
        open_file = open("true_data.txt", "r")
        lines = open_file.read().splitlines()
        open_file.close()
        """

    def video_capture(self, video_id):
        target_video = self.movie_files[video_id]
        return MyVideoCapture(target_video)

    def get_movie_name(self, video_id):
        target_video = self.movie_files[video_id]
        return target_video.lstrip(self.defaults._defaults["import_path"])

class Default_Configure:
    def __init__(self):
        self._defaults ={
        "gt_path":"soft_data/mov_labels.txt",
        "frame_per_detection":15,
        "import_path":"/Users/Ryo/desktop/Master/raw_movie"
        "export_path":""
        }


label_data ="label_data/"
class_list = glob.glob(label_data+"*_class.txt")
App(tk.Tk(), " MovLabel", "", class_list)
