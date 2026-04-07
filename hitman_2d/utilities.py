import os
from typing import Iterable, Any

import pygame


def load_assets(path: str) -> dict:
    """Recusively load all images in the provided directory to
    pygame Surfaces and store them in a dictionnary.

    Args:
        path (str): Path of the directory to scan

    Returns:
        dict: Dictionnary containing all the pygame image surface and arranged like
        in the directory
    """
    assets: dict[str, pygame.Surface | dict] = {}
    for ressource_name in os.listdir(path):
        ressource_path: str = os.path.join(path, ressource_name)
        if os.path.isdir(ressource_path):
            assets[ressource_name] = load_assets(ressource_path)
        elif any(ressource_name.endswith(ext) for ext in (".jpeg", ".jpg", "png")):
            assets[ressource_name.split(".")[0]] = pygame.image.load(ressource_path).convert_alpha()
        
    return assets

def find_all_element_from_type(obj: dict, element_type: list[type]) -> dict:
    stack: list[tuple[str, dict]] = [("", obj)]
    result: dict = {}
    
    while stack:
        path, element = stack.pop(0)
        
        for k, v in element.items():
            if isinstance(v, tuple(element_type)):
                result[os.path.join(path, k)] = v
            if isinstance(v, dict):
                stack.append((os.path.join(path, k), v))
                
    return result


def find_all_paths(
    links: dict[int, tuple[int]], 
    start: int, 
    end: int
    
) -> list[list[int]]:
    """
    Return a list of all valid path from start to end
    in the graph links.
    """
    stack: list[list[int]] = [[start]]
    
    pool_of_results: list[list[int]] = []    
    
    while stack:
        
        current_path = stack.pop(0)
        neighbors = links[current_path[-1]]
        
        for neighbor in neighbors:
            
            temp_path = current_path[:]
            
            if neighbor in temp_path: # Avoid returning in visited room and check the other neighbor
                continue
            
            temp_path = temp_path + [neighbor] # Add neighbors to the temporary path
            
            if neighbor == end: # Valid path found, add to the pool of result
                pool_of_results.append(temp_path[:])
            else: # Add the temporary path to future investigation
                stack.append(temp_path[:]) 
    
    return sorted(pool_of_results, key=len)


def get_from_dict(obj: dict, path: list[str], default_value=None) -> None:
    current_obj = obj
    
    for p in path:
        try:
            current_obj = current_obj[p]
        except KeyError:
            return default_value
        
    return current_obj


def set_to_dict(obj: dict, path: list[str], value: Any) -> None:
    current_obj = obj
    
    for i, p in enumerate(path):
        
        if p not in current_obj:
            current_obj[p] = {}
        
        if i == len(path) - 1:
            current_obj[p] = value
            return
            
        current_obj = current_obj[p]
            


def generate_unique_id(elements: Iterable[str]) -> str:
    if len(elements) == 0: return "0"
    
    id_list: list[str] = sorted(elements, key=int)

    if int(id_list[0]) != 0: return "0"
    
    for i, id_ in enumerate(id_list):
        if i != int(id_):
            return str(int(id_list[i - 1]) + 1)
        
    return str(len(id_list))
    

if __name__ == "__main__":
    
    
    # obj = {}
    
    # set_to_dict(obj, ["a", "b", "c"], 3)
    
    # print(obj)
    
    # set_to_dict(obj, ["a", "b", "d"], 12)
    
    # set_to_dict(obj, ["h", "b"], 1)
    
    # print(obj)
    
    # import random
    
    # id_list: list[str] = list({str(random.randint(0, 10)) for _ in range(10)})
    
    # print(id_list, generate_unique_id(id_list))
    
    links = {
        1: (2,),
        2: (1, 3),
        3: (2, 4, 8),
        4: (3, 5),
        5: (4, 6, 7),
        6: (5,),
        7: (5, 8),
        8: (3, 7)
    }
    
    all_path = find_all_paths(
        links,
        start=1,
        end=7
    )
    
    print(all_path)