import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from PIL import Image
import time
from webdriver_manager.chrome import ChromeDriverManager
import oxen
from oxen.auth import config_auth
from selenium.webdriver.chrome.options import Options
import filecmp
import uuid
config_auth(os.getenv("OXENAI_TOKEN"))

def capture_screenshot(driver, url, output_dir, idx):
    """
    Capture a screenshot of a webpage.

    Args:
        driver (WebDriver): The WebDriver instance.
        url (str): The URL of the webpage.
        output_dir (str): The output directory.
        idx (int): The index of the screenshot.

    Returns:
        str: The path to the screenshot.
    """
    # Navigate to the URL
    driver.get(url)
    
    # Allow the page to load
    time.sleep(2)
    
    # Capture screenshot
    screenshot_path = os.path.join(output_dir, f'image_{idx}.png')
    driver.save_screenshot(screenshot_path)
    
    return screenshot_path

def get_element_bounding_boxes(driver):
    """
    Get the bounding boxes of all input, a, and button elements on a webpage.
    
    Args:
        driver (WebDriver): The WebDriver instance.
        
    Returns:
        list: The bounding boxes of the elements.
        """
    elements = {
        'input': driver.find_elements(By.TAG_NAME, 'input'),
        'a': driver.find_elements(By.TAG_NAME, 'a'),
        'button': driver.find_elements(By.TAG_NAME, 'button')
    }
    
    bounding_boxes = []
    for element_type, elems in elements.items():
        for elem in elems:
            location = elem.location
            size = elem.size
            bounding_box = {
                'type': element_type,
                'x': location['x'],
                'y': location['y'],
                'width': size['width'],
                'height': size['height']
            }
            bounding_boxes.append(bounding_box)
    
    return bounding_boxes

def normalize_bounding_boxes(bounding_boxes, image_size):
    """
    Normalize the bounding boxes of elements on a webpage.

    Args:
        bounding_boxes (list): The bounding boxes of the elements.
        image_size (tuple): The size of the image.

    Returns:
        list: The normalized bounding boxes of the elements.
    """
    image_width, image_height = image_size
    normalized_boxes = []

    for box in bounding_boxes:
        x_center = (box['x'] + box['width'] / 2) / image_width
        y_center = (box['y'] + box['height'] / 2) / image_height
        width = box['width'] / image_width
        height = box['height'] / image_height
        if (x_center <= 0 and y_center <= 0) or x_center > 1 or y_center > 1: continue
        normalized_boxes.append({
            'type': box['type'],
            'x_center': x_center,
            'y_center': y_center,
            'width': width,
            'height': height
        })

    return normalized_boxes

def save_yolo_annotations(normalized_boxes, annotation_path):
    """
    Save the YOLO annotations to a file.
        
    Args:
        normalized_boxes (list): The normalized bounding boxes of the elements.
        annotation_path (str): The path to the annotation file.     
    """
    with open(annotation_path, 'w') as f:
        for box in normalized_boxes:
            class_id = {
                'input': 0,
                'a': 1,
                'button': 2
            }[box['type']]
            f.write(f'{class_id} {box["x_center"]} {box["y_center"]} {box["width"]} {box["height"]}\n')

def process_urls(urls, output_dir):
    """
    Process a list of URLs. Capture screenshots and generate YOLO annotations. 
    Args:
        urls (list): The URLs to process.
        output_dir (str): The output directory.
    
    """
    service = Service('/usr/local/bin/chromedriver')
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    # driver = webdriver.Chrome(service=service, options=options)
    display = Display(visible=0, size=(800, 800))  
    display.start()

    chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                        # and if it doesn't exist, download it automatically,
                                        # then add chromedriver to path

    chrome_options = webdriver.ChromeOptions()    
    # Add your options as needed    
    options = [
    # Define window size here
    "--window-size=1200,1200",
        "--ignore-certificate-errors"
        #"--headless",
        #"--disable-gpu",
        #"--window-size=1920,1200",
        #"--ignore-certificate-errors",
        #"--disable-extensions",
        #"--no-sandbox",
        #"--disable-dev-shm-usage",
        #'--remote-debugging-port=9222'
    ]

    for option in options:
        chrome_options.add_argument(option)
    driver = webdriver.Chrome(options = chrome_options)
    
    # Ensure output directories exist
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'labels'), exist_ok=True)

    for idx, url in enumerate(urls):
        id = str(uuid.uuid4())
        screenshot_path = capture_screenshot(driver, url, os.path.join(output_dir, 'images'), id)
        bounding_boxes = get_element_bounding_boxes(driver)
        image = Image.open(screenshot_path)
        image_size = image.size
        normalized_boxes = normalize_bounding_boxes(bounding_boxes, image_size)
        
        annotation_path = os.path.join(output_dir, 'labels', f'image_{id}.txt')
        save_yolo_annotations(normalized_boxes, annotation_path)

    driver.quit()

# # Example usage
# urls = [
#     'https://google.ch',
#     'https://example.com',
#     'https://digitec.ch'
#     # Add more URLs as needed
# ]

def oxen_pull():
    """
    Pull the data repository from Oxen Hub.
    Returns:
        Repository: The repository object.
    """
    return oxen.clone("Yingrjimsch/a2c2_prompts")

def oxen_push(repo):
    """
    Push the changes to the data repository on Oxen Hub.
    Args:
        repo (Repository): The repository object.  
    """
    repo.add(".")
    # Commit the changes with a message
    repo.commit("Adding new data for training")

    # Set where to push the data to (replace <namespace> and <repo_name> with your remote)
    repo.set_remote("origin", "https://hub.oxen.ai/Yingrjimsch/a2c2_prompts")

    # Push the changes to the remote
    repo.push()

def read_urls_from_file(filepath):
    """
    Read URLs from a file.
    Args:
        filepath (str): The path to the file.
        Returns:
        list: The URLs.
    """
    with open(filepath, 'r') as file:
        urls = file.read().splitlines()
    return set(urls)

def get_unique_urls(file1, file2):
    """
    Get the unique URLs from two files.
    Args:
        file1 (str): The path to the first file.
        file2 (str): The path to the second file.
    Returns:
        list: The unique URLs.
     """
    urls1 = read_urls_from_file(file1)
    urls2 = read_urls_from_file(file2)
    
    unique_urls = urls1.symmetric_difference(urls2)
    
    return list(unique_urls)

def append_list_to_file(file_path, items):
    """
    Append a list of items to a file.
    Args:
        file_path (str): The path to the file.
        items (list): The items to append.
    """
    with open(file_path, 'a') as file:
        for item in items:
            file.write(f'\n{item}')

if __name__ == "__main__":
    dir = oxen_pull()
    urls = get_unique_urls('url_list.txt', 'a2c2_prompts/url_list.txt')
    if not urls == []:
        process_urls(urls, dir.path)
        append_list_to_file(os.path.join(dir.path, 'url_list.txt'), urls)
        oxen_push(dir)
    else:
        print("Nothing to do!")
