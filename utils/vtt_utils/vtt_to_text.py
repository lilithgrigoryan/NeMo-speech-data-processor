import sys

import pysrt

print(sys.argv)
vtt_filepath = sys.argv[1]

subs = pysrt.open(vtt_filepath)
captions = [sub.text for sub in subs]
text = " ".join(captions)

print(text)
