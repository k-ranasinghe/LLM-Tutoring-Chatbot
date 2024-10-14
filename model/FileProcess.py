import os
import shutil
import mimetypes
import time
from pydub import AudioSegment
from math import ceil
import PIL.Image
import pytesseract
import fitz
import cv2
import base64
from groq import Groq
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    TextLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    CSVLoader,
    DirectoryLoader, 
    PyPDFDirectoryLoader, 
    UnstructuredEPubLoader, 
    UnstructuredExcelLoader, 
    NotebookLoader, 
    PythonLoader, 
    UnstructuredXMLLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from fastapi import BackgroundTasks


# Load environment variables from .env file
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
chroma = Chroma(persist_directory="file_embeddings", embedding_function=embeddings)

def clear_vector_db():
    """Function to completely remove all embeddings from the vector database without deleting the collection."""
    
    # Get all documents and ensure they contain 'ids'
    documents = chroma.get()
    
    # Ensure 'ids' exists and proceed with deletion
    ids_to_delete = documents.get('ids', [])
    
    if ids_to_delete:
        # Delete the documents based on the ids
        chroma.delete(ids=ids_to_delete)
        print(f"Cleared {len(ids_to_delete)} vectors from the database.")
    else:
        print("No documents found to delete.")


def contents_reduce(contents, input_text):
    if len(contents) <= 5:
        return contents
    chroma.add_documents(contents)
    query_embedding = embeddings.embed_query(input_text)
    similar_vectors = chroma.similarity_search_by_vector(query_embedding, k=5)
    
    return similar_vectors

def create_documents(contents):
    documents = []
    for doc in contents:
        document = Document(page_content=contents[doc])
        documents.append(document)
    
    return documents

def process_file(file_path, input_text, background_tasks: BackgroundTasks):
    # Get the file's MIME type to determine its format
    mime_type, _ = mimetypes.guess_type(file_path)
    filename = os.path.basename(file_path)
    filename = filename.replace('uploads/', '', 1)
    
    # Check for audio files
    if mime_type and mime_type.startswith('audio'):
        transcript = transcribe_audio(file_path)
        return {"format": mime_type, "filename": filename, "transcription": transcript}
    
    # Check for image files (e.g., png, jpeg, etc.)
    elif mime_type and mime_type.startswith('image'):
        captions = extract_info_from_image(file_path)
        return {"format": mime_type, "filename": filename, "captions": captions}
    
    # Check for PDF (application/pdf)
    elif mime_type == 'application/pdf':
        all_captions = process_pdf(file_path)
        captions = contents_reduce(all_captions, input_text)
        all_documents = process_text_documents(file_path)
        documents = contents_reduce(all_documents, input_text)
        background_tasks.add_task(clear_vector_db)
        return {"format": mime_type, "filename": filename, "documents": documents, "image-captions": captions}
    
    # Check for video files (e.g., mp4)
    elif mime_type and mime_type.startswith('video'):
        all_captions = process_video(file_path)
        captions = contents_reduce(all_captions, input_text)
        transcript = transcribe_audio(file_path)
        background_tasks.add_task(clear_vector_db)
        return {"format": mime_type, "filename": filename, "transcription": transcript, "captions": captions}
    
    # Check for text files or documents
    elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/html', 'text/markdown', 'application/epub+zip',
                        'application/msword', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/xml',
                        'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'text/x-python', 'text/plain']:
        all_documents = process_text_documents(file_path)
        documents = contents_reduce(all_documents, input_text)
        background_tasks.add_task(clear_vector_db)
        return {"format": mime_type, "filename": filename, "documents": documents}

    else:
        return {"error": f"Unsupported file format: {mime_type}"}

######################### AUDIO PROCESSING ##########################
# Constants
MAX_FILE_SIZE_MB = 25
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to Bytes

def transcribe_audio(file_path):
    # Get the size of the file in bytes
    file_size = os.path.getsize(file_path)

    # If the file is within the 25 MB limit, process it directly
    if file_size <= MAX_FILE_SIZE_BYTES:
        return transcribe_chunk(file_path)

    # If the file exceeds the size limit, we need to split it
    else:
        return transcribe_large_audio(file_path, file_size)


