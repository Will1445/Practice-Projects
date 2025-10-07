import random
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

WORDS_PER_MINUTE = 160

def estimate_tts_duration(text, wpm=WORDS_PER_MINUTE):
    word_count = len(text.split())
    minutes = word_count / wpm
    return minutes * 60  # seconds

def select_random_video_segment(video_path, duration_needed):
    video = VideoFileClip(video_path)
    max_start = video.duration - duration_needed
    if max_start <= 0:
        return video.subclip(0, video.duration)
    
    start_time = random.uniform(0, max_start)
    end_time = start_time + duration_needed
    return video.subclip(start_time, end_time)

def create_tiktok_video(video_path, audio_path, story_text, output_path="final_video.mp4"):
    # Estimate duration
    estimated_duration = estimate_tts_duration(story_text)

    # Select segment from video
    video_segment = select_random_video_segment(video_path, estimated_duration)

    # Load actual TTS audio
    audio = AudioFileClip(audio_path)

    # Adjust video to exact audio length (tiny trimming or looping)
    if video_segment.duration > audio.duration:
        video_segment = video_segment.subclip(0, audio.duration)
    elif video_segment.duration < audio.duration:
        from moviepy.video.fx.loop import loop
        video_segment = loop(video_segment, duration=audio.duration)

    video_segment = video_segment.set_audio(audio)

    # Add basic subtitle
    subtitle = TextClip(
        story_text,
        fontsize=40,
        color='white',
        size=(video_segment.w * 0.9, None),
        method='caption',
        align='center',
        font='Arial-Bold'
    ).set_position(('center', 'bottom')).set_duration(audio.duration)

    # Combine video + subtitle
    final = CompositeVideoClip([video_segment, subtitle])

    final.write_videofile(output_path, fps=30)
    print(f"✅ Exported to {output_path}")

create_tiktok_video(
    video_path="parkour.mp4",
    audio_path="output_us_casual_k.mp3",
    story_text="This is a Reddit story about someone who..."
)
