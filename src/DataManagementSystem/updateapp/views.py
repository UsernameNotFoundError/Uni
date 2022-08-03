from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from updateapp.DataBaseGenerator import SuperUpdate
from updateapp.my_functions import Test
import _thread
from datetime import datetime
import pathlib
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def home_page(request):
    """
    other page
    """
    last_update_date = datetime.fromtimestamp(
                    pathlib.Path('/home/amine/UsernameNotFoundError/src/DataManagementSystem/updateapp/myupdatefiles/assembly_summary_refseq.txt').stat().st_mtime)

    return render(request, "updateapp/home_page.html", 
            {"last_update_date":last_update_date}
                    )


def after_update_page(request):
    """
    This is the page for fdog and cluster usage
    """
    return


@staff_member_required
def test_page(request):
    if request.method == 'GET':
        print(request.GET, len(request.GET.dict()))
    return HttpResponse("This is a celary testing page please take a look at the terminal!")


@staff_member_required
def update_view(request):
    """
    Update page 
    A funtions that creates a global instance at the first run 
    uses multithreading to update the data base while showing the progress at teh frontend
    """
    if request.method == "POST":
        print("stop open request")
        my_global_instance._stop_me = True
    try:
        step_indicator = my_global_instance.updating_status
        html_print = my_global_instance.html_print
        if step_indicator >= 100 or my_global_instance._stop_me :  # Stop refresh
            print("End Updating")
            exec("del(globals()['my_global_instance'])")
            refresh_page = False
        else:
            refresh_page = not my_global_instance._stop_me
        print("checkpointing:", step_indicator)
        return render(request, "updateapp/update_page.html", {
                                                            "step_indicator": step_indicator, 
                                                            "refresh":refresh_page,
                                                            "updating_status": html_print})
    except NameError:
        # exec is used to avoid: "variable referenced before assignment" 
        print("124, Here:", request.GET, request.GET['ignore_this_taxa'], request.GET['do_only_this_taxa'])
        if len(request.GET.dict())>1:
            ignore_this_taxa = request.GET['ignore_this_taxa']
            do_only_this_taxa = request.GET['do_only_this_taxa']
            print("baba", ignore_this_taxa, do_only_this_taxa)
            print('Initiation o the update thread')
            print("checkpoint 21547")
            exec("global my_global_instance\nmy_global_instance = SuperUpdate(ignore_this_taxa, do_only_this_taxa)")
            #my_global_instance = SuperUpdate(ignore_this_taxa, do_only_this_taxa)
            print("check_me", "my_global_instance" in globals().keys())
            _thread.start_new_thread(my_global_instance._start_update, ())
        else:
            exec(
            """
                print('Initiation o the update thread')
                global my_global_instance
                my_global_instance = SuperUpdate()
                _thread.start_new_thread(my_global_instance._start_update, ())
            """.replace('  ', ''), globals())
        
        step_indicator = my_global_instance.updating_status
        refresh_page = not my_global_instance._stop_me
        return render(request, "updateapp/update_page.html", {
                                                            "step_indicator": step_indicator, 
                                                            "refresh":refresh_page,
                                                            "updating_status": my_global_instance.html_print})
    except Exception as e:
        print("Fatal error", e)
        return HttpResponse("Fatal Error while updating!")