def transcribe_chunk(file_path):
    """Transcribes a single audio chunk using the Whisper API."""
    with open(file_path, "rb") as audio_file:
        file_content = audio_file.read()
    transcription = client.audio.transcriptions.create(
        file=(os.path.basename(file_path), file_content),
        model="whisper-large-v3-turbo",
        response_format="json",
        language="en",
        temperature=0.0
    )
    
    return transcription.text


def transcribe_large_audio(file_path, file_size):
    """Handles larger audio files by splitting and transcribing each chunk."""
    audio = AudioSegment.from_file(file_path)

    # Determine the length of the audio file in milliseconds
    audio_length_ms = len(audio)
    
    # Calculate how many chunks we need based on the size limit
    # Estimate: average bitrate of MP3 files is about 1 MB per minute (depends on format)
    estimated_chunk_size_ms = (MAX_FILE_SIZE_BYTES / file_size) * audio_length_ms
    
    # Split the audio into chunks of size less than 25 MB
    num_chunks = ceil(audio_length_ms / estimated_chunk_size_ms)
    
    combined_transcription = ""

    for i in range(num_chunks):
        start_ms = i * estimated_chunk_size_ms
        end_ms = min((i + 1) * estimated_chunk_size_ms, audio_length_ms)
        
        # Extract the chunk
        chunk = audio[start_ms:end_ms]
        
        # Export the chunk to a temporary file
        chunk_path = f"temp_chunk_{i}.mp3"
        chunk.export(chunk_path, format="mp3")
        
        # Transcribe the chunk
        chunk_transcription = transcribe_chunk(chunk_path)
        
        # Append to the combined transcription
        combined_transcription += chunk_transcription + " "

        # Clean up the temporary file
        os.remove(chunk_path)

    return combined_transcription.strip()

######################### IMAGE PROCESSING ##########################
def extract_info_from_image(image_path):
    img = PIL.Image.open(image_path)

    # Extract text from the image using pytesseract
    initial_caption = pytesseract.image_to_string(img).strip()
    
    # with open(image_path, "rb") as image_file:
    #     img1 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # chat_completion = client.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": [
    #                 {"type": "text", "text": "What is in this image?"},
    #                 {
    #                     "type": "image_url",
    #                     "image_url": {
    #                         "url": f"data:image/jpeg;base64,{img1}",
    #                     },
    #                 },
    #             ],
    #         }
    #     ],
    #     model="llama-3.2-11b-vision-preview",
    # )
    
    # another_caption = chat_completion.choices[0].message.content
    
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(img)
    model_caption = response.text.strip()
    
    combined_caption = (f"Caption by pytesseract:\n{initial_caption}\n\n"
                        f"Caption by model:\n{model_caption}")
    
    return combined_caption

######################### PDF PROCESSING ############################
def extract_images_from_pdf(pdf_path, output_dir):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract the PDF's base name without the extension
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Iterate through each page in the PDF
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"{pdf_name}.pdf_{page_number+1}_img_{img_index+1}.{image_ext}"

            # Save the extracted image to the output directory
            with open(os.path.join(output_dir, image_filename), "wb") as img_file:
                img_file.write(image_bytes)

    pdf_document.close()


