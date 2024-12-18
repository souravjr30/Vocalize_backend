from summarizer import TextSummarizer
from tts_engine import TTSEngine
#import speech_recognition as sr
import whisper
from pydub import AudioSegment
import os
import yt_dlp as youtube_dl
import subprocess
from translator import translate_text
from fpdf import FPDF
import fitz  # PyMuPDF

def convert_mp3_to_wav(mp3_path):
    audio = AudioSegment.from_mp3(mp3_path)
    wav_path = os.path.splitext(mp3_path)[0] + ".wav"
    audio.export(wav_path, format="wav")
    return wav_path

def transcribe_audio_to_text(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def stream_audio_from_youtube(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0'  # Bind to IPv4 since IPv6 addresses cause issues sometimes
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        for f in info_dict['formats']:
            if 'acodec' in f and 'vcodec' in f and f['acodec'] != 'none' and f['vcodec'] == 'none':
                audio_url = f['url']
                return audio_url
    return None

def extract_audio_from_video(video_path):
    wav_path = os.path.splitext(video_path)[0] + ".wav"
    command = [
        'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', wav_path
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during ffmpeg execution: {e}")
        return None
    return wav_path

def save_to_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def main():
    # Initialize components
    summarizer = TextSummarizer()
    tts_engine = TTSEngine()
    speaker_wav_path = r"C:\Users\soura\Demo\AI.wav"
    
    # Prompt user for input method
    print("Prompting user for input method...")
    choice = input("Enter '1' to input text, '2' to upload an audio file, '3' to input a YouTube link, '4' to upload a video file, or '5' to upload a PDF file: ")
    print(f"User choice: {choice}")
    
    if choice == '1':
        # Prompt user for input text
        text = input("Enter the text you want to summarize: ")
    elif choice == '2':
        # Prompt user for audio file path
        audio_path = input("Enter the path to the audio file: ")
        print("Converting MP3 to WAV...")
        wav_path = convert_mp3_to_wav(audio_path)
        text = transcribe_audio_to_text(wav_path)
    elif choice == '3':
        # Prompt user for YouTube link
        youtube_url = input("Enter the YouTube link: ")
        print("Streaming audio from YouTube...")
        audio_url = stream_audio_from_youtube(youtube_url)
        
        if audio_url is None:
            print("Failed to extract audio URL from YouTube link.")
            return
        
        # Use ffmpeg to stream and convert audio to wav
        wav_path = "youtube_audio.wav"
        command = [
            'ffmpeg', '-loglevel', 'error', '-i', audio_url, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', wav_path
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during ffmpeg execution: {e}")
            return
        
        text = transcribe_audio_to_text(wav_path)
    elif choice == '4':
        # Prompt user for video file path
        video_path = input("Enter the path to the video file: ")
        print("Extracting audio from video...")
        wav_path = extract_audio_from_video(video_path)
        if wav_path is None:
            print("Failed to extract audio from video file.")
            return
        text = transcribe_audio_to_text(wav_path)
    elif choice == '5':
        # Prompt user for PDF file path
        pdf_path = input("Enter the path to the PDF file: ")
        print("Extracting text from PDF...")
        text = extract_text_from_pdf(pdf_path)
    else:
        print("Invalid choice")
        return
    
    # Generate summary
    print("Generating summary...")
    summary = summarizer.summarize(text)
    print(f"\nSummary: {summary}\n")
    
    # Prompt user for output method
    output_choice = input("Enter '1' for text-to-speech, '2' for language translation, '3' to save as PDF file: ")
    if output_choice == '1':
        # Convert summary to speech
        print("Converting to speech...")
        audio_filepath = tts_engine.text_to_speech(summary, speaker_wav=speaker_wav_path)
        if audio_filepath:
            print(f"Audio saved as: {audio_filepath}\n")
            # Play the audio
            print("Playing audio...")
            tts_engine.play_audio(audio_filepath)
    elif output_choice == '2':
        # Language options
        languages = {
            '1': ('Arabic', 'ar'),
            '2': ('Chinese (Simplified)', 'zh-cn'),
            '3': ('Czech', 'cs'),
            '4': ('Dutch', 'nl'),
            '5': ('English', 'en'),
            '6': ('French', 'fr'),
            '7': ('German', 'de'),
            '8': ('Hindi', 'hi'),
            '9': ('Italian', 'it'),
            '10': ('Japanese', 'ja'),
            '11': ('Kannada', 'kn'),
            '12': ('Korean', 'ko'),
            '13': ('Malayalam', 'ml'),
            '14': ('Russian', 'ru'),
            '15': ('Spanish', 'es'),
            '16': ('Tamil', 'ta'),
            '17': ('Telugu', 'te')
        }
        
        # Display language options
        print("Select the target language:")
        for key, (language, code) in languages.items():
            print(f"{key}: {language}")
        
        # Prompt user for target language
        language_choice = input("Enter the number corresponding to the target language: ")
        if language_choice in languages:
            target_language = languages[language_choice][1]
            translated_summary = translate_text(summary, target_language)
            print(f"\nTranslated Summary: {translated_summary}\n")
            
            # Convert translated summary to speech
            print("Converting translated summary to speech...")
            audio_filepath = tts_engine.text_to_speech(translated_summary, speaker_wav=speaker_wav_path)
            if audio_filepath:
                print(f"Audio saved as: {audio_filepath}\n")
                # Play the audio
                print("Playing audio...")
                tts_engine.play_audio(audio_filepath)
    elif output_choice == '3':
        # Save summary to PDF file
        pdf_filename = input("Enter the filename for the PDF file (without extension): ") + ".pdf"
        save_to_pdf(summary, pdf_filename)
        print(f"Summary saved as PDF file: {pdf_filename}")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()