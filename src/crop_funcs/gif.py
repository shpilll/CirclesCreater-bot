from moviepy.video.io.VideoFileClip import VideoFileClip


def crop_and_resize_gif(input_path, output_path):
    video = VideoFileClip(input_path)

    width, height = video.size
    min_dimension = min(width, height)

    x1 = (width - min_dimension) // 2
    y1 = (height - min_dimension) // 2
    x2 = x1 + min_dimension
    y2 = y1 + min_dimension

    cropped_video = video.cropped(x1=x1, y1=y1, x2=x2, y2=y2)

    resized_video = cropped_video.resized((600, 600))

    resized_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video.fps)

    video.close()
    cropped_video.close()
    resized_video.close()