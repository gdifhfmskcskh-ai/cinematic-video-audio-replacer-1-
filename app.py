import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
import streamlit as st


st.set_page_config(
    page_title="Cinematic Video Audio Replacer",
    page_icon="✨",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            linear-gradient(rgba(3, 7, 18, 0.65), rgba(3, 7, 18, 0.65)),
            url("https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?q=80&w=1920&auto=format&fit=crop")
            center center / cover fixed no-repeat;
        color: #ffffff;
    }

    .main .block-container {
        position: relative;
        z-index: 1;
        max-width: 1050px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    .glass-card {
        background: rgba(11, 15, 25, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 22px;
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.30),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }

    .hero-title {
        text-align: center;
        font-size: clamp(2rem, 5vw, 3.6rem);
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-bottom: 8px;
        color: #ffffff;
        text-shadow: 0 8px 30px rgba(0, 0, 0, 0.55);
    }

    .hero-subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.78);
        font-size: 1.05rem;
        margin-bottom: 30px;
    }

    .section-title {
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .stApp, .stApp p, .stApp label, .stApp span, .stApp div {
        color: #ffffff;
    }

    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
        min-height: 52px;
        border: none !important;
        border-radius: 14px !important;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.28);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 35px rgba(168, 85, 247, 0.38);
        color: #ffffff !important;
    }

    .stButton > button *,
    .stDownloadButton > button * {
        color: #ffffff !important;
    }

    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px dashed rgba(255, 255, 255, 0.20);
        border-radius: 18px;
        padding: 8px;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.025);
        border-radius: 14px;
    }

    .stAlert {
        background: rgba(11, 15, 25, 0.75);
        border-radius: 15px;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding: 1.5rem 1rem 2rem 1rem;
        }
        .glass-card {
            padding: 18px;
            border-radius: 20px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-title">✨ Cinematic Video Audio Replacer</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-subtitle">'
    "Replace your video's original audio with a new soundtrack — fast, clean and cinematic."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🎬 Choose Your Media</div>', unsafe_allow_html=True)

video_col, audio_col = st.columns(2, gap="large")

with video_col:
    st.markdown("### 🎥 Video")
    video_file = st.file_uploader(
        "Upload video",
        type=["mp4", "mov", "mkv", "avi"],
        key="video_uploader",
    )
    if video_file is not None:
        st.success(f"Video loaded: {video_file.name}")
        try:
            st.video(video_file)
        except Exception:
            st.warning("Video preview is not available for this format.")

with audio_col:
    st.markdown("### 🎵 Audio")
    audio_file = st.file_uploader(
        "Upload audio",
        type=["mp3", "wav", "m4a", "aac"],
        key="audio_uploader",
    )
    if audio_file is not None:
        st.success(f"Audio loaded: {audio_file.name}")
        try:
            st.audio(audio_file)
        except Exception:
            st.warning("Audio preview is not available for this format.")

st.markdown("</div>", unsafe_allow_html=True)


def replace_audio(video_uploaded_file, audio_uploaded_file):
    ffmpeg_executable = imageio_ffmpeg.get_ffmpeg_exe()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        video_extension = Path(video_uploaded_file.name).suffix.lower() or ".mp4"
        audio_extension = Path(audio_uploaded_file.name).suffix.lower() or ".mp3"

        input_video = temp_path / f"input_video{video_extension}"
        input_audio = temp_path / f"input_audio{audio_extension}"
        output_video = temp_path / "cinematic_audio_replaced.mp4"

        input_video.write_bytes(video_uploaded_file.getbuffer())
        input_audio.write_bytes(audio_uploaded_file.getbuffer())

        command = [
            ffmpeg_executable,
            "-y",
            "-i", str(input_video),
            "-i", str(input_audio),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-movflags", "+faststart",
            str(output_video),
        ]

        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if process.returncode != 0:
            raise RuntimeError(
                "FFmpeg could not process the video.\n\n"
                + process.stderr[-4000:]
            )

        if not output_video.exists():
            raise RuntimeError("FFmpeg finished but no output video was created.")

        return output_video.read_bytes()


st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown(
    '<div class="section-title">🚀 Generate Your Cinematic Video</div>',
    unsafe_allow_html=True,
)

if video_file is None or audio_file is None:
    st.info("Upload both a video and an audio file to continue.")

process_clicked = st.button(
    "✨ Process & Generate Video Now",
    disabled=(video_file is None or audio_file is None),
    use_container_width=True,
)
st.markdown("</div>", unsafe_allow_html=True)


if process_clicked:
    with st.spinner("🎬 Processing your cinematic video..."):
        try:
            final_video = replace_audio(video_file, audio_file)
            st.session_state["final_video"] = final_video
            st.success("🎉 Your new cinematic video has been generated successfully!")
        except Exception as error:
            st.error("❌ Processing failed.")
            st.code(str(error))


if "final_video" in st.session_state:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">🎞️ Final Cinematic Video</div>',
        unsafe_allow_html=True,
    )

    final_video_data = st.session_state["final_video"]
    st.video(final_video_data)

    st.download_button(
        label="⬇️ Download Cinematic Video",
        data=final_video_data,
        file_name="cinematic_audio_replaced.mp4",
        mime="video/mp4",
        use_container_width=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align:center;color:rgba(255,255,255,0.55);
                font-size:0.85rem;margin-top:30px;">
        ✨ Cinematic Video Audio Replacer<br>
        Powered by Python • Streamlit • FFmpeg
    </div>
    """,
    unsafe_allow_html=True,
)
