from __future__ import print_function
import os 
from tqdm import tqdm
import cv2
import numpy as np 
import argparse

import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K

batch_size = 32
num_classes = 2
epochs = 2

images = []
labels = []
im_w = 150
im_h = 150

input_shape = (im_w, im_h, 3)

def process(live_input_dirs, fraud_input_dir):
  for images_dir in live_input_dirs:
    files = [os.path.join(images_dir, name) for name in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, name))]
    for i in tqdm(range(0,len(files))):
      filename = os.path.join(images_dir, str(i)+".png")
      img = cv2.imread(filename, cv2.IMREAD_COLOR)
      images.append(img)
      labels.append(1)

  for images_dir in fraud_input_dir:
    files = [os.path.join(images_dir, name) for name in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, name))]
    for i in tqdm(range(0,len(files))):
      filename = os.path.join(images_dir, str(i)+".png")
      img = cv2.imread(filename, cv2.IMREAD_COLOR)
      images.append(img)
      labels.append(0)


  X = np.array(images, dtype=float)
  y = np.array(labels, dtype=float)
  X /= 255
  y= y.reshape((-1,1))
  X = X.reshape((-1, im_h, im_w, 3))

  from sklearn.preprocessing import OneHotEncoder
  Oneencoder = OneHotEncoder()
  y = Oneencoder.fit_transform(y)

  model = Sequential()
  model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu',
                 input_shape=input_shape))
  model.add(Conv2D(64, (3, 3), activation='relu'))
  model.add(MaxPooling2D(pool_size=(2, 2)))
  model.add(Dropout(0.25))
  model.add(Flatten())
  model.add(Dense(128, activation='relu'))
  model.add(Dropout(0.5))
  model.add(Dense(num_classes, activation='softmax'))

  model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])

  model.fit(X, y,
          batch_size=batch_size,
          epochs=epochs,
          verbose=1,
          validation_split=0.2)

  # serialize model to YAML
  model_yaml = model.to_yaml()
  with open("model.yaml", "w") as yaml_file:
    yaml_file.write(model_yaml)

  # serialize weights to HDF5
  model.save_weights("model.h5")
  print("Saved model to disk")

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = 'Process video')
  parser.add_argument('-l','--live', nargs='+', help='list of live optical flow images folders', required=True)
  parser.add_argument('-f','--fraud', nargs='+', help='list of fraud ioptical flow mages folders', required=True)
  args = parser.parse_args()
  process(args.live, args.fraud)