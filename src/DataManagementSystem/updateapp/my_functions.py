from django.http import HttpResponse
from django.shortcuts import render
from time import sleep
import _thread
from django.template import Context
from django.template import Template



class Test():

    def __init__(self):
        self.magic_counter = "0"
        self.refresh = 2
        self._stop_me = False


    def test(self):
        print("inside test")
        
        for i in range(11):
            if self._stop_me:
                print("KAbooom")
                break
            print(i)
            self.magic_counter=str(i)
            #_thread.start_new_thread(self.oo, (i,))
            sleep(2)
        #sleep(1)
        self._stop_me = True
        self.refresh = 9999999
        return

    def oo(self, i):
        print("thread", i)
        render(self.request, "updateapp/abc.html", {"a": i})


if __name__=="__main__":
    print("Hello!")