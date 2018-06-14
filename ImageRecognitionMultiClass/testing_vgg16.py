# Import basic libraries and keras
import os
import numpy as np
from scipy.misc import imresize
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
from sklearn.metrics import classification_report
from keras import backend as K
from keras import applications
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator, load_img

# Parameters of the model
img_width, img_height = 32, 32
nb_test_samples = 400
batch_size = 20

# Load the models from disk
try:
    vgg_model = load_model("vgg16_pretrained_imagenet.h5")
except:
    vgg_model = applications.VGG16(include_top=False, weights='imagenet')
    vgg_model.save("vgg16_pretrained_imagenet.h5")
model = load_model('bottleneck_fc_model.h5')

# Use the image data format of Keras
if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

# Run on test set
def run_on_test_set(test_set_path):
    test_datagen = ImageDataGenerator(rescale=1. / 255)
    if not os.path.exists('bottleneck_features_test.npy'):
        test_generator = test_datagen.flow_from_directory(test_set_path, shuffle=False,
            target_size=(img_width, img_height), batch_size=batch_size, class_mode='categorical')
        bottleneck_features_test = vgg_model.predict_generator(test_generator,
            nb_test_samples // batch_size, verbose = 1)
        np.save(open('bottleneck_features_test.npy', 'wb'), bottleneck_features_test)
    else:
        bottleneck_features_test = np.load(open('bottleneck_features_test.npy', 'rb'))
    predictions = model.predict_classes(bottleneck_features_test)
    truevalues = [0] * 100 + [1] * 100 + [2] * 100 + [3] * 100
    print(classification_report(truevalues, predictions))

# Classify an image and optionally show it
def classify_image(image_path, plot = True):
    img = load_img(image_path)
    test_x = imresize(img, size=(img_height, img_width)).reshape(input_shape)
    test_x = test_x.reshape((1,) + test_x.shape)
    test_x = test_x / 255.0
    bottleneck_features_test_x = vgg_model.predict(test_x)
    prediction = model.predict(bottleneck_features_test_x)
    predictedclass = np.argmax(prediction)
    predictedvalue = "airplane"
    if predictedclass == 1:
        predictedvalue = "automobile"
    elif predictedclass == 2:
        predictedvalue = "ship"
    elif predictedclass == 3:
        predictedvalue = "truck"
    
    if plot:
        img=mpimg.imread(image_path)
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.imshow(img)
        ax.set_title("This is a " + predictedvalue)
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.show()

    return predictedvalue

run_on_test_set('data/test')
classify_image('data/test/airplanes/airplane.359.png')
