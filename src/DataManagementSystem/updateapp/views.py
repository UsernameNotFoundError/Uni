from django.shortcuts import render
from django.http import HttpResponse
from updateapp.DataBaseGenerator import SuperUpdate
from updateapp.my_functions import Test
import _thread
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def first_page(request):
    """
    first page
    """
    if not request.user.is_superuser:
        print("ping")
        return render(request, "mainapp/home_page.html")
    return render(request, "updateapp/progress_page.html")


@staff_member_required
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


@staff_member_required
def test_page(request):
    if request.user.is_superuser:
        HttpResponse("Work in progress!")
        Tt = SuperUpdate()
    else: 
        return HttpResponse("Unauthorised access !")
    
    return HttpResponse("This is a celary testing page please take a look at the terminal!")


@staff_member_required
def update_view(request):
    """
    A funtions that intiliases an instance at the first run 
    and use 
    """
    if request.method == "POST":
        print("stop open request")
        my_global_instance._stop_me = True
    try:
        step_indicator = my_global_instance.updating_status
        html_print = my_global_instance.html_print
        if step_indicator >= 100 or my_global_instance._stop_me :  # Stop refresh
            print("COla")
            exec("del(globals()['my_global_instance'])")
            refresh_page = False
        else:
            refresh_page = not my_global_instance._stop_me
        return render(request, "updateapp/update_page.html", {
                                                            "step_indicator": step_indicator, 
                                                            "stop":refresh_page,
                                                            "updating_status": html_print})
    except NameError:
        # exec is used to avoid: "variable referenced before assignment" 
        exec(
        """
            global my_global_instance
            my_global_instance = SuperUpdate()
            _thread.start_new_thread(my_global_instance._start_update, ())
        """.replace('  ', ''), globals())
        
        step_indicator = my_global_instance.updating_status
        refresh_page = not my_global_instance._stop_me
        return render(request, "updateapp/update_page.html", {
                                                            "step_indicator": step_indicator, 
                                                            "stop":refresh_page,
                                                            "updating_status": my_global_instance.html_print})
    except Exception as e:
        print("Fatal error", e)
        return HttpResponse("Fatal Error while updating!")