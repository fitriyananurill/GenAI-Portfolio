import gradio as gr
from .logic import generate_caption

iface = gr.Interface(
    fn=generate_caption,
    inputs=gr.Image(type="pil"),
    outputs="text",
    title="Image Captioning with BLIP",
    description="Upload gambar untuk menghasilkan caption otomatis.",
)

if __name__ == "__main__":
    iface.launch(server_name="127.0.0.1", server_port=7860)