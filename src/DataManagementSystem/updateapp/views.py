from django.shortcuts import render
from django.http import HttpResponse
from updateapp.DataBaseGenerator import SuperUpdate
from updateapp.my_functions import Test
import _thread


def first_page(request):
    """
    first page
    """
    return render(request, "updateapp/progress_page.html")

def home_page(request):
    """
    other page
    """
    print("test")
    if request.method == 'POST':
        print("HERE =>>>>>", request.POST)
        print("\nwow =>>>>>", request.FILES)
        print("plop: >>", request.FILES['files_list'])
        mm = request.FILES['files_list']
        my_files = []
        # Problem here
        for f in request.FILES.getlist('files_list'):
            my_files += f
        print("checkpoint:", my_files)
        
    return render(request, "updateapp/home_page.html")


def test_page(request):
    if request.user.is_superuser:
        HttpResponse("Work in progress!")
        Tt = SuperUpdate()
    else: 
        return HttpResponse("Unauthorised access !")
    
    return HttpResponse("This is a celary testing page please take a look at the terminal!")


def a_dance_the_devil(request):
    """
    A funtions that intiliases an instance at the first run 
    and use 
    """
    try:
        step_indicator = my_global_instance.magic_counter
        return render(request, "updateapp/abc.html", {"step_indicator": step_indicator, "stop":my_global_instance.refresh})
    except NameError:
        # exec is used to avoid: "variable referenced before assignment" 
        """exec("global my_global_instance", globals())
        exec("my_global_instance = Test()", globals())
        exec("_thread.start_new_thread(my_global_instance.test, ())", globals())

        """
        exec(
        """
            global my_global_instance
            my_global_instance = Test()
            _thread.start_new_thread(my_global_instance.test, ())
        """.replace('  ', ''), globals())
        
        step_indicator = my_global_instance.magic_counter
        return render(request, "updateapp/abc.html", {"step_indicator":step_indicator , "stop":my_global_instance.refresh})
    except:
        print("Fatal error")
        return HttpResponse("Fatal Error while updating!")