"""Call from CLI"""

# Start word count service
from simplewc.servicer import serve_insecure

serve_insecure('[::]:50001')