def generate_captions_for_images(output_dir):
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')

    captions = []
    gemini_counter = 0
    gemini_tpm_limit = 14  # Gemini model's 15 TPM limit
    timer_duration = 60  # 1 minute
    timer_start = time.time()
    
    def reset_gemini_counter():
        nonlocal gemini_counter
        gemini_counter = 0
        print("Gemini counter reset. You can now process another 15 images with Gemini.")
    
    
    # Iterate through each image file in the output directory
    for image_filename in sorted(os.listdir(output_dir)):
        image_path = os.path.join(output_dir, image_filename)

        # Ensure it's a file (not a subdirectory) and an image
        if os.path.isfile(image_path) and image_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            img = PIL.Image.open(image_path)
            initial_caption = pytesseract.image_to_string(img).strip()
            
            if gemini_counter < gemini_tpm_limit:
                # If the Gemini model can still process images
                response = gemini_model.generate_content(img)
                model_caption = response.text.strip()
                gemini_counter += 1

                combined_caption = (f"Caption by pytesseract:\n{initial_caption}\n\n"
                                    f"Caption by model:\n{model_caption}")

                print(f"Gemini processed {gemini_counter} images.")
            else:
                # If Gemini reaches the cap, switch to Llama
                print("Gemini model limit reached. Switching to Llama model.")
                
                # Convert image to base64 to pass to Llama
                with open(image_path, "rb") as image_file:
                    img_base64 = base64.b64encode(image_file.read()).decode('utf-8')

                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "What is in this image?"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{img_base64}",
                                    },
                                },
                            ],
                        }
                    ],
                    model="llama-3.2-11b-vision-preview",
                )
                
                llama_caption = chat_completion.choices[0].message.content
                combined_caption = (f"Caption by pytesseract:\n{initial_caption}\n\n"
                                    f"Caption by model:\n{llama_caption}")

            # Store the caption along with image reference
            captions.append((image_filename, combined_caption))

            # Check if the timer has reached one minute and reset the Gemini counter
            if time.time() - timer_start >= timer_duration:
                reset_gemini_counter()
                timer_start = time.time()  # Reset the timer start
                
    return captions


def process_pdf(pdf_path):
    output_dir = "extracted_images"
    extract_images_from_pdf(pdf_path, output_dir)
    captions = generate_captions_for_images(output_dir)
    documents = create_documents(captions)

    # Clean up the output directory. This directory was created to store the extracted images
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    return documents

######################### VIDEO PROCESSING ##########################
def extract_frames_from_video(video_path, output_dir, desired_fps=None):
    # Open the video file
    video_capture = cv2.VideoCapture(video_path)

    # Get the original FPS of the video
    original_fps = video_capture.get(cv2.CAP_PROP_FPS)

    # Calculate the exact number of frames to skip to match the desired FPS
    frame_interval = original_fps / desired_fps if desired_fps else 1

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract the video filename without extension
    video_filename = os.path.splitext(os.path.basename(video_path))[0]

    frame_count = 0
    extracted_count = 0  
    while True:
        # Read the next frame
        ret, frame = video_capture.read()
        if not ret:
            break

        # Calculate timestamp for the current frame
        timestamp = frame_count / original_fps  # in seconds

        # Extract frame based on the interval
        if frame_count >= extracted_count * frame_interval:
            # Convert frame to RGB (PIL expects RGB images)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image
            img = PIL.Image.fromarray(frame_rgb)

            # Save the frame as an image file with the desired format
            frame_filename = f"{video_filename}_time_{timestamp:.2f}_frame_{extracted_count:04d}.png"
            img.save(os.path.join(output_dir, frame_filename))
            extracted_count += 1

        frame_count += 1

    video_capture.release()
    print(f"Extracted {extracted_count} frames from {video_path} at {desired_fps or original_fps} FPS")


