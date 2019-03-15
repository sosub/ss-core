from re import sub
from django.utils.timezone import now
from .models import Video, Profile


def convert(text):
    patterns = {
        '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
        '[đ]': 'd',
        '[èéẻẽẹêềếểễệ]': 'e',
        '[ìíỉĩị]': 'i',
        '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
        '[ùúủũụưừứửữự]': 'u',
        '[ỳýỷỹỵ]': 'y'
    }

    output = text
    for regex, replace in patterns.items():
        output = sub(regex, replace, output)
        # deal with upper case
        output = sub(regex.upper(), replace.upper(), output)
    return output


def name_to_slug(name):
    slug = sub('\W+', '-', convert(name).lower()).strip('-')

    return slug


def youtube_duration_to_second(duration):
    from re import search
    total_second = 0
    hours = search(r'(\d+)H', duration)
    minutes = search(r'(\d+)M', duration)
    seconds = search(r'(\d+)S', duration)
    
    if hours:
        total_second += int(hours.groups()[0])*3600
    if minutes:
        total_second += int(minutes.groups()[0])*60
    if seconds:
        total_second += int(seconds.groups()[0])

    return total_second

def get_permission(action, user, extras=None):
    if not user.is_active:
        return False

    if action in ['create_video', 'create_source', 'create_speaker', 'upload_file']:
        return user.profile.role in [
            Profile.POSTER, 
            Profile.MODERATOR,
            Profile.ADMINISTRATOR, 
        ]

    if action == 'update_video':
        return user.profile.role in [
            Profile.MODERATOR,
            Profile.ADMINISTRATOR,
        ] or (user.profile.role == Profile.POSTER and extras["video"].createdBy == user)

    if action in ['update_source', 'update_speaker', 'create_category', 'create_subcategory', 'publish_video']:
        return user.profile.role in [
            Profile.MODERATOR,
            Profile.ADMINISTRATOR, 
        ]

    if action == 'import':
        return user.is_staff