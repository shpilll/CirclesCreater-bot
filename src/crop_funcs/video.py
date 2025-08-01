import subprocess

from moviepy.video.io.VideoFileClip import VideoFileClip

def crop_video(input_path, output_path):
    try:

        video = VideoFileClip(input_path)
        if video.rotation in (90, 270):  # Если видео портретное
            video = video.resized(video.size[::-1])  # Меняем ширину и высоту местами
            video.rotation = 0  # Сбрасываем метаданные

        width, height = video.size
        min_dimension = min(width, height)

        x1 = (width - min_dimension) // 2
        y1 = (height - min_dimension) // 2
        x2 = x1 + min_dimension
        y2 = y1 + min_dimension

        cropped_video = video.cropped(x1=x1, y1=y1, x2=x2, y2=y2)
        video_2 = cropped_video.resized(new_size=(600,600))

        video_2.write_videofile(output_path, codec="libx264", audio_codec="aac")

        video.close()
        cropped_video.close()
        video_2.close()

    except Exception as e:
        print(f"Error cropping video: {e}")

