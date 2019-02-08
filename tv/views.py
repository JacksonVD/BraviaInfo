from django.shortcuts import render
from tv.models import Commands
from django.shortcuts import redirect
from django.contrib import messages
from multiprocessing.pool import ThreadPool

# Home page view
def home(request):
    return render(request, 'home.html')

# Runs setPower command when power change form is submitted, then returns home
def setPower(request):
    IP = request.GET['tvinfo'].split("=")[1].split("&")[0]
    PSK = request.GET['tvinfo'].split("&")[1].split("=")[1].replace("/", "")
    Commands().setPower(IP, PSK)

    return redirect('/tvinfo?IP=' + IP + "&PSK=" + PSK)

# Runs setVolume command when volume change form is submitted, then returns home
def setVolume(request):
    IP = request.POST.get("tvinfo", "").split("=")[1].split("&")[0]
    PSK = request.POST.get("tvinfo", "").split("&")[1].split("=")[1].replace("/", "")
    Commands().setVolume(request.POST.get("volinput", ""), IP, PSK)

    return redirect('/tvinfo?IP=' + IP + "&PSK=" + PSK)

# Runs setVolume command when volume change form is submitted, then returns home
def setSource(request):
    IP = request.POST.get("tvinfo", "").split("=")[1].split("&")[0]
    PSK = request.POST.get("tvinfo", "").split("&")[1].split("=")[1].replace("/", "")
    Commands().setSource(request.POST.get("newsource", ""), IP, PSK)

    return redirect('/tvinfo?IP=' + IP + "&PSK=" + PSK)

# Runs setApp command when application change form is submitted, then returns home
def setApp(request):
    IP = request.POST.get("tvinfo", "").split("=")[1].split("&")[0]
    PSK = request.POST.get("tvinfo", "").split("&")[1].split("=")[1].replace("/", "")
    Commands().setApp(request.POST.get("newapp", ""), IP, PSK)

    return redirect('/tvinfo?IP=' + IP + "&PSK=" + PSK)

# Runs sendIRCC command when IRCC execution form is submitted, then returns home
def sendIRCC(request):
    IP = request.POST.get("tvinfo", "").split("=")[1].split("&")[0]
    PSK = request.POST.get("tvinfo", "").split("&")[1].split("=")[1].replace("/", "")
    # Allows multiple IRCC commands to be run - splits on comas
    for ircc in request.POST.get("newircc", "").split(","):
        Commands().sendIRCC(ircc, IP, PSK)

    return redirect('/tvinfo?IP=' + IP + "&PSK=" + PSK)

def getInfo(request):
    IP = request.GET['IP']
    PSK = request.GET['PSK']
    pool = ThreadPool(processes=7)
    try:
        networkThread = pool.apply_async(func=Commands().getNetwork, args=(IP, PSK))
        getnetwork = networkThread.get()
    except:
        if not IP:
            messages.error(request, "Please enter an IP address")
        else:
            messages.error(request,"Could not establish connection with " + IP)
        return redirect('home')

    # Grab all the dynamic content by running the various commands, and return them
    # I just wanted to experiment with a thread pool, not really sure if it makes any difference to the speed, plus
    # who knows how scalable it'll be

    sourceThread = pool.apply_async(func=Commands().getCurrent, args=(IP, PSK))
    allSourcesThread = pool.apply_async(func=Commands().getSources, args=(IP, PSK))
    volumeThread = pool.apply_async(func=Commands().getVolume, args=(IP, PSK))
    applicationsThread = pool.apply_async(func=Commands().getApplications, args=(IP, PSK))
    timeThread = pool.apply_async(func=Commands().getTime, args=(IP, PSK))
    modelThread = pool.apply_async(func=Commands().getModelInfo, args=(IP, PSK))

    getsource = sourceThread.get()
    getall = allSourcesThread.get()
    getvolume = volumeThread.get()
    getapplications = applicationsThread.get()
    gettime = timeThread.get()
    getmodel = modelThread.get()

    getcontrols = Commands().getControls(IP, PSK)
    gettv = Commands().getTV(IP, PSK)

    # Render the home page
    return render(request, 'tvinfo.html', {'getSource': getsource, 'getAll': getall, 'getVolume': getvolume,
                                          'getApplications': getapplications, 'getTime': gettime, 'getModel': getmodel,
                                          'getNetwork': getnetwork, 'getControls': getcontrols, 'getTV': gettv})

def sendKeyboard(request):
    IP = request.POST.get("tvinfo", "").split("=")[1].split("&")[0]
    PSK = request.POST.get("tvinfo", "").split("&")[1].split("=")[1].replace("/", "")
    kb = request.POST.get("kbcommand", "")
    Commands().sendKeyboard(kb, IP, PSK)

    return redirect('/tvinfo?IP=' + IP + "&PSK=" + PSK)