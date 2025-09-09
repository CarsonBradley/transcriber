from deepgram import DeepgramClient
from deepgram import PrerecordedOptions

key = '850e2b55f87cf82ae7d59111752e7adaf09c5e4e'


def format_time(seconds):
            """
            Format the given time in seconds into HH:MM:SS.
            Rounds to the nearest whole second.
            """
            rounded_seconds = int(round(seconds))
            hrs = rounded_seconds // 3600
            mins = (rounded_seconds % 3600) // 60
            secs = rounded_seconds % 60
            return f"{hrs:02d}:{mins:02d}:{secs:02d}"


class DeepgramTranscriber:
    def __init__(self, key: str):
        self.client = DeepgramClient(key)

    def transcribe_url(self, url: str, lang: str, model: str):
        """
        Transcription function that sends request to Deepgram 
        for the JSON formatted transcription of the audio file
        """
        if 'https:' not in url:
            source = open(url, "rb")
        else:
            source = {"url": url}

        try:
            options = PrerecordedOptions(
                model = model,
                smart_format = True,
                language= lang,
                diarize=True
            )

            response = self.client.listen.prerecorded.v("1").transcribe_url(source, options, timeout=300)

            # Convert response to JSON
            response = response.to_dict()

        except Exception as e:
            print(f"Exception: {e}")
        return response

    def format_transcript(self, response: dict):
        """
        Format the response from Deepgram into legible
        text with the standard transcript format
        """
        if not response:
            return "Transcription failed or no response provided."

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
                formatted_start = format_time(start_time)
                formatted_end = format_time(end_time)

                # Create formatted paragraph string
                formatted_paragraph = f"[{formatted_start} - {formatted_end}] {speaker}: {paragraph_text}"
                full_text.append(formatted_paragraph)

            # Join all paragraphs with newlines and return
            return "\n".join(full_text)

        except KeyError as e:
            print(f"KeyError: {e} not found in the JSON data")
            return None


# How to use the new, improved class:
if __name__ == "__main__":
    API_KEY = '850e2b55f87cf82ae7d59111752e7adaf09c5e4e'
    URL = "https://storage.googleapis.com/radiotransdata/audio-files/redfm_TESTER_06_28_24_08_28_00%20(1)%20(1).wav"

    # 1. Create the reusable transcriber tool
    transcriber = DeepgramTranscriber(API_KEY)

    # 2. Use the tool to run a specific job
    raw_response = transcriber.transcribe_url(URL, lang="multi", model="nova-3")

    # 3. Pass the result of that job to the formatter
    if raw_response:
        formatted_transcript = transcriber.format_transcript(raw_response)
        print(formatted_transcript)
    else:
        print("Transcription failed.")

