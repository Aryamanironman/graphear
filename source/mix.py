import wave, numpy as np

SR=44100; DUR=42.0; N=int(SR*DUR)
def read_wav(p):
    with wave.open(p,'rb') as w:
        ch=w.getnchannels(); sw=w.getsampwidth(); fr=w.getframerate(); nf=w.getnframes()
        raw=w.readframes(nf)
    a=np.frombuffer(raw,dtype=np.int16).astype(np.float32)/32768.0
    if ch==2: a=a.reshape(-1,2)
    else: a=np.stack([a,a],axis=1)
    return a

music=read_wav('out/soundtrack.wav')[:N]
if len(music)<N: music=np.pad(music,((0,N-len(music)),(0,0)))

starts={1:0.80,2:4.95,3:9.95,4:15.95,5:20.25,6:26.15,7:32.15,8:37.45}
vo=np.zeros((N,2),dtype=np.float32)
for i,st in starts.items():
    a=read_wav(f'out/vo/trim{i}.wav')
    s=int(st*SR); e=min(N,s+len(a))
    vo[s:e]+=a[:e-s]
    print(f'line{i}: {st:.2f}s -> {st+len(a)/SR:.2f}s')

# envelope for ducking
mono=np.abs(vo).mean(axis=1)
win=int(0.14*SR)
k=np.ones(win)/win
env=np.convolve(mono,k,mode='same')
env=np.clip(env/0.05,0,1)
duck=1-0.30*env

out=music*0.82*duck[:,None]+vo*0.92

# gentle glue + normalize
out=np.tanh(out*1.15)/1.15
peak=np.max(np.abs(out)); out=out/peak*0.92
out=np.clip(out,-1,1)

pcm=(out*32767).astype(np.int16)
with wave.open('out/mix.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('music/speech balance written, peak',float(peak))
