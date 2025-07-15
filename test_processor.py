# test_processor.py
from app import processor

test_file = r"D:\Data\Docs PKJHA 29-12-24\B. TECH\Udemy\Python Programming\Generative AI\Project\Project Media Processing Automation Tool\Videos\apna_mart_ad_2.mp4"  # or .wav, .mp3, etc.
processor.run(test_file)
print(processor.results[-1])  # Print the last result
