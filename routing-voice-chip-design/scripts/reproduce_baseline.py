#!/usr/bin/env python3
import hashlib,json,time
from pathlib import Path
import soundfile as sf
from moonshine_voice.moonshine_api import ModelArch
from moonshine_voice.transcriber import Transcriber
ROOT=Path(__file__).resolve().parents[1]
model=ROOT/'models/artifacts';sample=ROOT/'models/reference.wav'
audio,sr=sf.read(sample,dtype='float32');started=time.perf_counter()
with Transcriber(model,ModelArch.TINY_STREAMING) as t:
    initialized=time.perf_counter();result=t.transcribe_without_streaming(audio.tolist(),sr);finished=time.perf_counter()
report={'scope':'CPU software baseline only; not FPGA/ASIC inference or energy measurement','sample_sha256':hashlib.sha256(sample.read_bytes()).hexdigest(),'sample_rate':sr,'audio_seconds':len(audio)/sr,'initialization_seconds':initialized-started,'transcription_seconds':finished-initialized,'real_time_factor':(finished-initialized)/(len(audio)/sr),'transcript':' '.join(line.text for line in result.lines)}
(ROOT/'reports/software-baseline.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
