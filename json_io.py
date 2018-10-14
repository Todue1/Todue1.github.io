from PIL import Image
from io import BytesIO
from oauth2client import client

from flask import Flask, render_template, request, redirect, Response
import random, json, base64, time, os, io, sys

from google.cloud.vision import types
from google.cloud import vision_v1p3beta1 as vision

def detect_handwritten_ocr(path):
    """Detects handwritten characters in a local image.

    Args:
    path: The path to the local file.
    """
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    # Language hint codes for handwritten OCR:
    # en-t-i0-handwrit, mul-Latn-t-i0-handwrit
    # Note: Use only one language hint code per request for handwritten OCR.
    image_context = vision.types.ImageContext(
        language_hints=['en-t-i0-handwrit'])

    response = client.document_text_detection(image=image,
                                              image_context=image_context)

    print('Full Text: {}'.format(response.full_text_annotation.text))
    for page in response.full_text_annotation.pages:
        print(len(page.blocks))
        try:
            date = ' '.join([''.join([j.text for i in page.blocks[0].paragraphs[0].words for j in i.symbols])])
        except IndexError:
            date = None
        try:
            assignment = ' '.join([''.join([j.text for i in page.blocks[1].paragraphs[0].words for j in i.symbols])])
        except IndexError:
            assignment = None
        try:
            className = ' '.join([''.join([j.text for i in page.blocks[2].paragraphs[0].words for j in i.symbols])])
        except IndexError:
            className = None
        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('Paragraph confidence: {}'.format(
                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))
    return [date, assignment, className]

app = Flask(__name__)

PNG_START = 22
JPEG_START = 23

@app.route('/')
def output():
	# serve index template
    return render_template('index.html')

@app.route('/receiver', methods = ['POST'])
def worker():
	# read json + reply
    data = request.get_json(force=True)

    if data[:10] == 'data:image':
        if data[:14] == 'data:image/png': # Detects whether image if jpeg or png
            arr = base64.b64decode(data[PNG_START:])
        else:
            arr = base64.b64decode(data[JPEG_START:])

        image = Image.open(BytesIO(arr))
        rotated = image.rotate(-90)
        print(image)
        print(rotated)
        filePath1 = os.path.join(os.path.dirname(__file__), 'data/image' + str(time.time()) + '.jpg') # Guarentees that each picture has a unique name
        filePath2 = os.path.join(os.path.dirname(__file__),'data/image' + str(time.time()) + 'r.jpg')
        image.save(filePath1, 'JPEG')
        rotated.save(filePath2, 'JPEG')

        data = detect_handwritten_ocr(filePath1) # Save it to send to the ocr function

        print("___".join([i if i is not None else '' for i in data]))
        return "___".join([i if i is not None else '' for i in data])
    else:
        CLIENT_SECRET_FILE = 'C:/Users/Calvin/Downloads/client_secret_907446991357-o57v2h2eo5ciso51slrnud4e8up2i2jj.apps.googleusercontent.com.json'
        credentials = client.credentials_from_clientsecrets_and_code(
            CLIENT_SECRET_FILE,
            ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
            data)

        print(credentials.id_token['email'])
        return credentials.id_token['email']


if __name__ == '__main__':
	# run!
    app.debug = True
    # app.run() to have it work locally
    # app.run('0.0.0.0', '5010') to let others connect, requires host's IP address (ipconfig)
    app.run('0.0.0.0', '5010')
