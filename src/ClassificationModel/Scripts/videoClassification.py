from ipywidgets import Video
from transformers import XCLIPProcessor, XCLIPModel
import torch

from src.ClassificationModel.Scripts.labels import video_Labels

model_name = "microsoft/xclip-base-patch32"
processor = XCLIPProcessor.from_pretrained(model_name)
model = XCLIPModel.from_pretrained(model_name)
from decord import VideoReader, cpu
import numpy as np


def sample_frame_indices(clip_len, frame_sample_rate, seg_len):
    """
    Sample frame indices for a video clip within a given segment.

    Parameters:
    - clip_len (int): Length of the video clip in frames.
    - frame_sample_rate (int): Rate at which frames are sampled.
    - seg_len (int): Length of the video segment.

    Returns:
    - indices (numpy.ndarray): Array of sampled frame indices.
    """
    # Calculate the converted length based on the frame sample rate
    converted_len = int(clip_len * frame_sample_rate)

    # Generate a random end index within the given segment length
    end_idx = np.random.randint(converted_len, seg_len)

    # Calculate the start index based on the end index and converted length
    start_idx = end_idx - converted_len

    # Generate evenly spaced indices within the calculated range
    indices = np.linspace(start_idx, end_idx, num=clip_len)

    # Clip the indices to ensure they are within the valid range and convert to int64
    indices = np.clip(indices, start_idx, end_idx - 1).astype(np.int64)

    # Return the sampled indices
    return indices


def get_video_classification(file_path):
    """
    Perform video classification using a pre-trained model.

    Parameters:
    - file_path (str): The path to the video file.

    Returns:
    - probs (torch.Tensor): A tensor of probabilities for different classes.
    """

    file_path = file_path
    # Create a Video object from the downloaded file with a width of 500 pixels
    Video.from_file(file_path)
    # Set a fixed seed for NumPy's random number generator to ensure reproducibility
    np.random.seed(0)

    # Define a function to sample frame indices from a video clip

    # Create a VideoReader object for the specified file path with a single CPU thread
    vr = VideoReader(file_path, num_threads=1, ctx=cpu(0))

    # Set the video reader to the beginning of the video
    vr.seek(0)

    # Sample frame indices for a video clip with a length of 8 frames, frame sample rate of 1, and the length of the video
    indices = sample_frame_indices(clip_len=8, frame_sample_rate=1, seg_len=len(vr))

    results = {}

    for key, value in video_Labels.items():
        # Retrieve the batch of frames corresponding to the sampled indices and convert to NumPy array
        video = vr.get_batch(indices).asnumpy()
        inputs = processor(
            text=value,
            videos=list(video),
            return_tensors="pt",
            padding=True,
        )

        # forward pass
        with torch.no_grad():
            outputs = model(**inputs)
        probs = outputs.logits_per_video.softmax(dim=1)
        classes = value
        classified_results = {
            cls: prob.item() for cls, prob in zip(classes, probs[0].detach().numpy())
        }
        results[key] = classified_results

    return results
