from typing import List, Dict
from dataclasses import dataclass
#Example usage 
@dataclass
class room:
    name: str
    desc: str
    exits: Dict[str, str]
    objects: List[str]

class world:
    def __init__(self):
        self.rooms = {
            "Hall":  room("Hall",  "A plain hall. Door to the East is locked.", {"east":"Doorway","south":"Closet"}, []),
            "Closet":room("Closet","A dusty closet. Something glints here.", {"north":"Hall"}, ["key"]),
            "Doorway":room("Doorway","A heavy door bars the way East.", {"west":"Hall","east":"Outside"}, []),
            "Outside":room("Outside","Freedom!", {}, [])
        }
        #Initial Agent State
        self.locked = True
        self.agent_room = "Hall"
        self.inventory = []

    #Describe the Current room and possible interactions
    def agent_interaction(self)->str:
        rooms = self.rooms[self.agent_room]
        desc = f"You are in the {rooms.name},{rooms.desc},Exits: {list(rooms.exits.keys())}"
        if rooms.objects:
            desc += f"You see {' '.join(rooms.objects)} here."
        if self.locked and self.agent_room == "Doorway":
            desc += "The door is locked"
        return desc.strip()
    
    #Room Selection and movement
    def agent_action(self,direction):
        room_exit = self.rooms[self.agent_room]
        if direction in room_exit.exits:
            dest = room_exit[direction]
            if dest == "Doorway" and self.locked:
                return "Door is locked"
            self.agent_room = dest
            return f"You move {direction} to the {dest}"
        return " You can't go that way"
    
    #Object Pickup
    def agent_pickup(self,obj):
        room_object = self.rooms[self.agent_room]
        if obj in room_object.objects:
            room_object.objects.remove(obj)
            self.inventory.append(obj)
            return f"You picked up the {obj}"
        return f"There is no {obj} here"
    
    #use object
    def agent_use(self,obj,target):
        if obj not in self.inventory:
            return f"You don't have {obj}"
        if obj == "key" and target == "door" and self.agent_room == "Doorway":
            self.locked = False
            return "You unlocked the door"
        return f"You can't use {obj} on {target}"
    
    
    






