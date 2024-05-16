import numpy as np
import cv2
from imutils import contours
from PIL import Image, ImageEnhance
import fitz
import io
import matplotlib.pyplot as plt


def convertPdftoImage(filename, image_path):
    '''
    This function inputs a PDF file, converts it to an image, and then returns the filepath
    '''
   
    # file path you want to extract images from
    file = filename

    # open the file
    pdf_document = fitz.open(file)

    # Get the page
    page = pdf_document.load_page(0)
    
    # Convert the page to an image
    pix = page.get_pixmap()
    
    # Save the image
    pix.save(image_path % 0)
        # Close the PDF
    pdf_document.close()
    return "page_0.png"



# convertPdftoImage("NumbersTemp1.pdf","page_%d.png" )
# Load image, grayscale, Gaussian blur, Canny edge detection
def OutlineTable(filename):
    '''
    This function attempts to outline the table with a rectangle and preprocess the image before cropping
    '''
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    darkened_image = np.clip(gray* 0.8, 0, 255).astype(np.uint8)  # Multiply by 0.7 to darken
    thresh = cv2.threshold(darkened_image,127,255,cv2.THRESH_BINARY)[1]

    # Sharpening the image
    kernel = np.ones((3, 3), np.uint8)
    sharpened_image = cv2.dilate(thresh,kernel)
    thresh = sharpened_image
    binary = cv2.bitwise_not(thresh)

    contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) ==2 else contours[1]
    colour = (255,0,0)
    thickness = 2
    # i = 0
    # arrX1 = np.zeros(shape=len(contours),dtype=int)
    # arrX2 = np.zeros(shape=len(contours),dtype=int)
    # arrY1 = np.zeros(shape=len(contours),dtype=int)
    # arrY2 = np.zeros(shape=len(contours),dtype=int)
    # thresh2 = cv2.threshold(gray,210,255,cv2.THRESH_BINARY)[1]
    # for i in thresh2:
    #      print(i)
    # cv2.imwrite("thresh.png", thresh2)
    # imgThresh = cv2.imread("thresh.png")
    for cnts in contours:
        x1,y1,w,h = cv2.boundingRect(cnts)
        x1 = x1 - 10
        y1 = y1 - 10
        x2 = x1 + w + 20
        y2 = y1 + h + 20
        if w>10 and w>10 and h>25:
            # arrX1[i] = x1
            # arrX2[i] = x2
            # arrY1[i] = y1
            # arrY2[i] = y2
            cv2.rectangle(gray, (x1, y1), (x2, y2), colour, thickness) # draw rectangle
            # i+=1

    # sorted_X1 = arrX1.sort()
    # sorted_X2 = arrX2.sort()
    # sorted_Y1 = arrY1.sort()
    # sorted_Y2 = arrY2.sort()

    # for i in range(len(arrX1)):
    #     if arrX1[i]!=0 and arrX2[i]!=0 and arrY1[i]!=0 and arrY2[i]!=0:
    #         cropped = image[arrY1[i]:arrY2[i],arrX1[i]:arrX2[i]]
    #         cv2.imwrite(f"Cropped {i+1}.png", cropped)

    cv2.imwrite("Input_table.png", gray) #save image
    cv2.imshow("Input_table", gray)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
