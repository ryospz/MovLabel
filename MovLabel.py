import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
import glob
import pandas as pd
import csv
import os
import datetime

class App:
    def __init__(self, window, window_title, video_source=0, class_list=None):
        self.window = window
        self.window.title(window_title)


        self.video_loader = LoadMovie()
        self.video_source = video_source
        self.video_id = self.video_loader.video_id
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
        self.btn_saver=tk.Button(window, text="Save", width=20, height = 2 ,command=self.label_saver)
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
        self.saver = Saver(self.class_list_name)

        self.update()
        self.window.mainloop()


    def label_saver(self):
        labels = []
        for cln in self.class_list_name:
            labels.append(cln.variable.get())
        #print(" ".join(labels))
        _movie_name = self.video_loader.get_movie_name(self.video_id)
        _frame_num = self.frame_set_num*75
        print(labels)
        #print(self.saver.data_df.query("Movie_Name == @_movie_name").query("Begin == @_frame_num"))
        if self.saver.data_df.query("Movie_Name == @_movie_name").query("Begin == @_frame_num").empty:
            print("new labels")
            self.saver.save_new_label(_movie_name, self.frame_set_num*75, labels)
        else:
            print("overwrite")
            self.saver.save_overwrite(_movie_name, self.frame_set_num*75, labels)
    #def previous_frame()
    def refresh(self):
        self.vid.framen=0
    def initialize_pulldown(self, is_labeled=False):
        if is_labeled:
            label = labeled_data["mov_name"]["class"]["frame"]
            for cln in self.class_list_name:
                cln.variable.get()

        for cln in self.class_list_name:
            cln.variable.set(cln.item[0])
    def next_set(self):
        if self.frame_set_num>=(len(self.vid.frames)-90)//75:
            self.video_id+=1
            self.jump_movie()
        else:
            self.frame_set_num+=1
        print(self.frame_set_num)
        self.vid.framen=self.frame_set_num*75
        self.movie_text_setter()
        self.initialize_pulldown()

    def previous_set(self):
        if self.frame_set_num<=0:
            self.video_id-=1
            self.jump_movie()
        else:
            self.frame_set_num-=1
        print(self.frame_set_num)
        self.vid.framen=self.frame_set_num*75
        self.movie_text_setter()
        self.initialize_pulldown()


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
        #    self.vid = VideoCapture(self.video_source)
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
    def __init__(self, class_list_name):
        defaults = Default_Configure()
        self._defaults = defaults._defaults
        self.export_path = self._defaults["export_path"]
        self.class_list_name = class_list_name
        self.def_columns = ["Movie_Name", "Begin", "End"] + [cln.name for cln in self.class_list_name ]+ ["update_date"]
        try:
            self.data_df = pd.read_csv(self.export_path, index_col=0)
        except:
            self.df_initialize()
        else:
            pass

    def df_initialize(self):
        self.data_df = pd.DataFrame(columns=self.def_columns)
        with open(self.export_path, "w") as f:
            f.write(",".join(self.def_columns))
        self.data_df = pd.read_csv(self.export_path, index_col=0)


    def get_time(self):
        dt_now = datetime.datetime.now()
        dt_now = dt_now.strftime('%Y/%m/%d-%H:%M')
        return dt_now


    def save_new_label(self, movie_name, initial_frame,labels):
        dt_now = self.get_time()

        add_row = [movie_name, initial_frame, initial_frame+150]+labels+[dt_now]
        #print(add_row)
        #add_pd = pd.Series(add_row, columns=self.data_df.columns, index=self.data_df.columns)
        add_pd = pd.Series(add_row[1:], index=self.data_df.columns, name=add_row[0])
        self.data_df = self.data_df.append(add_pd)
        #self.data_df[:, movie_name]=add_row
        #print(self.data_df)
        with open(self.export_path, "a") as f:
            print("write")
            f.write("\n")
            f.write(",".join([str(e) for e in add_row]))


    def save_overwrite(self, movie_name, initial_frame, labels):
        dt_now = self.get_time()
        #print(labels)
        #self.data_df = self.data_df = pd.read_csv(self.export_path, index_col=0)
        self.data_df = self.data_df.query("Movie_Name != @movie_name | Begin != @initial_frame")
        if self.data_df.empty:
            self.df_initialize()
            return self.save_new_label(movie_name, initial_frame, labels)
        add_row = [movie_name, initial_frame, initial_frame+150]+labels+[dt_now]
        add_pd = pd.Series(add_row[1:], index=self.data_df.columns, name=add_row[0])
        self.data_df = self.data_df.append(add_pd)
        #print(self.data_df)

        self.data_df.to_csv(self.export_path, sep=",")






class VideoCapture:
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
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)
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

class LoadMovie:
    def __init__(self):
        self.defaults = Default_Configure()
        self.movie_files = glob.glob(self.defaults._defaults["import_path"]+"/*.MOV")
        self.movie_files.sort()
        self.video_id = 0
        self.movie_ifGT = [False]*len(self.movie_files)
        if os.path.exists(self.defaults._defaults["video_id_path"]):
            with open(self.defaults._defaults["video_id_path"], "r") as f:
                reader = csv.reader(f)
                self.exists_file = [row for row in reader]
                self.exists_file[0]
                self.add_file = []
                for vd in self.movie_files:
                    if not vd in self.exists_file[0]:
                        self.add_file.append(vd)
                        print(vd)
                self.movie_files = self.exists_file[0]+self.add_file
                self.movie_ifGT[:len(self.exists_file[1])] = self.exists_file[1]
                self.video_id = len(self.exists_file) if not self.add_file==[] else 0
        with open(self.defaults._defaults["video_id_path"], "w") as f:
            writer = csv.writer(f)
            writer.writerow(self.movie_files)
            writer.writerow(self.movie_ifGT)



        """
        open_file = open("true_data.txt", "r")
        lines = open_file.read().splitlines()
        open_file.close()
        """

    def video_capture(self, video_id):
        target_video = self.movie_files[video_id]
        return VideoCapture(target_video)

    def get_movie_name(self, video_id):
        target_video = self.movie_files[video_id]
        return target_video.strip().lstrip(self.defaults._defaults["import_path"])

class Default_Configure:
    def __init__(self):
        self._defaults ={
        "gt_path":"soft_data/mov_labels.txt",
        "detection_per_second":2,
        "viewing_span":10,
        "import_path":"./movies",
        "video_id_path":"./save_data/video_id.csv",
        "export_path":"./save_data/new_mov_labels.csv"
        }

if __name__ == "__main__":
    label_data ="label_data/"
    class_list = glob.glob(label_data+"*_class.txt")
    try:
        while True:
            App(tk.Tk(), " MovLabel", "", class_list)
            exit()
    except:
        print("End")
