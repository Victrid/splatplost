#!/bin/python

import sys
import os
from PIL import Image
import numpy as np

def diff(a,b):
    return (a!=b).sum()

def safe_val(x,y):
    return x >= 0 and x < 120 and y >= 0 and y < 320

def find_neighbours(x,y,orig,visited,mindist):
    neib = []
    if safe_val(x+1,y) and (x+1,y) not in visited and dis(orig, (x+1,y) )<mindist:
        neib.append((x+1,y))
    if safe_val(x,y-1) and (x,y-1) not in visited and dis(orig, (x,y-1) )<mindist:
        neib.append((x,y-1))
    if safe_val(x-1,y) and (x-1,y) not in visited and dis(orig, (x-1,y) )<mindist:
        neib.append((x-1,y))
    if safe_val(x,y+1) and (x,y+1) not in visited and dis(orig, (x,y+1) )<mindist:
        neib.append((x,y+1))
    return neib

def dis(a,b):
    return abs(a[0]-b[0])+abs(a[1]-b[1])

def find_nearest(x,y,orig,curr):
    queue = [(x,y)]
    visited = [(x,y)]
    dist = 500
    queue+=find_neighbours(x,y,(x,y),visited,dist)
    visited+=find_neighbours(x,y,(x,y),visited,dist)
    candidate = []
    while len(queue) > 0:
        p = queue[0]
        queue.pop(0)
        if orig[p[0]][p[1]] == curr[p[0]][p[1]]:
            queue+=find_neighbours(p[0],p[1],(x,y),visited,dist)
            visited+=find_neighbours(p[0],p[1],(x,y),visited,dist)
        else:
            candidate.append(p)
            if dist > dis(p,(x,y)):
                dist = dis(p,(x,y))
    dist = 500
    final = (-1,-1)
    for t in candidate:
        if dis(t,(x,y)) < dist:
            final = t
    return final

def genq(graph):
   rq = np.zeros_like(graph)
   rq.fill(1)
   rq = rq.astype(int)
   seq = []
   curr = (0,0)
   while diff(rq,graph) != 0:
       tp = find_nearest(curr[0],curr[1],graph,rq)
       if tp[0]==-1:
           im = Image.fromarray(rq*255).convert("RGB")
           im.save("./md.jpeg")
           raise Exception()
       seq.append(tp)
       curr = tp
       rq[tp[0]][tp[1]] = graph[tp[0]][tp[1]]
   return seq

def march(a,b):
    output_q = []
    ver = b[0]-a[0]
    hor = b[1]-a[1]
    if ver > 0:
        output_q += ["down"]*ver
    else:
        output_q += ["up"]*(-ver)
    if hor > 0:
        output_q += ["right"]*hor
    else:
        output_q += ["left"]*(-hor)
    return output_q

def stamp(seq):
    num = 0
    init = (0,0)
    for item in seq:
        q = march(init,item)
        for word in q:
            print(word)
            num+=1
        print("a")
        num+=1
        init = item
    return num

def main(argv):
  im = Image.open(argv[0])
  if not (im.size[0] == 320 and im.size[1] == 120):
      print("ERROR: Image must be 320px by 120px!")
      sys.exit()
  im = im.convert("1")   
  im_px = im.load()
  image = np.array(im.getdata()).reshape(120,320)/255
  image = image.astype(int)
  orig = image.sum()+320*120-1
  idem = stamp(genq(image))
  sys.stderr.write(f"{orig},{idem}")

if __name__ == "__main__":
    main(sys.argv[1:])
