from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import LectureMaterial
from .serializer import LectureMaterialSerializer
import librosa
import io
import torch
from whisper import load_model, log_mel_spectrogram
from django.conf import settings
import os
import pandas as pd
import shutil

from .multimodal_rag import transcribe_audio_files, process_all_pdfs, generate_captions_for_images, create_documents_from_captions, process_videos_in_directory, text_preprocess, update_metadata, save_doc

# @api_view(["POST"])  # Correct: ["POST"] is a list of strings
# def upload_material(request):
#     files = request.FILES.getlist('files')  # Use 'files' to match the frontend key
#     if not files:
#         return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

#     responses = []
#     audio_files = []
#     converted_audio_files = []

#     for file in files:
#         file_name = file.name
#         file_type = file.content_type

#         # Create a new dictionary with the file data
#         data = {
#             'file': file,
#             'file_name': file_name,
#             'file_type': file_type,
#         }

#         # Initialize the serializer with the data
#         serializer = LectureMaterialSerializer(data=data)

#         if serializer.is_valid():
#             # serializer.save()
#             if file_name.endswith((".m4a", ".mp3", ".webm", ".mp4", ".mpga", ".wav", ".mpeg")):
#                 audio_files.append(file)

#             responses.append(serializer.data)
#         else:
#             responses.append(serializer.errors)
    
#     if audio_files:

#         for file in audio_files:
#             # Read the file content
#             file_content = file.read()
            
#             # Convert file content to a NumPy array using librosa
#             audio, sr = librosa.load(io.BytesIO(file_content), sr=None)
            
#             # Create a new InMemoryUploadedFile with the converted data (if needed)
#             # Here, we're assuming `transcribe_audio_files` expects raw audio data as NumPy array
#             converted_audio_files.append(audio)

#         transcribed_audio_files = transcribe_audio_files(converted_audio_files)
#         print(transcribed_audio_files)

#     if any(isinstance(response, dict) and 'error' in response for response in responses):
#         return Response(responses, status=status.HTTP_400_BAD_REQUEST)
    
#     return Response(responses, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def upload_material(request):
    files = request.FILES.getlist('files')
    if not files:
        return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    course = request.POST.get('course')
    subject = request.POST.get('subject')

    print(course, subject)

    responses = []

    audio_files = []
    converted_audio_files = []
    pdf_files = []
    video_files = []
    text_files = []

    for file in files:
        file_name = file.name
        file_type = file.content_type

        data = {
            'file': file,
            'file_name': file_name,
            'file_type': file_type,
        }

        serializer = LectureMaterialSerializer(data=data)

        if serializer.is_valid():
            if file_name.endswith((".m4a", ".mp3", ".webm", ".mp4", ".mpga", ".wav", ".mpeg")):
                audio_files.append((file, file_name))
            elif file_name.endswith(".pdf"):
                pdf_files.append(file)
                text_files.append(file)
            elif file_name.endswith((".mp4", ".avi", ".mov", ".mkv")):
                video_files.append(file)
            elif file_name.endswith((".docx", ".txt", ".html", ".md", ".c", ".epub", ".pptx", ".csv", ".xlsx", ".ipynb", ".py", ".xml")):
                text_files.append(file)

            responses.append(serializer.data)
        else:
            responses.append(serializer.errors)

    ############## Audio ###############

    if audio_files:
        for file, file_name in audio_files:
            file_content = file.read()
            audio, sr = librosa.load(io.BytesIO(file_content), sr=None)
            converted_audio_files.append((audio, file_name))

        transcribed_audio_files = transcribe_audio_files(converted_audio_files, course, subject)
        # print(transcribed_audio_files)

    
    ############## Images ###############

    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)  # Create the pdfs directory if it doesn't exist

    extracted_images_dir = os.path.join(settings.MEDIA_ROOT, 'extracted_images')
    os.makedirs(extracted_images_dir, exist_ok=True) 

    for file in pdf_files:
        file_path = os.path.join(pdf_dir, file.name)
        with open(file_path, 'wb') as f:
            f.write(file.read())

    process_all_pdfs(pdf_dir, extracted_images_dir)

    captions = generate_captions_for_images(extracted_images_dir)
    pdf_image_captions = create_documents_from_captions(captions, course, subject)
    # print(pdf_image_captions)


    ############## Video ###############

    video_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
    os.makedirs(video_dir, exist_ok=True)  # Create the videos directory if it doesn't exist

    for file in video_files:
        file_path = os.path.join(video_dir, file.name)
        with open(file_path, 'wb') as f:
            f.write(file.read())

    frame_dir = os.path.join(settings.MEDIA_ROOT, 'video_frames')
    os.makedirs(frame_dir, exist_ok=True) 

    frame_rate = 1
    proccessed_videos = process_videos_in_directory(video_dir, frame_dir, frame_rate, course, subject)
    # print(proccessed_videos)


    ############## Text ###############

    text_files_dir = os.path.join(settings.MEDIA_ROOT, 'textFiles')
    os.makedirs(text_files_dir, exist_ok=True)  # Create the textFiles directory if it doesn't exist

    for file in text_files:
        file_path = os.path.join(text_files_dir, file.name)
        with open(file_path, 'wb+') as f:
            for chunk in file.chunks():
                    f.write(chunk)

    preproccessed_text = text_preprocess(text_files_dir)
    # print(preproccessed_text)

    documents = update_metadata(preproccessed_text, course, subject)


    ############## Update Metadata ###############

    if audio_files:
        for doc in transcribed_audio_files:
            documents.append(doc)

    if pdf_files:
        for doc in pdf_image_captions:
            documents.append(doc)

    if video_files:
        for doc in proccessed_videos:
            documents.append(doc)

    print(len(documents))
    # print(documents)

    save_doc(documents)

    ############## Cleanup ###############

    # Remove the directories and their contents
    if os.path.exists(pdf_dir):
        shutil.rmtree(pdf_dir)
    if os.path.exists(extracted_images_dir):
        shutil.rmtree(extracted_images_dir)
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
    if os.path.exists(frame_dir):
        shutil.rmtree(frame_dir)
    if os.path.exists(text_files_dir):
        shutil.rmtree(text_files_dir)


    # RESPONSE

    if any(isinstance(response, dict) and 'error' in response for response in responses):
        return Response(responses, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(responses, status=status.HTTP_201_CREATED)
    


@api_view(["GET"])  # Correct: ["GET"] is a list of strings
def view_material(request):
    materials = LectureMaterial.objects.all()
    serializedData = LectureMaterialSerializer(materials, many=True).data
    return Response(serializedData)

@api_view(["GET"])
def view_recent_materials(request):
    materials = LectureMaterial.objects.order_by('-uploaded_at')[:5]  # Get 5 most recent files
    serializedData = LectureMaterialSerializer(materials, many=True).data
    return Response(serializedData)

@api_view(["GET"])
def search_materials(request):
    query = request.GET.get('q', None)
    if query:
        materials = LectureMaterial.objects.filter(file_name__icontains=query)
    else:
        materials = LectureMaterial.objects.all()
    serializedData = LectureMaterialSerializer(materials, many=True).data
    return Response(serializedData)

@api_view(["DELETE"])
def delete_material(request, pk):
    try:
        material = LectureMaterial.objects.get(pk=pk)
    except LectureMaterial.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    material.file.delete(save=False)
    material.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


