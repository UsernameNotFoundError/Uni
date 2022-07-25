from django.http import HttpResponse
from django.shortcuts import render
from time import sleep
import _thread
from django.template import Context
from django.template import Template



class Test():

    def __init__(self):
        self.magic_counter = "nöooooo"
        self.refresh = 5


    def test(self):
        print("inside test")
        
        for i in range(10):
            print(i)
            self.magic_counter=str(i)
            #_thread.start_new_thread(self.oo, (i,))
            sleep(5)
        self.refresh = 9999999


    def oo(self, i):
        print("thread", i)
        render(self.request, "updateapp/abc.html", {"a": i})


if __name__=="__main__":
    print("Hello!")