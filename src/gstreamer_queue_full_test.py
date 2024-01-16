"""
This script demonstrates how to exit a GStreamer pipeline when a queue becomes full.

Key Features:
- Initialization of the GStreamer framework.
- Starting the pipeline to play the video stream.
- Waiting for an error or end-of-stream (EOS) message to terminate the pipeline.
- Releasing resources by setting the pipeline's state to NULL.

Note: This script is an example and may need modifications to work in different environments or for specific use cases.
"""

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

# Initialize GStreamer
Gst.init(None)

def overrun_callback(queue):
    print("Queue overrun, stopping pipeline")
    # must signal to the bus, other approaches like 
    # pipeline.set_state(Gst.State.NULL) will not work
    bus.post(Gst.Message.new_eos(pipeline))
    return False

# Create the elements
pipeline = Gst.Pipeline.new("test-pipeline")
source = Gst.ElementFactory.make("videotestsrc", "source")
queue = Gst.ElementFactory.make("queue", "queue")
sink = Gst.ElementFactory.make("autovideosink", "sink")

if not pipeline or not source or not queue or not sink:
    print("Not all elements could be created.")
    exit(-1)

# Set properties
queue.set_property("leaky", 2)  # 2 corresponds to leaky=upstream
queue.set_property("max-size-time", 1)  # 1 nano-second; will become full I hope

# Add elements to the pipeline
pipeline.add(source)
pipeline.add(queue)
pipeline.add(sink)

# Link the elements together
source.link(queue)
queue.link(sink)

# Connect the overrun callback
queue.connect("overrun", overrun_callback)

# Start playing
pipeline.set_state(Gst.State.PLAYING)

# Wait until error or EOS
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

# Free resources
pipeline.set_state(Gst.State.NULL)
