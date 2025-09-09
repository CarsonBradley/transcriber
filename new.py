from deepgram import DeepgramClient
from deepgram import PrerecordedOptions

key = '850e2b55f87cf82ae7d59111752e7adaf09c5e4e'

class Transcriber:
    def __init__(self, key: str, lang: str, model: str):
        self.key = key
        self.lang = lang
        self.model = model
        self.deepgram = DeepgramClient(self.key)

    def format_time(self):
        """
        Format the given time in seconds into HH:MM:SS.
        Rounds to the nearest whole second.
        """
        rounded_seconds = int(round(self.seconds))
        hrs = rounded_seconds // 3600
        mins = (rounded_seconds % 3600) // 60
        secs = rounded_seconds % 60
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"

    def transcribe_url(self, url):
        """
        Transcription function that sends request to Deepgram 
        for the JSON formatted transcription of the audio file
        """
        if 'https:' not in url:
            source = open(url, "rb")
        else:
            source = {"url": url}

        try:
            deepgram = DeepgramClient(self.key)
            options = PrerecordedOptions(
                model = self.model,
                smart_format = True,
                language= self.lang,
                diarize=True
            )

            response = deepgram.listen.prerecorded.v("1").transcribe_url(source, options, timeout=300)

            # Convert response to JSON
            response = response.to_dict()

        except Exception as e:
            print(f"Exception: {e}")
        return response

    def format_transcript(self, response):
        """
        Format the response from Deepgram into legible
        text with the standard transcript format
        """

        response = self.transcribe_url()

        try:
            # Get the transcript paragraphs
            paragraphs = response['results']['channels'][0]['alternatives'][0]['paragraphs']['paragraphs']

            full_text = []
            for paragraph in paragraphs:
                # Get start and end times
                start_time = paragraph['sentences'][0]['start']
                end_time = paragraph['sentences'][-1]['end']

                # Check if speaker information exists
                speaker = None
                if 'speaker' in paragraph:
                    speaker = f"Speaker {paragraph['speaker']}"
                else:
                    speaker = "Speaker Unknown"

                # Concatenate sentences to form the paragraph text
                paragraph_text = " ".join([s['text'] for s in paragraph['sentences']]).strip()

                # Format the times
                formatted_start = format_time(self.start_time)
                formatted_end = format_time(end_time)

                # Create formatted paragraph string
                formatted_paragraph = f"[{formatted_start} - {formatted_end}] {speaker}: {paragraph_text}"
                full_text.append(formatted_paragraph)

            # Join all paragraphs with newlines and return
            return "\n".join(full_text)

        except KeyError as e:
            print(f"KeyError: {e} not found in the JSON data")
            return None



