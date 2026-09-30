from pathlib import Path

import gradio as gr
from .transcribe import transcribe_audio
from .summarize import summarize_transcript

def process_audio(audio_path):
    if audio_path is None:
        return "Tidak ada file audio yang diunggah.", ""
    transcript = transcribe_audio(audio_path)
    summary = summarize_transcript(transcript)
    return transcript, summary

demo = gr.Interface(
    fn=process_audio,
    inputs=gr.Audio(type="filepath", label="Upload rekaman meeting"),
    outputs=[
        gr.Textbox(label="Hasil Transkripsi"),
        gr.Textbox(label="Ringkasan & Poin Penting"),
    ],
    examples=[[str(Path(__file__).with_name("audio_example.mp3"))]],
    cache_examples=False,
    title="Audio Transcription App",
    description="Upload file audio meeting untuk ditranskrip dan diringkas otomatis."
)

if __name__ == "__main__":
    demo.launch()