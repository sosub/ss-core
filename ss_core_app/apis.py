import uuid
import os
import requests

import boto3
from boto3.s3.transfer import TransferConfig

from django.http import JsonResponse, HttpResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes

from . import models
from .utils import youtube_duration_to_second, get_permission
from ss_core.settings import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_BUCKET, AWS_HOST, YOUTUBE_API_KEY


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
def get_user(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "username": request.user.username,
            "name": request.user.get_full_name(),
            "role": models.Profile.ROLES[request.user.profile.role],
        })
    else:
        return JsonResponse({
            "detail": "Not authorization."
        })


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
def upload_file(request):
    if get_permission('upload_file', request.user):
        try:
            client = boto3.client(
                "s3",
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
            )

            folder_path = request.POST.get('path', '')
            upload_file = request.FILES['upload_file']
            file_unique_name = os.path.join(folder_path, "%s.%s" % (str(uuid.uuid4()), str(upload_file).split(".")[-1]))

            client.upload_fileobj(
                upload_file,
                AWS_BUCKET,
                file_unique_name,
                ExtraArgs={
                    'ACL':'public-read',
                    "Metadata": {
                        "uploader": request.user.username
                    },
                    'ContentType': 'text/plain' if str(upload_file).split(".")[-1] == 'srt' else 'image/jpeg',
                },
            )
        except Exception as e:
            return JsonResponse({
                "is_success": False,
                "detail": str(e),
            })

        return JsonResponse({
            "is_success": True,
            "detail": os.path.join(AWS_HOST, AWS_BUCKET, file_unique_name)
        })
    else:
        return JsonResponse({
            "is_success": False,
            "detail": "Permission denied."
        })


def youtube_duration(request):
    try:
        response = requests.get('https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id=%s&key=%s'
                    % (request.GET['youtube_id'], YOUTUBE_API_KEY))
        duration = youtube_duration_to_second(response.json()['items'][0]['contentDetails']['duration'])
    except Exception as e:
        return JsonResponse({
            "detail": str(e) 
        })

    return JsonResponse({
        "duration": duration
    })