def transcribe_frames(input_dir):
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')

    transcriptions = {}
    gemini_counter = 0
    gemini_tpm_limit = 14  # Gemini model's 15 TPM limit
    timer_duration = 60  # 1 minute
    timer_start = time.time()
    
    def reset_gemini_counter():
        nonlocal gemini_counter
        gemini_counter = 0
        print("Gemini counter reset. You can now process another 15 images with Gemini.")

    # Iterate over all image files in the directory
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".png"):
            file_path = os.path.join(input_dir, filename)

            # Open the image
            img = PIL.Image.open(file_path)
            initial_caption = pytesseract.image_to_string(img).strip()

            if gemini_counter < gemini_tpm_limit:
                # If the Gemini model can still process images
                response = gemini_model.generate_content(img)
                model_caption = response.text.strip()
                gemini_counter += 1

                combined_caption = (f"Caption by pytesseract:\n{initial_caption}\n\n"
                                    f"Caption by model:\n{model_caption}")

                print(f"Gemini processed {gemini_counter} images.")
            else:
                # If Gemini reaches the cap, switch to Llama
                print("Gemini model limit reached. Switching to Llama model.")
                
                # Convert image to base64 to pass to Llama
                with open(file_path, "rb") as image_file:
                    img_base64 = base64.b64encode(image_file.read()).decode('utf-8')

                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "What is in this image?"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{img_base64}",
                                    },
                                },
                            ],
                        }
                    ],
                    model="llama-3.2-11b-vision-preview",
                )
                
                llama_caption = chat_completion.choices[0].message.content
                combined_caption = (f"Caption by pytesseract:\n{initial_caption}\n\n"
                                    f"Caption by model:\n{llama_caption}")

            # Store the transcription
            transcriptions[filename] = combined_caption
            
            # Check if the timer has reached one minute and reset the Gemini counter
            if time.time() - timer_start >= timer_duration:
                reset_gemini_counter()
                timer_start = time.time()  # Reset the timer start
    
    return transcriptions


def process_video(video_path):
    output_dir = "extracted_frames"
    extract_frames_from_video(video_path, output_dir, desired_fps=1)
    transcriptions = transcribe_frames(output_dir)
    documents = create_documents(transcriptions)
    
    # Clean up the output directory. This directory was created to store the extracted frames/images
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    return documents


######################### TEXT DOCUMENT PROCESSING ##################
def text_preprocess(input_dir):
    pdf_loader = PyPDFDirectoryLoader(input_dir)
    word_loader = DirectoryLoader(input_dir, glob="*.docx", loader_cls=UnstructuredWordDocumentLoader)
    text_loader = DirectoryLoader(input_dir, glob="*.txt", loader_cls=TextLoader)
    html_loader = DirectoryLoader(input_dir, glob="*.html", loader_cls=UnstructuredHTMLLoader)
    markdown_loader = DirectoryLoader(input_dir, glob="*.md", loader_cls=UnstructuredMarkdownLoader)
    epub_loader = DirectoryLoader(input_dir, glob="*.epub", loader_cls=UnstructuredEPubLoader)
    powerpoint_loader = DirectoryLoader(input_dir, glob="*.pptx", loader_cls=UnstructuredPowerPointLoader)
    csv_loader = DirectoryLoader(input_dir, glob="*.csv", loader_cls=CSVLoader)
    excel_loader = DirectoryLoader(input_dir, glob="*.xlsx", loader_cls=UnstructuredExcelLoader)
    notebook_loader = DirectoryLoader(input_dir, glob="*.ipynb", loader_cls=NotebookLoader)
    python_loader = DirectoryLoader(input_dir, glob="*.py", loader_cls=PythonLoader)
    xml_loader = DirectoryLoader(input_dir, glob="*.xml", loader_cls=UnstructuredXMLLoader)

    # Load documents from all loaders
    pdf_documents = pdf_loader.load()
    word_documents = word_loader.load()
    text_documents = text_loader.load()
    html_documents = html_loader.load()
    markdown_documents = markdown_loader.load()
    epub_documents = epub_loader.load()
    powerpoint_documents = powerpoint_loader.load()
    csv_documents = csv_loader.load()
    excel_documents = excel_loader.load()
    notebook_documents = notebook_loader.load()
    python_documents = python_loader.load()
    xml_documents = xml_loader.load()

    # Combine all documents
    all_documents = (
        pdf_documents + word_documents + text_documents + html_documents +
        markdown_documents + epub_documents + powerpoint_documents +
        csv_documents + excel_documents + notebook_documents +
        python_documents + xml_documents
    )

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = text_splitter.split_documents(all_documents)

    return documents


def process_text_documents(file_path):
    input_dir = os.path.dirname(file_path)
    documents = text_preprocess(input_dir)
    return documents

