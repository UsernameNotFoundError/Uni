from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from updateapp.DataBaseGenerator import SuperUpdate
from updateapp.my_functions import Test
import _thread
from datetime import datetime
import os
import pathlib
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def home_page(request):
    """
    other page
    """
    if  os.path.exists(SuperUpdate.UPDATE_FILES_DIR+'assembly_summary_refseq.txt'):
        last_update_date = datetime.fromtimestamp(
                        pathlib.Path(SuperUpdate.UPDATE_FILES_DIR+'assembly_summary_refseq.txt').stat().st_mtime)
    else:
        last_update_date = "an unknown date"
    return render(request, "updateapp/home_page.html", 
            {"last_update_date":last_update_date}
                    )


def after_update_page(request):
    """
    This is the page for fdog and cluster usage
    """
    if request.method == "POST":  # to lunch fdog
        pass  # RUN FUCTION HERE
        print(request.POST['fanta'].replace('\r\n','\n'))
        return HttpResponse("cluster is lunched! you can see the progress with \"squeue\" command")
    print("working! fdog")
    SLURM_SCRIPT = """
    #!/bin/bash
    #SBATCH --partition=all,pool,inteli7
    #SBATCH --account=praktikant
    #SBATCH --cpus-per-task=10
    #SBATCH --mem-per-cpu=3000mb
    #SBATCH --job-name="fdog_DB"
    #SBATCH --output=addTaxa_%A_%a.o.out
    #SBATCH --error=addTaxa_%A_%a.e.out
    #SBATCH --array=1-1000%4

    echo This is task $SLURM_ARRAY_TASK_ID

    SEED=$(awk "FNR==$SLURM_ARRAY_TASK_ID" /home/amine/Documents/Slurmrun/fdog_seed_1.csv)
    NAME=`echo $SEED |cut -d ',' -f 1`
    TAX=`echo $SEED |cut -d ',' -f 2`
    END=`echo $SEED |cut -d ',' -f 3`

    fdog.addTaxon -f /share/gluster/GeneSets/NCBI-Genomes/${NAME:4:3}/${NAME:7:3}/${NAME:10:3}/$NAME.$END/raw_dir/protein.faa -i $TAX -o /share/gluster/GeneSets/NCBI-Genomes/${NAME:4:3}/${NAME:7:3}/${NAME:10:3}/$NAME.$END/fdog -c --cpus 10 --replace -v $END
    """.replace("    ", "")
    return render(request, "updateapp/fdog_page.html", 
            {"slurm_script": SLURM_SCRIPT}
                    )


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
        print("checkpointing:", "my_global_instance" in globals().keys(), my_global_instance._job_done)
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