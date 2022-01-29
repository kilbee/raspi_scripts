import numpy as np
import cv2


def scale_image(img, scale_percent=30):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(img, dim, interpolation = cv2.INTER_AREA)


def contoursConvexHull(contours):   
    pts = []
    for i in range(0, len(contours)):
        for j in range(0, len(contours[i])):
            pts.append(contours[i][j])

    pts = np.array(pts)
    result = cv2.convexHull(pts)
    return result


def image_blur(img, window_name, val = 0):
    if val == 0:
        val = cv2.getTrackbarPos("blur", window_name) # if val not passed - use trackbar value instead
    if val > 1:
        img = cv2.blur(img, (val, val))        
    return img


def image_dilate(img, window_name, val = 0, iterations = 1):
    if val == 0:
        val = cv2.getTrackbarPos("dilate", window_name)  # if val not passed - use trackbar value instead
    iterations = 1
    if val > 1:
        kernel = np.ones((val, val), np.uint8)
        img = cv2.dilate(img, kernel, iterations)
    return img


def image_erode(img, window_name, val = 0, iterations = 1):
    if val == 0:
        val = cv2.getTrackbarPos("erode", window_name)   # if val not passed - use trackbar value instead
    if val > 1:
        kernel = np.ones((val, val), np.uint8)
        img = cv2.erode(img, kernel, iterations)
    return img


def image_threshold(img, window_name, val = 0):
    if val == 0 :
        val = cv2.getTrackbarPos("threshold", window_name)   # if val not passed - use trackbar value instead
    _, thresh = cv2.threshold(img, val, 255, cv2.THRESH_BINARY)    
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def fill_contours(mask, contours):
    len_contour = len(contours)
    contour_list = []
    for i in range(len_contour):
        drawing = np.zeros_like(mask, np.uint8)  # create a black image
        img_contour = cv2.drawContours(drawing, contours, i, (255, 255, 255), -1)
        contour_list.append(img_contour)
    return sum(contour_list)


def process_image_mask_live(img):
    imgray = convert_to_bnw(img)
    imgray = image_erode(imgray, settings_window) # erosion
    imgray = image_dilate(imgray, settings_window) # dilation (fixes erosion)
    imgray = image_blur(imgray, settings_window)  # blurring
    contours = image_threshold(imgray, settings_window)
    mask = np.zeros(img.shape, np.uint8)
    mask = fill_contours(mask, contours)
    return mask, contours


def convert_to_bnw(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def process_image_mask_live_custom(imgray, threshold, erosion, dilation, blur):
    imgray = image_erode(imgray, None, erosion) # erosion
    imgray = image_dilate(imgray, None, dilation) # dilation (fixes erosion)
    imgray = image_blur(imgray, None, blur)  # blurring
    contours = image_threshold(imgray, None, threshold)
    mask = np.zeros(imgray.shape, np.uint8)
    mask = fill_contours(mask, contours)

    #mask = cv2.resize(mask, (img.shape[1], img.shape[0]), interpolation = cv2.INTER_AREA) # scale masks back to image shape
    #cv2.imwrite(out_file_path, mask)
    return mask, contours

def process_image_mask(in_file_path, out_file_path, threshold, erosion, dilation, blur, process_scale):    
    img = cv2.imread(in_file_path)
    img = scale_image(img, process_scale)
    imgray = convert_to_bnw(img)
    imgray = image_erode(imgray, None, erosion) # erosion
    imgray = image_dilate(imgray, None, dilation) # dilation (fixes erosion)
    imgray = image_blur(imgray, None, blur)  # blurring
    contours = image_threshold(imgray, None, threshold)
    mask = np.zeros(img.shape, np.uint8)
    mask = fill_contours(mask, contours)

    mask = cv2.resize(mask, (img.shape[1], img.shape[0]), interpolation = cv2.INTER_AREA) # scale masks back to image shape
    cv2.imwrite(out_file_path, mask)
    return mask, contours


def draw_convex_frame(contours):
    convexhull_points = contoursConvexHull(contours)
    cv2.polylines(mask, [convexhull_points], True, (0,255,0), 2)
    return mask



if __name__ == '__main__':
    img_path = 'E:\\3ds\\but2\\in4\\zapalniczka_IMG_3820.JPG'
    img = cv2.imread(img_path)
    img = scale_image(img, 30) # scale of image will affect masking results!

    image_window = "Mask preview"
    settings_window = "Settings"

    cv2.namedWindow(image_window)
    cv2.namedWindow(settings_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(settings_window, 600, 600)
    cv2.createTrackbar("threshold", settings_window, 12, 255, id)
    cv2.createTrackbar("erode", settings_window, 20, 20, id)
    cv2.createTrackbar("dilate", settings_window, 20, 20, id)
    cv2.createTrackbar("blur", settings_window, 10, 50, id)
    cv2.createTrackbar("balance", settings_window, 50, 100, id)
    cv2.createTrackbar("limits", settings_window, 1, 1, id)

    while True:
        mask, contours = process_image_mask_live(img)
        
        if len(contours) > 0 and cv2.getTrackbarPos("limits", settings_window) > 0:
            draw_convex_frame(contours)

        # show mixed source image and mask overlayed on top, use balance to balance between both
        mask_balance = cv2.getTrackbarPos("balance", settings_window)
        mask_visibility = mask_balance/100
        img_visibility = 1 - mask_visibility
        combined = cv2.addWeighted(img, img_visibility, mask, mask_visibility, 0)
        cv2.imshow(image_window, combined)   # shows mixed source and mask
        #cv2.imshow(window_name, mask)      # shows mask only
        #cv2.imshow(window_name, img)       # show img only


        if cv2.waitKey(1) & 0xFF == ord("q"): # If you press the q key
            break
