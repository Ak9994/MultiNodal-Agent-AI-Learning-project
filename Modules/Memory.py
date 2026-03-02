from dataclasses import dataclass, field
from typing import List
import time
#Memory variables
@dataclass
class MemoryVar():
    text: str
    tags: List[str]
    #Memory Score
    score: float
    #Memory Timestamp
    timestamp: float = field(default_factory=lambda: time.time())

#Compare scores 
def cosine_overlap(txt1:str,txt2:str):
    words1 = set(txt1.lower().split())
    words2 = set(txt2.lower().spilt())
    comp_score = len(words1 & words2)/max(1,len(words1 | words2))
    return comp_score

#Memory 
class Memory():
    def __init__(self):
        #list of memory variables 
        self.items: list[MemoryVar] = []

    #Add to memory
    def write(self,text,tags,score):
        self.items.append(MemoryVar(text=text,tags=tags or [],score=score))

    #Read from memory
    def retrieve(self,query,k=5):
        now = time.time()
        scored_items = []
        for item in self.items:
            #Decay over time , for now 30s 
            recent_score = 1.0/(1.0 + (now - item.timestamp)/30)
            relevance_score_score = cosine_overlap(query,item.text)
            score= item.score
            final_score = recent_score + relevance_score_score + score
            scored_items.append((final_score,item))
        #Get top results
        sorted_items = sorted(scored_items,key=lambda x:x[0],reverse=True)
        top_k = sorted_items[:k]
        result = [pair[1] for pair in top_k]
        return result