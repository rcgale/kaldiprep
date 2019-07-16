import collections
import os
import wave
from typing import List

import itertools
from sortedcontainers import SortedDict
from sortedcontainers import SortedSet


Utterance = collections.namedtuple(
    "Utterance", [
        "utterance_id",
        "speaker_id",
        "transcript",
        "filename"
    ]
)


Segment = collections.namedtuple(
    "Segment", [
        "segment_id",
        "utterance_id",
        "speaker_id",
        "transcript",
        "filename",
        "start_time",
        "end_time",
    ]
)


def write_data_set(utterances: List[Utterance], path: str, *_, wav_format="{}", encoding=None):
    if not os.path.exists(path):
        os.makedirs(path)


    transcripts, utterance_to_speaker, speaker_to_utterance, utterance_to_wav, segments = \
        _process_utterances(utterances)

    text = _text_lines(transcripts)
    _write_file("text", text, path, encoding=encoding)

    wav_scp = _wav_scp_lines(utterance_to_wav, wav_format=wav_format)
    _write_file("wav.scp", wav_scp, path, encoding=encoding)

    utt2spk = _utt2spk_lines(speaker_to_utterance, utterance_to_speaker)
    _write_file("utt2spk", utt2spk, path, encoding=encoding)

    spk2utt = _spk2utt_lines(speaker_to_utterance)
    _write_file("spk2utt", spk2utt, path, encoding=encoding)

    if len(segments):
        segments_lines = _segments_lines(segments)
        _write_file("segments", segments_lines, path, encoding=encoding)


def _write_file(filename, lines, path, encoding):
    with open(os.path.join(path, filename), "w", encoding=encoding) as file:
        for line in lines:
            print(line, file=file)


def _text_lines(transcripts):
    for utterance_id, transcript in transcripts.items():
        yield "{utterance_id} {transcript}".format(
            utterance_id=utterance_id,
            transcript=transcript
        )


def _wav_scp_lines(utterance_to_wav, wav_format):
    for utterance_id, wav_path in utterance_to_wav.items():
        yield "{utterance_id} {wav}".format(
            utterance_id=utterance_id,
            wav=wav_format.format(wav_path)
        )


def _segments_lines(segments: List[Segment]):
    for segment in segments:
        yield "{segment_id} {utterance_id} {start_time} {end_time}".format(
            segment_id=segment.segment_id,
            utterance_id=segment.utterance_id,
            start_time=segment.start_time,
            end_time=segment.end_time,
        )


def _utt2spk_lines(speaker_to_utterance, utterance_to_speaker):
    for speaker_id in speaker_to_utterance:
        for utterance_id in speaker_to_utterance[speaker_id]:
            yield "{utterance_id} {speaker_id}".format(
                utterance_id=utterance_id,
                speaker_id=utterance_to_speaker[utterance_id]
            )


def _spk2utt_lines(speaker_to_utterance):
    for speaker_id in speaker_to_utterance:
        utterances = " ".join(speaker_to_utterance[speaker_id])
        yield "{speaker_id} {utterance_id}".format(
            speaker_id=speaker_id,
            utterance_id=utterances
        )


def _process_utterances(utterances):
    transcripts = SortedDict()
    utterance_to_speaker = SortedDict()
    speaker_to_utterance = SortedDict()
    utterance_to_wav = SortedDict()
    segments = SortedSet()
    has_no_segments = SortedSet()

    sorted_utterances = sorted(utterances, key=lambda u: u.speaker_id)
    grouped_by_speaker = itertools.groupby(sorted_utterances, lambda u: u.speaker_id)

    for speaker_id, speaker_utterances in grouped_by_speaker:

        sorted_speaker_utterances = SortedSet()

        for utterance in speaker_utterances:
            if hasattr(utterance, "segment_id"):
                segment_id = utterance.segment_id
                segments.add(utterance)
            else:
                segment_id = utterance.utterance_id
                has_no_segments.add(utterance)
            sorted_speaker_utterances.add(segment_id)
            transcripts[segment_id] = utterance.transcript
            utterance_to_speaker[segment_id] = speaker_id
            utterance_to_wav[utterance.utterance_id] = utterance.filename

        if len(sorted_speaker_utterances) > 0:
            speaker_to_utterance[speaker_id] = sorted_speaker_utterances

    if len(segments) and len(has_no_segments):
        generated_segments = [_get_segment_from_utterance(utterance) for utterance in has_no_segments]
        segments.update(generated_segments)

    return transcripts, utterance_to_speaker, speaker_to_utterance, utterance_to_wav, segments


def _get_segment_from_utterance(utterance: Utterance):
    if hasattr(utterance, "segment_id"):
        return utterance

    with wave.open(utterance.filename, 'r') as w:
        length_seconds = round(1.0 * w.getnframes() / w.getframerate(), 1)
        return Segment(
            segment_id=utterance.utterance_id,
            utterance_id=utterance.utterance_id,
            speaker_id=utterance.speaker_id,
            transcript=utterance.transcript,
            filename=utterance.filename,
            start_time=0.0,
            end_time=length_seconds
        )
