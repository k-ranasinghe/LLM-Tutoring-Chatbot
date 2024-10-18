import os
import time
from pydub import AudioSegment # type: ignore
from math import ceil
import base64
import tempfile
from langchain.schema import Document
import fitz # type: ignore
import google.generativeai as genai # type: ignore
import PIL.Image
from groq import Groq
from openai import OpenAI
import cv2 # type: ignore
from PIL import Image
import pytesseract # type: ignore
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma # type: ignore
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

# Load environment variables from .env file
load_dotenv()
# client = Groq(api_key=os.getenv('GROQ_API_KEY'))
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

######################### AUDIO ##########################
# Constants
MAX_FILE_SIZE_MB = 25
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to Bytes

def transcribe_audio_files(files_with_names, subject):
    documents = []

    for file, file_name in files_with_names:
        # Check the size of the audio file
        file_size = len(file)  # Assuming file is a NumPy array or similar in-memory representation

        if file_size <= MAX_FILE_SIZE_BYTES:
            # Process it directly
            transcription = transcribe_chunk(file, file_name)
        else:
            # Handle large audio files by splitting
            transcription = transcribe_large_audio(file, file_size, file_name)

        file_id, file_name = file_name.split('-', 1)
        print(transcription)
        document = Document(
            page_content=transcription,
            metadata={"subject": subject, "format": "audio", "source": file_name, "id": int(file_id)}
        )

        documents.append(document)

    return documents


def transcribe_chunk(file, file_name):
    """Transcribes a single audio chunk using the Whisper API."""
    transcription = client.audio.transcriptions.create(
        file=(file_name, file),  # Required audio file
        model="whisper-large-v3-turbo",
        response_format="json",
        language="en",
        temperature=0.0
    )
    
    return transcription.text


def transcribe_large_audio(file, file_size, file_name):
    """Handles larger audio files by splitting and transcribing each chunk."""
    
    # Check if file is a path or raw audio data
    if isinstance(file, bytes):
        # Save raw audio data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(file)
            temp_file_path = temp_file.name
    else:
        # Assume `file` is already a valid file path
        temp_file_path = file

    audio = AudioSegment.from_file(temp_file_path)  # Load audio from the file

    # Determine the length of the audio file in milliseconds
    audio_length_ms = len(audio)
    
    # Calculate chunk size
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
        with open(chunk_path, "rb") as chunk_file:
            chunk_transcription = transcribe_chunk(chunk_file.read(), chunk_path)

        # Append to the combined transcription
        combined_transcription += chunk_transcription + " "

        # Clean up the temporary file
        os.remove(chunk_path)

    # Clean up the temporary file if it was created
    if isinstance(file, bytes):
        os.remove(temp_file_path)

    return combined_transcription.strip()

######################### IMAGES ##########################

# def extract_images_from_pdf(pdf_path, output_dir):
#     # Open the PDF file
#     pdf_document = fitz.open(pdf_path)

#     # Ensure the output directory exists
#     os.makedirs(output_dir, exist_ok=True)

#     # Extract the PDF's base name without the extension
#     pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

#     # Iterate through each page in the PDF
#     for page_number in range(len(pdf_document)):
#         page = pdf_document.load_page(page_number)
#         images = page.get_images(full=True)

#         for img_index, img in enumerate(images):
#             xref = img[0]
#             base_image = pdf_document.extract_image(xref)
#             image_bytes = base_image["image"]
#             image_ext = base_image["ext"]
#             image_filename = f"{pdf_name}.pdf_{page_number+1}_img_{img_index+1}.{image_ext}"

#             # Save the extracted image to the output directory
#             with open(os.path.join(output_dir, image_filename), "wb") as img_file:
#                 img_file.write(image_bytes)

#     pdf_document.close()


def extract_images_from_pdf(pdf_path, output_dir, zoom=2):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract the PDF's base name without the extension
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Iterate through each page in the PDF
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)

        # Render the page to an image
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        
        # Define the output image filename
        image_filename = f"{pdf_name}_page_{page_number + 1}.png"

        # Save the rendered image to the output directory
        pix.save(os.path.join(output_dir, image_filename))

    # Close the PDF document
    pdf_document.close()

