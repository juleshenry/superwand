import subprocess as s
[s.run("python3 ~/superwand/superwand.py gloria.png "+o,shell=True) for o in 'Spring,Summer,Winter,Fall,Safari,Urban,Neon,Tropical,Arctic,Paixão'.split(',')]
