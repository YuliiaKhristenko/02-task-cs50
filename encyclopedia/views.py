from django import forms 
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import util
from . import md2html

import random

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'size' : '40'}))
    content = forms.CharField(label="Content", widget=forms.Textarea( attrs={'size' : '80'} ))
    
class EditEntryForn(forms.Form):
        title = forms.CharField(label="Title", widget=forms.HiddenInput())
        content = forms.CharField(label="Content", widget=forms.Textarea(attrs={'size' : '80'}))

class SearchForm(forms.Form):
    q = forms.CharField(widget=forms.TextInput(attrs={'size' : '40'}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

#TODO: fix error method

def error(request):
    print("In views.error")
    if "e_title" not in request.session:
        print("e_title not in request.session. setting to empty str")
        request.session["e_title"] = ""

    if "e_src" not in request.session:
        print("e_src not in request.session. setting to empty str")
        request.session["e_src"] = ""

    print(f'got session e_title = {request.session["e_title"]}')
    return render (request, "encyclopedia/error.html", {
        "e_title": request.session["e_title"],
        "e_src": request.session["e.src"]
    })

def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data["q"]
            qu = q.upper()

            # List of all entries
            entry_titles = util.list_entries()
            fuzzy_matches = None
            for title in entry_titles:
                eu = title.upper()
                if qu == eu:
                    print (f"Rendering {title} page")
                    entry = util.get_entry(title)
                    return render(request, "encyclopedia/entry.html", {
                        "entry" : md2html.md2html(entry),
                        "title" : title
                    })
                elif eu.find(qu) > -1:
                    print(f"Found fuzzy in {title}")
                    if fuzzy_matches is None:
                        fuzzy_matches = []
                        fuzzy_matches.append(title)
            if len(fuzzy_matches) > 0:
                print("Got fuzzy matches")
                return render(request, "encyclopedia/search.html", {
                "entry_titles": fuzzy_matches,
                "q": q
                })
            else:
                return render(request, "encyclopedia/search.html", {
                "q": q
                })
    else: 
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })
        
def random_entry(request):
    entries = util.list_entries()
    limit = len(entries)
    r = random.randrange(limit)
    title = entries[r]
    return HttpResponseRedirect(reverse("entry", args=[title]))

def entry(request, title):
    print("In views.entry")
    if not request.path.startswith("/wikipedia"):
        return HttpResponseRedirect(f"wikipedia/{title}")
    
    # get entry content
    entry = util.get_entry(title)
    print(f"entry={entry}")
    #  show an error if no such entry
    if entry is None:
        #  setup session and show error page
        request.session["e_title"] = title
        print(f'set session e_title to {request.session["e_title"]}')
        print("redirecting...")
        return HttpResponseRedirect(reverse(f"error"))
    
    return render(request, "encyclopedia/entry.html", {
        "entry": md2html.md2html(entry),
        "title": title
    })

def add(request, title=""):
    print(f"In ADD with title '{title}'")

    if request.method == "POST":
        
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]

            # Check if an entry exists
            print(f"Form ADD was posted for title '{title}'")

            entry = util.get_entry(title)
            if entry is not None:
                print(f"Entry {title} exists")
                request.session["e_title"] = title
                request.session["e_src"] = "add"
                return HttpResponseRedirect(reverse(f"error"))

            content = form.cleaned_data["content"]
            f = open(f"entries/{title}.md", "w")
            f.write(content)
            f.close()
            request.session["result"] = "success"
            return HttpResponseRedirect(reverse("entry", args = [title]))
        else:
            return render(request, "encyclopedia/add.html", {
                "form": form
            })

    print ('Ready to show form: no such entry')
    return render(request, "encyclopedia/add.html", {
        "title" : title,
        "form": NewEntryForm(initial={'title': title})
        })
    
def edit(request, title=""):
    print("In edit")
    print(f'title={title}')
    if request.method == "POST":
        print('Form was posted')
        form = EditEntryForn(request.POST)
        if form.is_valid():
            print("Form is valid")
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            f = open(f"entries/{title}.md", "w")
            f.write(content)
            f.close()
            request.session["result"] = "success"
            return HttpResponseRedirect(reverse("entry", args = [title]))
        else:
            print("Form is NOT valid")
            return render(request, "encyclopedia/edit.html", {
                "form": form
            })
            
    print('Trying to show a form to edit entry')
    entry = util.get_entry(title)
    
    # Show an error page
    if entry is None:
        print(f"Couldn't get entry {title}")
        #  Setup
        request.session["e_title"] = title
        request.session["e_src"] = "edit"
        return HttpResponseRedirect(reverse(f"error"))
    
    print('Got entry to show form')
    return render(request, "encyclopedia/edit.html", {
        "title" : title,
        "form" : EditEntryForn(initial={'title': title, 'content' : entry})
    })
    
