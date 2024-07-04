from celery import shared_task
from pydub import AudioSegment
from pydub.silence import split_on_silence
import io
from django.core.files import File


@shared_task
def summarize_call_session(call_session_id):
    from .models import CallSession
    call_session = CallSession.objects.get(pk=call_session_id)
    conversation = call_session.conversation.all().order_by('save_time')

    def _generate_summary(audio):
        combined_file = io.BytesIO()
        audio.export(combined_file, format='wav')
        combined_file.seek(0)
        call_session.audio = File(combined_file)
        call_session.audio.name = 'audio.wav'
        call_session.save()
        combined_file.close()  # Closing the BytesIO object as it's no longer needed.

    audio = AudioSegment.empty()
    for conv in conversation:
        print(conv.audio)
        audio_snippet = AudioSegment.from_file(conv.audio.open(mode='rb'))
        audio_chunks = split_on_silence(
            audio_snippet,
            min_silence_len=2000,
            silence_thresh=-45,
            keep_silence=500,
        )
        audio_processed = sum(audio_chunks)
        audio += audio_processed

    if audio:
        _generate_summary(audio)


