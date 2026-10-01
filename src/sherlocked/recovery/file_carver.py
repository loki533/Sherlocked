from __future__ import annotations
from pathlib import Path
from typing import List, Optional

class FileCarver:
    """Recover file candidates directly from raw image bytes using signatures."""
    SIGNATURES = {"png": b"\x89PNG\r\n\x1a\n", "jpg": b"\xff\xd8\xff", 
                  "gif": (b"GIF87a", b"GIF89a"), "pdf": b"%PDF-", "zip": b"PK\x03\x04"}
    
    DEFAULT_MAX_SIZE = {"png":64*1024*1024,"jpg":64*1024*1024,"gif":64*1024*1024,"pdf":128*1024*1024,"zip":256*1024*1024}

    def __init__(self,image_path,chunk_size=1024*1024): self.image_path=Path(image_path); self.chunk_size=max(4096,int(chunk_size))
    @classmethod
    def _find_signature(cls,buffer):
        matches=[]
        for ext,sigs in cls.SIGNATURES.items():
            if isinstance(sigs,bytes): sigs=(sigs,)
            for sig in sigs:
                start=0
                while True:
                    off=buffer.find(sig,start)
                    if off<0: break
                    matches.append((off,ext)); start=off+1
        return sorted(matches)

    
    def scan(self,start_offset=0,end_offset=None)->List[dict]:
        if not self.image_path.exists(): raise FileNotFoundError(self.image_path)
        size=self.image_path.stat().st_size; start=max(0,int(start_offset)); end=size if end_offset is None else min(int(end_offset),size)
        if start>=end:return []
        max_sig=max(len(s) if isinstance(s,bytes) else max(map(len,s)) for s in self.SIGNATURES.values()); overlap=max_sig-1
        buf=b""; base=start; out=[]; seen=set()
        with self.image_path.open("rb") as f:
            f.seek(start)
            while f.tell()<end:
                chunk=f.read(min(self.chunk_size,end-f.tell()))
                if not chunk: break
                buf+=chunk
                for rel,ext in self._find_signature(buf):
                    absolute=base+rel; key=(absolute,ext) #conversion of buffer relative to absolute byte position
                    if key not in seen: seen.add(key); out.append({"offset":absolute,"extension":ext})
                if len(buf)>overlap: base+=len(buf)-overlap; buf=buf[-overlap:]
        return out
    
    def carve_candidate(self,offset:int,extension:str,output_dir=None,max_size:Optional[int]=None)->Optional[dict]:
        ext=extension.lower().lstrip('.');
        if ext not in self.SIGNATURES: raise ValueError(f"Unsupported carving type: {ext}")
        max_size=max_size or self.DEFAULT_MAX_SIZE[ext]; offset=int(offset)
        if offset<0 or offset>=self.image_path.stat().st_size:return None
        with self.image_path.open('rb') as f: f.seek(offset); data=f.read(max_size)
        end=self._find_end(data,ext)
        if end is None:return None
        carved=data[:end]
        if not self._validate(carved,ext):return None
        result={"offset":offset,"extension":ext,"size":len(carved),"status":"carved_candidate","validation":"passed"}
        if output_dir is not None:
            output=Path(output_dir); output.mkdir(parents=True,exist_ok=True); path=output/f"carved_{offset:012x}.{ext}"; path.write_bytes(carved); result["output_path"]=str(path)
        return result
    
    @staticmethod
    def _find_end(data,ext):
        markers={"jpg":(b"\xff\xd9",2),"png":(b"IEND\xaeB`\x82",8),"gif":(b"\x3b",1),"pdf":(b"%%EOF",5)}
        if ext in markers:
            marker,tail=markers[ext]; pos=data.find(marker, 2 if ext in ('jpg','png') else 5); return pos+tail if pos!=-1 else None
        
            #data.find(marker , start)-> skips first 2 bytes i.e file header 
            #inorder to avoid false positive such that if magic bytes are similar with file header

        if ext=='zip':
            pos=data.find(b"PK\x05\x06",4)
            if pos!=-1:return pos+22
            pos=data.find(b"PK\x06\x06",4); return pos+56 if pos!=-1 else None
        return None
    
    @staticmethod
    def _validate(data,ext):
        if ext=='png':return data.startswith(b"\x89PNG\r\n\x1a\n") and data.endswith(b"IEND\xaeB`\x82")
        if ext=='jpg':return data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9")
        if ext=='gif':return data[:6] in (b"GIF87a",b"GIF89a") and data.endswith(b"\x3b")
        if ext=='pdf':return data.startswith(b"%PDF-") and b"%%EOF" in data[-1024:]
        if ext=='zip':return data.startswith(b"PK\x03\x04") and (b"PK\x05\x06" in data[-65557:] or b"PK\x06\x06" in data[-65577:])
        return False
    
    def carve_all(self,output_dir=None,start_offset=0,end_offset=None,max_candidates=None)->List[dict]:
        results=[]
        for c in self.scan(start_offset,end_offset):
            r=self.carve_candidate(c['offset'],c['extension'],output_dir)
            if r is not None:results.append(r)
            if max_candidates and len(results)>=max_candidates:break
        return results
