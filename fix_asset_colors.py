import os

import cv2

image_path_list: list[str] = []

stack: list[str] = ["Assets"]

while stack:
    path = stack.pop(0)
    if (os.path.isdir(path)):
        stack.extend(os.path.join(path, ressource) for ressource in os.listdir(path))
    else:
        image_path_list.append(path)
        
for image_path in image_path_list:
    img = cv2.imread(image_path)
    
    black_mask = (img == [0, 0, 0]).all(axis=-1)
    white_mask = (img == [255, 255, 255]).all(axis=-1)
    
    img[black_mask] = [1, 1, 1]
    img[white_mask] = [0, 0, 0]
    
    # print(image_path)
    # if image_path == r"Assets\Furnitures\Containers\basket_container.png":
    #     cv2.imshow(image_path, img)
    #     cv2.waitKey(0)
    
    # print(img.shape, black_mask)
    cv2.imwrite(image_path, img)
