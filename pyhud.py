#!/usr/bin/env python

import threading
from Tkinter import *
from playsound import playsound
from Queue import Empty, Queue

LEFT_SIDE_EVENT_NUM = 1
RIGHT_SIDE_EVENT_NUM = 2

EVENT_STATE_TRUE = 1
EVENT_STATE_FALSE = 0

class ThreadedUdpListener(threading.Thread):
    def __init__(self, queue):
        super(ThreadedUdpListener, self).__init__()
        self.queue = queue
        
    def run(self):
        dyn_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dyn_sock.bind(('0.0.0.0', 5007))
        try:
            while True:
                dyn_data = dyn_sock.recvfrom(4)[0] # 142 values, each 4 bytes, + 640 values each 1 byte
                event_num = struct.unpack('s', dyn_data[0:2])[0] # little endian 0-4
                event_state = struct.unpack('s', dyn_data[2:4])[0]
                event_state_bool = false
                if (event_state == EVENT_STATE_TRUE):
                    event_state_bool = true
                elif (event_state == EVENT_STATE_FALSE):
                    pass
                else:
                    print("[+] ERROR: Event state not 1 or 0. It was " + str(event_state))
                    # Let's crash, as this may invalidate the experiment
                    exit()
                if (event_num != LEFT_SIDE_EVENT_NUM and event_num != RIGHT_SIDE_EVENT_NUM):
                    print("[+] ERROR: Event number not 1 or 2. It was " + str(event_num))
                    # Let's crash, as this may invalidate the experiment
                    exit()                    
                # pushes a tuple of (integer, boolean) on the queue. integer is the side, boolean is the 
                queue.put( (event_num, event_state_bool) )
        except KeyboardInterrupt:
            exit()

class Gui(object):
    '''
    Takes a Queue that holds tuples from the UDP listener:
    (side, boolean) where the first value is an integer and the second is a boolean
    '''
    def __init__(self, queue, handler):
        self.queue = queue
        self.handler = handler
        
        # keep track of current value, so we don't have to update GUI unless
        # things have changed
        self.left_pedestrian = False
        self.right_pedestrian = False
        
        
        self.root = Tk()
        # HUD dimensions
        self.root.geometry("848x480")
        # make window transparent
        self.root.attributes('-alpha', 0.3)
        
        self.none_image = PhotoImage(file = "images/none.gif")
        self.left_image = PhotoImage(file = "images/left.gif")
        self.right_image = PhotoImage(file = "images/right.gif")
        self.both_image = PhotoImage(file = "images/both.gif")
        self.label = Label(self.root, image = self.none_image)
        self.label.pack()
        self.updateGUI()

    def run(self):
        self.label.pack()
        self.label.after(1000, self.updateGUI)
        self.root.mainloop()

    draw(self):
        if(self.left_pedestrian and self.right_pedestrian):
            self.label.config(image = self.both_image)
        elif(self.left_pedestrian and not self.right_pedestrian):
            self.label.config(image = self.left_image)
        elif(not self.left_pedestrian and self.right_pedestrian):
            self.label.config(image = self.right_image)
        elif(not self.left_pedestrian and not self.right_pedestrian):
            self.label.config(image = self.none_image)
        self.root.update()
            
    def event_loop(self):
        try:
            # This will throw an Empty exception if the queue is empty,
            # where we sleep and try again in a few milliseconds
            (side, state) = queue.Queue.get_nowait()
            
            if (side == LEFT_SIDE_EVENT_NUM and state != self.left_pedestrian):
                self.left_pedestrian = state
                self.draw()
            elif (side == RIGHT_SIDE_EVENT_NUM and state != self.right_pedestrian):
                self.left_pedestrian = state
                self.draw()
            self.label.after(100, self.updateGUI)
        except Empty:
            self.label.after(100, self.updateGUI)

class SoundPlayer(object):
    @staticmethod
    def right():
        playsound('sounds/right.wav')
    @staticmethod
    def left():
        playsound('sounds/left.wav')
    @staticmethod
    def stereo():
        playsound('sounds/stereo.wav')
    
class AudioHandler(object):
    '''
    This handler only plays audio when a pedestrian is detected
    '''
    def handlePedestrians(left, right):
        if (left and right):
            SoundPlayer.stereo()
        elif left:
            SoundPlayer.left()
        elif right:
            SoundPlayer.right()

class VisualHandler(object):
    '''
    This handler displays arrows when a pedestrian is detected
    '''
    def handlePedestrians(left, right):
        if (left and right):
            SoundPlayer.stereo()
        elif left:
            SoundPlayer.left()
        elif right:
            SoundPlayer.right()
            
if __name__ == "__main__":
    queue = Queue()
    ThreadedUdpListener(queue).start()
    Gui(queue).run()
