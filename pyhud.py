#!/usr/bin/env python

import threading
import socket
import argparse
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
        self.left_pedestrian = False
        self.right_pedestrian = False
        
    def push(self):
        queue.put( (self.left_pedestrian, self.right_pedestrian) )
    
    @staticmethod
    def crash_on_bad_response(event_num, event_state):
        if (event_num != LEFT_SIDE_EVENT_NUM and event_num != RIGHT_SIDE_EVENT_NUM):
            print("[+] ERROR: Event number not 1 or 2. It was " + str(event_num))
            exit()
        if (event_state != EVENT_STATE_TRUE and event_state != EVENT_STATE_FALSE):
            print("[+] ERROR: Event state not 1 or 0. It was " + str(event_state))
            exit()

    def maybe_queue_msg(self, event_num, event_state_bool):
        if (event_num == LEFT_SIDE_EVENT_NUM and self.left_pedestrian != event_state_bool):
            self.left_pedestrian = event_state_bool
            queue.put( (self.left_pedestrian , self.right_pedestrian ) )
        elif (event_num == RIGHT_SIDE_EVENT_NUM and self.right_pedestrian != right_pedestrian):
            self.right_pedestrian = event_state_bool
            queue.put( (self.left_pedestrian , self.right_pedestrian ) )

    def run(self):
        dyn_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dyn_sock.bind( ('0.0.0.0', 5007) )
        try:
            while True:
                dyn_data = dyn_sock.recvfrom(4)[0] # 142 values, each 4 bytes, + 640 values each 1 byte
                event_num = struct.unpack('s', dyn_data[0:2])[0] # little endian 0-4
                event_state = struct.unpack('s', dyn_data[2:4])[0]
                crash_on_bad_response(event_num, event_state)
                event_state_bool = false
                if (event_state == EVENT_STATE_TRUE):
                    event_state_bool = true
                self.maybe_queue_msg(event_num, event_state_bool)                
        except (KeyboardInterrupt, SystemExit):
            print("[+] Keyboard interrupt. Exiting.")
            raise

class Gui(object):
    '''
    Takes a Queue that holds tuples from the UDP listener:
    (side, boolean) where the first value is an integer and the second is a boolean
    '''
    def __init__(self, queue, graphics = True, audio = True, mono = False, debug = True):
        # Queue to communicate betweemn UDP listenter and the GUI
        self.queue = queue
        # True if the HUD should display arrows
        self.graphics = graphics
        # True if the HUD should play audio
        self.audio = audio
        # True if the HUD should play audio on left and right channels
        self.mono = mono
        
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
        self.label.after(0, self.self_test)
        self.root.mainloop()

    def maybe_draw(self, left_pedestrian, right_pedestrian):
        if (self.graphics):
            if (left_pedestrian and right_pedestrian):
                self.label.config(image = self.both_image)
            elif (left_pedestrian and not right_pedestrian):
                self.label.config(image = self.left_image)
            elif (not left_pedestrian and right_pedestrian):
                self.label.config(image = self.right_image)
            elif (not left_pedestrian and not right_pedestrian):
                self.label.config(image = self.none_image)
            self.root.update()

    def self_test(self):
        self.maybe_draw(True, False)
        self.label.after(500)
        self.maybe_draw(False, True)
        self.label.after(500)
        self.maybe_draw(True, True)
        self.label.after(500)
        self.maybe_draw(False, False)
        self.label.after(500)

        self.maybe_play_sound(True, False)
        self.label.after(3000)
        self.maybe_play_sound(False, True)
        self.label.after(3000)
        self.maybe_play_sound(True, True)
        
        self.label.after(3000, self.event_loop)

    def maybe_play_sound(self, left_pedestrian, right_pedestrian):
        if (self.audio):
            if (self.mono):
                if (left_pedestrian or right_pedestrian):
                    self.play_both()
            else: # self.stereo == true
                if (left_pedestrian and right_pedestrian):
                    self.play_both()
                elif (left_pedestrian and not right_pedestrian):
                    self.play_left()
                elif (not left_pedestrian and right_pedestrian):
                    self.play_right()
    @staticmethod
    def play_right():
        playsound('sounds/right.wav')

    @staticmethod
    def play_left():
        playsound('sounds/left.wav')

    @staticmethod
    def play_both():
        playsound('sounds/stereo.wav')

    def event_loop(self):
        print '[+] in event loop'
        try:
            (left_pedestrian, right_pedestrian) = queue.get(True, 1)
            if (self.debug):
                print("[+] Received notification left_pedestrian: {0!s} right pedestrian: {1!s}".format(left_pedestrian, right_pedestrian))
            self.maybe_draw(left_pedestrian, right_pedestrian)
            self.maybe_play_sound(left_pedestrian, right_pedestrian)
            self.label.after(1, self.event_loop)
        except Empty:
            self.label.after(1, self.event_loop)
        except (KeyboardInterrupt, SystemExit):
            print("[+] Keyboard interrupt. Exiting.")
            self.root.destroy()
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Heads-Up Display (HUD)', epilog="banana")
    parser.add_argument('--disable-audio',  dest='audio',    action='store_false', help='disable audio cues')
    parser.add_argument('--disable-visual', dest='graphics', action='store_false', help='disable visual cues')
    parser.add_argument('--mono-audio',     dest='mono',     action='store_true',  help='use mono audio cues')
    args = parser.parse_args()
    queue = Queue()
    ThreadedUdpListener(queue).start()
    Gui(queue, graphics = args.graphics, audio = args.audio, mono = args.mono)
