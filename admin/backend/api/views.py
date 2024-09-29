from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import LectureMaterial
from .serializer import LectureMaterialSerializer
import mysql.connector
import librosa
import io
import torch
from whisper import load_model, log_mel_spectrogram
from django.conf import settings
from dotenv import load_dotenv
import os
import pandas as pd
import shutil
import pinecone
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from .multimodal_rag import transcribe_audio_files, process_all_pdfs, generate_captions_for_images, create_documents_from_captions, process_videos_in_directory, text_preprocess, update_metadata, save_doc, process_mentor_files
load_dotenv()

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
            lecture_material = serializer.save() 
            file_id = lecture_material.id

            file.name = str(file_id) + "-" + file.name
            print(file.name)

            if file_name.endswith((".m4a", ".mp3", ".webm", ".wav", ".mpeg", ".ogg", ".opus", ".flac")):
                audio_files.append((file, file.name))
            if file_name.endswith(".pdf"):
                pdf_files.append(file)
                text_files.append(file)
            if file_name.endswith((".mp4", ".avi", ".mov", ".mkv", ".webm", ".mpeg", ".ogg")):
                video_files.append(file)
            if file_name.endswith((".docx", ".txt", ".html", ".md", ".epub", ".pptx", ".csv", ".xlsx", ".ipynb", ".py", ".xml")):
                text_files.append(file)

            responses.append(serializer.data)

        else:
            responses.append(serializer.errors)

    ############## Audio ###############

    if audio_files:
        for file, file_name in audio_files:
            file_content = file.read()
            # audio, sr = librosa.load(io.BytesIO(file_content), sr=None)
            converted_audio_files.append((file_content, file_name))

        transcribed_audio_files = transcribe_audio_files(converted_audio_files, course, subject)

    
    ############## Images ###############
    
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
    extracted_images_dir = os.path.join(settings.MEDIA_ROOT, 'extracted_images')

    if os.path.exists(pdf_dir):
        shutil.rmtree(pdf_dir)

    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(extracted_images_dir, exist_ok=True) 

    for file in pdf_files:
        file_path = os.path.join(pdf_dir, file.name)
        with open(file_path, 'wb') as f:
            f.write(file.read())

    process_all_pdfs(pdf_dir, extracted_images_dir)

    captions = generate_captions_for_images(extracted_images_dir)
    pdf_image_captions = create_documents_from_captions(captions, course, subject)


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
    
    # Step 3: Check for .mp4 files and process them as audio
    converted_audio_files = []

    # Open and check if any video file is .mp4
    for file in os.listdir(video_dir):
        file_path = os.path.join(video_dir, file)

        if file.endswith(".mp4"):
            # Open the .mp4 file as binary
            with open(file_path, 'rb') as f:
                file_content = f.read()

                # If you need to directly process it, add to converted_audio_files
                converted_audio_files.append((file_content, file))

    # Step 4: Transcribe audio from .mp4 files
    transcribed_video_files = transcribe_audio_files(converted_audio_files, course, subject)


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
        for doc in transcribed_video_files:
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

# @api_view(["DELETE"])
# def delete_material(request, pk):
#     try:
#         material = LectureMaterial.objects.get(pk=pk)
#     except LectureMaterial.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
    
#     # material.file.delete(save=False)
#     material.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)


pc = Pinecone(
        api_key=os.getenv("PINECONE_API_KEY")
    )

# Set your Pinecone index name
INDEX_NAME = os.getenv("PINECONE_INDEX")

@api_view(["DELETE"])
def delete_material(request, pk):
    try:
        # Retrieve and delete the material from the database
        material = LectureMaterial.objects.get(pk=pk)
    except LectureMaterial.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Delete the material from the database
    material.delete()

    # Initialize Pinecone index
    index = pc.Index(INDEX_NAME)

    # Step 1: Retrieve relevant IDs from Pinecone
    ids_to_delete = []
    print("document id: ", pk)

    try:
        query_response = index.query(
            vector=[0] * 768, # [0,0,0,0......0]
            filter={"id": pk},  # Adjust filter criteria if necessary
            top_k=10000,  # Adjust based on your requirements
            include_metadata=False  # Only need IDs, not metadata
        )
        ids_to_delete = [match.id for match in query_response.matches]
        print("no. of vectors: ",len(ids_to_delete))
        
    except Exception as e:
        return Response({"error": f"Error querying Pinecone: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Step 2: Delete vectors from Pinecone
    if ids_to_delete:
        try:
            index.delete(ids=ids_to_delete)
        except Exception as e:
            return Response({"error": f"Error deleting vectors from Pinecone: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def add_mentor_notes(request):
    # Retrieve data from the POST request
    mentor_id = request.data.get('mentorid')
    student_id = request.data.get('studentid')
    course = request.data.get('course')
    notes = request.data.get('notes')
    files = request.FILES.getlist('files')

    print(mentor_id, student_id, course, notes)
    
    mentor_files = []

    for file in files:
        file_name = file.name

        if file_name.endswith((".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")):
            mentor_files.append(file)

    mentor_files_dir = os.path.join(settings.MEDIA_ROOT, 'mentorFiles')
    os.makedirs(mentor_files_dir, exist_ok=True)  # Create the textFiles directory if it doesn't exist

    for file in mentor_files:
        file_path = os.path.join(mentor_files_dir, file.name)
        with open(file_path, 'wb+') as f:
            for chunk in file.chunks():
                    f.write(chunk)

    transcriptions, preprocessed_text = process_mentor_files(mentor_files_dir)

    # Combine texts from both lists and add notes
    combined_text = notes + "\n\n" + "\n".join(transcriptions.values()) + "\n".join([doc.page_content for doc in preprocessed_text])

    if os.path.exists(mentor_files_dir):
        shutil.rmtree(mentor_files_dir)

    # Validate the inputs
    if not mentor_id or not student_id or not course or not notes:
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Connect to the MySQL database
        db = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB")
        )

        # Create a cursor object to execute SQL queries
        cursor = db.cursor()

        # Insert the mentor notes into the mentor_notes table
        query = """
            INSERT INTO mentor_notes (mentorid, studentid, course, notes)
            VALUES (%s, %s, %s, %s)
        """
        values = (mentor_id, student_id, course, combined_text)
        cursor.execute(query, values)

        # Commit the transaction
        db.commit()

        # Close the connection
        cursor.close()
        db.close()

        # Return a success response
        return Response({
            "message": "Mentor notes added successfully", 
            "combined_text": combined_text, 
            "mentor_id": mentor_id, 
            "student_id": student_id, 
            "course": course
        }, status=status.HTTP_201_CREATED)

    except mysql.connector.Error as e:
        # Handle any errors that occur during database interaction
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)