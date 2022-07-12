from django.shortcuts import render
from mainapp.forms import UserLoginForm, UserProfileInfoForm
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth.decorators import login_required
#from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from mainapp.brain import BigBrain
from mainapp.models import Searchresults, Searchregister

# Create your views here.
@login_required
def _test_page(request, my_query="nope", what_is_checked="0123456"):
    """test page to try things out"""
    if my_query:  # Check is a search querry is given
        print("NEWWWWWWWWWWWWWWWWWWWWWW ----------------------------------------------------------------------------")
        MySearch = BigBrain(request.user)
        MySearch.look_for_this(my_query, list(what_is_checked))
        results_paginator = Paginator(MySearch.search_results, 10)  # Shows 10 results per page
        #print("range paginator", results_paginator.num_pages, results_paginator.num_pages)
        page_number = int( request.GET.get('page') if request.GET.get('page') is not None else 1 )
        #print("Test paginator: ",   MySearch.html_paginator_bar_generator(page_number, results_paginator.num_pages))
        #print("My paginator results\n:", results_paginator.get_page(1))
        my_results_dict = {
                'search_querry':my_query, 
                "my_search_results": results_paginator.page(page_number), 
                "my_search_collumns": MySearch.column_maker(), 
                "my_search_path_results": MySearch.get_only_mysql_rslt_path(),
                "page_pagination_bar": MySearch.html_paginator_bar_generator(page_number, results_paginator.num_pages)
                }
        
        return render(request,"mainapp/test_page.html", my_results_dict)
    else:
        print("Empty search querry given...")
        
    return render(request, "mainapp/test_page.html", {"search_querry":my_query})


@login_required
def home_page(request, notfound404=None):
    """Main page after user is logged in"""
    return render(request, "mainapp/home_page.html")


@login_required
def my_space(request):
    """Reworked my_space after user is logged in"""
    print(request.POST)
    searchregister_object = Searchregister.objects.filter(user_id=request.user.id).order_by("-date_of_the_experiment")
    MY_SEARCH_COLLUMNS = ['Date', 'Query']
    MY_RESULTS_COLLUMNS = BigBrain(request.user).column_maker()
    if "search target" in dict(request.POST):
        print("wow", request.POST["search target"])
        search_target = request.POST["search target"]
        searchresults_object = Searchresults.objects.filter(search_id=search_target)
        paginator_searchresults = Paginator(searchresults_object, 10)
        page_number = int( request.GET.get('page') if request.GET.get('page') is not None else 1 )
    elif request.GET.get('target'):
        print(">>>>>>>>>>> worked!!!!!!!!!!!!!!!!!!!!", request.GET.get('target'))
        search_target = request.GET.get('target')
        print("oizer", request.GET)
        searchresults_object = Searchresults.objects.filter(search_id=search_target)
        paginator_searchresults = Paginator(searchresults_object, 10)
        page_number = int( request.GET.get('page') if request.GET.get('page') is not None else 1 )
    else:
        print("NO")
        search_target=""
        searchresults_object = []
        paginator_searchresults = Paginator(searchresults_object, 10)
        page_number = 1

    print("PAGEEEEEEEEEEEEEEEEEEEEEEEEEE : ", page_number)
    my_render_dict = {
            "my_searchs": searchregister_object,
            "my_search_collumns": MY_SEARCH_COLLUMNS,
            "my_results_object": paginator_searchresults.page(page_number),
            "my_results_collumns": MY_RESULTS_COLLUMNS,
            "page_pagination_bar": BigBrain(request.user).html_paginator_bar_generator(page_number, paginator_searchresults.num_pages),
            "object_target": search_target
            }

    return render(
            request,
            "mainapp/my_space_page.html",
            my_render_dict
            )


@login_required
def results_page(request,  my_query=""):
    """results page:
        accessible from search_page only
    """
    if len(my_query)<1:
        return HttpResponseRedirect(reverse('search_page'))
    searchresults_object = Searchresults.objects.filter(search_id=my_query)
    paginator_search_results = Paginator(searchresults_object, 10)
    page_number = int( request.GET.get('page') if request.GET.get('page') is not None else 1 )
    my_results_dict = {
            'search_querry': Searchregister.objects.filter(user_id=request.user.id, search_id=my_query).last().querry_used, 
            "my_search_results": paginator_search_results.page(page_number), 
            "my_search_collumns": BigBrain(request.user).column_maker(), 
            "my_search_path_results": [],
            "page_pagination_bar": BigBrain(request.user).html_paginator_bar_generator(page_number, paginator_search_results.num_pages)
            }
    return render(request,"mainapp/results_page.html", my_results_dict)


@login_required
def search_page(request):
    """search page:
        contains form
        the user can look for the wished files and add them to his personal Space (working)
    """
    print(request.user.id)
    if request.method == 'POST':
        my_request_dict = dict(request.POST)
        if "save_location" not in my_request_dict:
            my_search_querry = request.POST["search_querry"]
            if len(my_request_dict)>2:  # Check if something is checked
                if my_search_querry:  # Check is a search querry is given
                    MySearch = BigBrain(request.user)
                    MySearch.look_for_this(my_search_querry, my_request_dict["what_is_checked"])
                    # NEW
                    search_target = Searchregister.objects.filter(user_id=request.user.id, querry_used=my_search_querry).last()
                    return HttpResponseRedirect(reverse('results_page', args=(search_target,)))

    return render(request,"mainapp/search_page.html")


def sign_up_page(request):
    """
    sign up page
    """
    # Incase user is logged in
    if request.method == 'GET':
        if request.user.is_authenticated:  #Check if the user is already online
            return HttpResponseRedirect(reverse("home_page"))

    registered = False
    if request.method == 'POST':
        #print("youhou", request.POST)
        user_form = UserLoginForm(request.POST)
        profile_form = UserProfileInfoForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user

            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()
            registered = True

            # User auto login
            user_login = authenticate(
                    username=request.POST['username'],
                    password=request.POST['password']
                    )
            print(user_login)
            if user_login:
                if user_login.is_active:
                    login(request, user_login)
                    return HttpResponseRedirect(reverse("home_page"))

                else:
                    return HttpResponse("Account not active")
            else:
                print("someone tried to login and failed!")
                return HttpResponse("Invalid login details supplied")

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserLoginForm()
        profile_form = UserProfileInfoForm()
    return render(
        request,
        'mainapp/sign_up_page.html',
        {   'user_form': user_form,
            'profile_form': profile_form,
            'registered':registered
            }
    )


@login_required
def tree_search_page(request):
    """search page:
        contains form
        the user can look for the wished files
        and they will be automaatically added to his/her personal Space
    """
    pass  # To be programmed later

    return render(request,"mainapp/tree_search_page.html")


def user_login(request):
    if request.user.is_authenticated:  #Check if the user is already online
        return HttpResponseRedirect(reverse("home_page"))

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print("hi", password)
        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse("home_page"))

            else:
                return HttpResponse("Account not active")
        else:
            print("someone tried to login and failed!")
            return HttpResponse("Invalid login details supplied")
    else:
        return render(request, 'mainapp/login_page.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))