def process_all_pdfs(input_dir, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            print(f"Processing {pdf_path}")
            extract_images_from_pdf(pdf_path, output_dir)


# Step 1: Generate Captions for All Images in Output Directory
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
            gemini_counter += 1
            
            if gemini_counter < gemini_tpm_limit:
                # If the Gemini model can still process images
                response = gemini_model.generate_content(img)
                model_caption = response.text.strip()
                
                combined_caption = (f"Caption by pytesseract:\n{initial_caption}\n\n"
                                    f"Caption by model:\n{model_caption}")

                print(f"Gemini processed {gemini_counter} images.")
            else:
                # If Gemini reaches the cap, switch to Llama
                print(f"GPT-4o processed {gemini_counter - 13} images.")
                
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
                    model="gpt-4o-mini",
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

# Step 2: Create a Document with All Captions
def create_documents_from_captions(captions, subject):
    documents = []

    for image_filename, caption in captions:
        # Extracting the source file name and page number from the filename
        # Assuming the filename format is "source_file_page_1000_img_1.png"
        parts = image_filename.split('_')
        source_file = '_'.join(parts[:-2])  # This extracts the source file name
        page_number = parts[-1].split('.')[0]  # This extracts '1000' from 'page_1000_img_1.png'
        file_id, file_name = source_file.split('-', 1)

        document = Document(
            page_content=caption,
            metadata={"subject": subject, "format": "image", "source": file_name, "page": int(page_number), "img": image_filename, "id": int(file_id)}
        )
        documents.append(document)

    return documents

######################### VIDEOS ##########################

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
            img = Image.fromarray(frame_rgb)

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


def create_documents_from_frames(captions, subject):
    documents = []

    for image_filename, caption in captions.items():
        # Extracting the source file name, timestamp, and frame number from the filename
        # Assuming the filename format is "video_filename_time_XX.XX_frame_XXXX.png"
        parts = image_filename.split('_')
        video_filename = parts[0]  # Extract the source video file name
        timestamp = parts[-3]  # Extract timestamp
        frame_number = parts[-1].split('.')[0]  # Extract frame number
        file_id, file_name = os.path.basename(image_filename).split('-', 1)

        document = Document(
            page_content=caption,
            metadata={
                "subject": subject, 
                "format": "video",
                "source": file_name,
                "timestamp": timestamp,
                "frame": int(frame_number),
                "id": int(file_id)
            }
        )
        documents.append(document)

    return documents


def process_videos_in_directory(input_dir, output_dir_base, frame_rate, subject):
    documents=[]
    # Iterate over all video files in the input directory
    for video_filename in os.listdir(input_dir):
        if video_filename.endswith((".mp4", ".avi", ".mov", ".mkv")):  # Add other video formats if needed
            video_path = os.path.join(input_dir, video_filename)

            # Create a specific output directory for each video
            video_output_dir = os.path.join(output_dir_base, os.path.splitext(video_filename)[0])

            # Extract frames from the video
            extract_frames_from_video(video_path, video_output_dir, frame_rate)

            # Transcribe the frames
            transcriptions = transcribe_frames(video_output_dir)

            # Create documents with the required format
            document = create_documents_from_frames(transcriptions, subject)
            for doc in document:
                documents.append(doc)

    return documents

######################### DOCS ##########################


from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader, UnstructuredEPubLoader, UnstructuredExcelLoader, NotebookLoader, PythonLoader, SQLDatabaseLoader, UnstructuredXMLLoader
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    TextLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    CSVLoader,
    DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Define loaders for different file types

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



def update_metadata(documents, subject):
    updated_documents = []

    for doc in documents:
        # Access existing metadata
        updated_metadata = doc.metadata.copy()

        # Extract the filename from the file path
        file_path = doc.metadata.get("source", "")
        file_id, file_name = os.path.basename(file_path).split('-', 1)

        # Modify metadata as needed
        updated_metadata['subject'] = subject 
        updated_metadata['format'] = 'text'
        updated_metadata['source'] = file_name
        updated_metadata['page'] = doc.metadata.get("page", "")
        updated_metadata['id'] = int(file_id)


        # Create a new document with updated metadata
        updated_doc = Document(page_content=doc.page_content, metadata=updated_metadata)
        updated_documents.append(updated_doc)

    return updated_documents


def save_doc(documents):
    embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    # Create a Chroma instance
    chroma = Chroma(
        embedding_function=embeddings,
        persist_directory="../knowledge_base"  # Specify your directory for persistence
    )
    
    # Add documents to the Chroma vector store
    chroma.add_documents(documents)