import os
import numpy as np

from openai import OpenAI

os.environ.get("OPENAI_API_KEY", "NOKEY")

# OpenAI API
client = OpenAI()


def cosine_similarity(x, y):
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))
