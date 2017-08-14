def csrf_exempt(view):
    view.csrf_exempt = True
    return view
