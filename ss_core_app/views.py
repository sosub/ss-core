from django.shortcuts import render, redirect
from .models import Video

def faq(request):
    return render(request, 'faq.html', {})


def give(request):
    return render(request, 'give.html')


def join(request):
    return render(request, 'join.html')
    

def gop_y(request):
    return redirect('https://docs.google.com/forms/d/e/1FAIpQLScg_huxaarq-Xn9nZ7BxyAAJdnYl37mu0jhdIDv9xbFMCOh0g/viewform')
    
    
def dich_thuat(request):
    return redirect('https://spiderum.com/bai-dang/SOSUB-Huong-dan-lam-phu-de-1-Loi-noi-dau-76h')


def video_list(request):
    videos = Video.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'video_list.html', {"videos": videos})
