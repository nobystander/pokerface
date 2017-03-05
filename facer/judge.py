# -*- coding=utf8 -*-
"""
    给每个用户打分使用
"""
import os
from tkMessageBox import showwarning
from Tkinter import Tk, Label, Button, Radiobutton, IntVar
from PIL import ImageTk, Image
from tkFont import Font
from model import FemaleFace
from detect import detect_face

image_dir = '../data'
master = None
tk_image = None
face_file_list = None
offset = 0
face_record, face_image, face_label, index_label, detect_label = [None for i in range(5)]


def get_filename(offset):
    """获取图片名称"""
    return face_file_list[offset]


def get_face_record(offset=0):
    """读取头像信息"""
    global face_record
    filename = get_filename(offset)
    face_record = FemaleFace.get(filename)
    if not face_record:
        face_record = FemaleFace.add(filename, label=-1)
    else:
        print 'T..' ,face_record.id


def init_master():
    """初始化主窗口"""
    global master
    master = Tk()
    master.title(u'Facer')
    master.geometry(u'660x700')
    master.resizable(width=False, height=False)


def place_image(offset=0):
    """获取用户头像"""
    global tk_image
    filename = get_filename(offset)
#   print os.path.join(image_dir, filename)
    image = Image.open(os.path.join(image_dir, filename))
    tk_image = ImageTk.PhotoImage(image)


def set_face_label():
    """设置头像标签"""
    print face_record.id,face_label.get()
    FemaleFace.update(face_record.id, label=face_label.get())

    handle_next()


def update():
    """更新页面"""
    print offset
    place_image(offset)

    face_image['image'] = tk_image
    index_label['text'] = u'{}/{}'.format(offset + 1, len(face_file_list))
    face_label.set(face_record.label)

    handle_detect()


def init():
    """初始化页面"""
    global face_file_list, face_image, face_label, detect_label

    all_files = os.listdir(image_dir)
    face_file_list = filter(lambda x: x.endswith('jpg'), all_files)
    get_face_record(offset)


    place_image(offset)
    face_image = Label(master, image=tk_image)
    face_image.place(anchor=u'nw', x=10, y=40)

    face_label = IntVar()
    face_label.set(face_record.label)
    score_ugly = Radiobutton(master, text=u'丑', variable=face_label,
                             value=0, command=set_face_label)
    score_ugly.place(anchor=u'nw', x=120, y=10)
    score_normal = Radiobutton(master, text=u'一般', variable=face_label,
                               value=1, command=set_face_label)
    score_normal.place(anchor=u'nw', x=160, y=10)
    score_pretty = Radiobutton(master, text=u'漂亮', variable=face_label,
                               value=2, command=set_face_label)
    score_pretty.place(anchor=u'nw', x=220, y=10)

    detect_label = Label(master, text=u'')
    detect_label.place(anchor=u'nw', x=580, y=10)

    handle_detect()


def handle_previous():
    """上一个用户"""
    global offset
    if offset <= 0:
        showwarning(u'error', u'已经是第一个')
        return

    offset -= 1
    get_face_record(offset)
    update()


def handle_next():
    """下一个用户"""
    global offset
    if offset >= len(face_file_list):
        showwarning(u'error', u'已经是第后一个')
        return

    offset += 1
    get_face_record(offset)
    update()


def handle_rotate():
    """旋转图片"""
    global tk_image
    filename = get_filename(offset)
    file_path = os.path.join(image_dir, filename)
    image = Image.open(file_path).rotate(90)
    image.save(file_path)
    tk_image = ImageTk.PhotoImage(image)
    face_image['image'] = tk_image


def handle_detect():
    """检查人脸"""
    filename = get_filename(offset)
    file_path = os.path.join(image_dir, filename)
    print filename
    print file_path
    result = detect_face(face_record.id, file_path)


    if result:
        detect_label['text'] = u'检测成功'
        detect_label['fg'] = 'green'
    else:
        detect_label['text'] = u'检测失败'
        detect_label['fg'] = 'red'


def add_assembly():
    """添加组件"""
    global index_label

    init()
    index_label = Label(master, text=u'{}/{}'.format(offset + 1, len(face_file_list)),
                        font=Font(size=20))
    index_label.place(anchor=u'nw', x=10, y=10)
    previous_button = Button(master, text=u'上一个', command=handle_previous)
    previous_button.place(anchor=u'nw', x=300, y=8)
    next_button = Button(master, text=u'下一个', command=handle_next)
    next_button.place(anchor=u'nw', x=380, y=8)
    rotate_button = Button(master, text=u'旋转', command=handle_rotate)
    rotate_button.place(anchor=u'nw', x=460, y=8)
    detect_button = Button(master, text=u'检查', command=handle_detect)
    detect_button.place(anchor=u'nw', x=520, y=8)


if __name__ == '__main__':
    init_master()
    add_assembly()
    master.mainloop()

