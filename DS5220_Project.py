"""# Setup"""

import numpy as np
import csv
import matplotlib.pyplot as plt
import math
from sklearn.metrics import classification_report, accuracy_score, log_loss
from sklearn.utils import class_weight
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten, Dropout, MaxPooling2D
import time

IMAGE_SHAPE = 28, 28, 4
IMAGE_SIZE = 28 * 28 * 4


"""# Functions"""


# Define function to return a batch of images and their labels
def get_batch(x_path, y_path, batch_size, image_shape=IMAGE_SHAPE):
    x_file, y_file = open(x_path), open(y_path)
    x_reader, y_reader = csv.reader(x_file, delimiter=','), csv.reader(y_file, delimiter=',')

    images = np.zeros((batch_size, *image_shape))
    labels = np.zeros((batch_size, 6))

    for i in range(0, batch_size):
        image = np.reshape(next(x_reader), image_shape)
        label = next(y_reader)

        images[i] = image
        labels[i] = label

    return images, labels


# Define function to return label name given one-hot encoding
def label_names(label):
    labels = ['building', 'barren_land', 'trees', 'grassland', 'road', 'water']
    return [labels[j] for j in range(len(labels)) if [i == 1 for i in label][j]][0]


# Define function to display images
def display_images(images, labels, ir):
    sqrt = math.floor(math.sqrt(np.shape(images)[0]))
    fig, axs = plt.subplots(sqrt, sqrt, figsize=(20, 20))

    for i, ax in enumerate(axs.flatten()):

        ax.set_title(label_names(labels[i]))
        if ir == False:
            ax.imshow(images[i, :, :, :3].astype(np.uint8))


def multilabel_confusion_matrix(y_test, y_pred, title):
    # Iterate over all samples and accumulate pred vs actual counts
    c = np.zeros((6, 6))
    for i in range(len(y_pred)):
        c[np.argmax(y_test[i, :]), np.argmax(y_pred[i, :])] += 1

    # Plot
    l = ['building', 'barren_land', 'trees', 'grassland', 'road', 'water']
    fig, ax = plt.subplots()
    im = ax.imshow(c)

    plt.xticks(np.arange(6), labels=l)
    plt.yticks(np.arange(6), labels=l)
    plt.xlabel("Predicted Classification")
    plt.ylabel("True Classification")
    plt.title(title)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    for i in range(6):
        for j in range(6):
            text = ax.text(j, i, c[i, j], ha="center", va="center", color="w")


def one_hot_from_probabilities(probabilities):
    one_hot = np.zeros((len(probabilities), 6))
    for i in range(len(probabilities)):
        one_hot[i, np.argmax(probabilities[i, :])] = 1

    return one_hot


# changes one hot to 1 to 6 labels
def label_names_num(label):
    labels = [1, 2, 3, 4, 5, 6]
    return [labels[j] for j in range(len(labels)) if [i == 1 for i in label][j]][0]


# Flattens images for input to models
def data_transform(images):
    shape = np.shape(images)

    transformed = np.reshape(images, (shape[0], (shape[1] * shape[2] * shape[3]))).astype('float32')
    transformed /= 255
    return transformed


# Gives accuracy score of predicted versus actual values
def acc(pred, actual):
    count = 0
    for i in range(len(actual)):
        if pred[i] == actual[i]:
            count += 1
    return float(count / len(pred))


"""# EDA"""

# Get and display a batch of images images
images, labels = get_batch("sat_6/X_train_sat6.csv", "sat_6/y_train_sat6.csv", 25)
display_images(images, labels, False)

# Obtain class distribution for train and test datasets
y_trn, y_tst = np.genfromtxt("sat_6/y_train_sat6.csv", delimiter=','), np.genfromtxt("sat_6/y_test_sat6.csv", delimiter=',')
l_y_trn, l_y_tst = len(y_trn), len(y_tst)

print("Training Set Class Distribution:")
for i in range(6):
    l = ['building', 'barren_land', 'trees', 'grassland', 'road', 'water']
    print(str(l[i]) + ":\t" + str(round(sum(y_trn[:, i]) / l_y_trn * 100, 1)) + "%")

print("\nTest Set Class Distribution:")
for i in range(6):
    l = ['building', 'barren_land', 'trees', 'grassland', 'road', 'water']
    print(str(l[i]) + ":\t" + str(round(sum(y_tst[:, i]) / l_y_tst * 100, 1)) + "%")


"""# NEURAL NETWORKS"""

# Get train set
X_train_pre, y_train = get_batch("sat_6/X_train_sat6.csv", "sat_6/y_train_sat6.csv", 10000)
X_train = data_transform(X_train_pre)

# Get test set
X_test_pre, y_test = get_batch("sat_6/X_test_sat6.csv", "sat_6/y_test_sat6.csv", 5000)
X_test = data_transform(X_test_pre)

# Assemble and compile models
nn_wider = Sequential()
nn_wider.add(Dense(units=512, activation='relu', input_shape=(IMAGE_SIZE,)))
nn_wider.add(Dense(units=512, activation='relu', ))
nn_wider.add(Dense(units=6, activation='softmax', ))
nn_wider.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

nn_deeper = Sequential()
nn_deeper.add(Dense(units=256, activation='relu', input_shape=(IMAGE_SIZE,)))
nn_deeper.add(Dense(units=256, activation='relu', ))
nn_deeper.add(Dense(units=256, activation='relu', ))
nn_deeper.add(Dense(units=256, activation='relu', ))
nn_deeper.add(Dense(units=6, activation='softmax', ))
nn_deeper.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

cnn = Sequential()
cnn.add(Conv2D(16, kernel_size=3, activation='relu', input_shape=IMAGE_SHAPE))
cnn.add(Conv2D(32, kernel_size=3, activation='relu'))
cnn.add(MaxPooling2D(pool_size=2))
cnn.add(Dropout(0.5))
cnn.add(Conv2D(32, kernel_size=3, activation='relu'))
cnn.add(Conv2D(64, kernel_size=3, activation='relu'))
cnn.add(MaxPooling2D(pool_size=2))
cnn.add(Dropout(0.5))
cnn.add(Flatten())
cnn.add(Dense(128, activation='relu'))
cnn.add(Dropout(0.5))
cnn.add(Dense(6, activation='softmax'))
cnn.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Assemble and compile models (class balanced)
nn_wider_balanced = Sequential()
nn_wider_balanced.add(Dense(units=512, activation='relu', input_shape=(IMAGE_SIZE,)))
nn_wider_balanced.add(Dense(units=512, activation='relu', ))
nn_wider_balanced.add(Dense(units=6, activation='softmax', ))
nn_wider_balanced.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

nn_deeper_balanced = Sequential()
nn_deeper_balanced.add(Dense(units=256, activation='relu', input_shape=(IMAGE_SIZE,)))
nn_deeper_balanced.add(Dense(units=256, activation='relu', ))
nn_deeper_balanced.add(Dense(units=256, activation='relu', ))
nn_deeper_balanced.add(Dense(units=256, activation='relu', ))
nn_deeper_balanced.add(Dense(units=6, activation='softmax', ))
nn_deeper_balanced.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

cnn_balanced = Sequential()
cnn_balanced.add(Conv2D(16, kernel_size=3, activation='relu', input_shape=IMAGE_SHAPE))
cnn_balanced.add(Conv2D(32, kernel_size=3, activation='relu'))
cnn_balanced.add(MaxPooling2D(pool_size=2))
cnn_balanced.add(Dropout(0.5))
cnn_balanced.add(Conv2D(32, kernel_size=3, activation='relu'))
cnn_balanced.add(Conv2D(64, kernel_size=3, activation='relu'))
cnn_balanced.add(MaxPooling2D(pool_size=2))
cnn_balanced.add(Dropout(0.5))
cnn_balanced.add(Flatten())
cnn_balanced.add(Dense(128, activation='relu'))
cnn_balanced.add(Dropout(0.5))
cnn_balanced.add(Dense(6, activation='softmax'))
cnn_balanced.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train models
history_wider = nn_wider.fit(X_train, y_train, epochs=15, verbose=True, validation_split=0.1)
history_deeper = nn_deeper.fit(X_train, y_train, epochs=15, verbose=True, validation_split=0.1)
history_cnn = cnn.fit(X_train_pre, y_train, epochs=15, verbose=True, validation_split=0.1)

# Train models (class balanced)
class_weights = class_weight.compute_class_weight('balanced', classes=np.unique(np.argmax(y_train, axis=1)),
                                                  y=np.argmax(y_train, axis=1))
d_class_weights = dict(enumerate(class_weights))

history_wider_balanced = nn_wider_balanced.fit(X_train, y_train, epochs=15, verbose=True, validation_split=0.1,
                                               class_weight=d_class_weights)
history_deeper_balanced = nn_deeper_balanced.fit(X_train, y_train, epochs=15, verbose=True, validation_split=0.1,
                                                 class_weight=d_class_weights)
history_cnn_balanced = cnn_balanced.fit(X_train_pre, y_train, epochs=15, verbose=True, validation_split=0.1,
                                        class_weight=d_class_weights)

# Plot train and val accuracy vs epochs
models = {"Wider NN": history_wider,
          "Wider NN Class Balanced": history_wider_balanced,
          "Deeper NN": history_deeper,
          "Deeper NN Class Balanced": history_deeper_balanced,
          "CNN": history_cnn,
          "CNN Class Balanced": history_cnn_balanced}

for model in models:
    plt.plot(models[model].history['accuracy'])
    plt.plot(models[model].history['val_accuracy'])
    plt.title(str(model))
    plt.xlabel('epoch')
    plt.ylabel('accuracy')
    plt.legend(['train', 'val'], loc='upper left')
    plt.show()

# Get predictions on test set
y_pred_wider = nn_wider.predict(X_test)
y_pred_wider_balanced = nn_wider_balanced.predict(X_test)
y_pred_deeper = nn_deeper.predict(X_test)
y_pred_deeper_balanced = nn_deeper_balanced.predict(X_test)
y_pred_cnn = cnn.predict(X_test_pre)
y_pred_cnn_balanced = cnn_balanced.predict(X_test_pre)

# Print classification reports for all NN models
print("Report for wider neural network:")
print(classification_report(y_test, one_hot_from_probabilities(y_pred_wider),
                            target_names=['building', 'barren_land', 'trees', 'grassland', 'road', 'water']))
print("\nReport for wider neural network (balanced):")
print(classification_report(y_test, one_hot_from_probabilities(y_pred_wider_balanced),
                            target_names=['building', 'barren_land', 'trees', 'grassland', 'road', 'water']))
print("\nReport for deeper neural network:")
print(classification_report(y_test, one_hot_from_probabilities(y_pred_deeper),
                            target_names=['building', 'barren_land', 'trees', 'grassland', 'road', 'water']))
print("\nReport for deeper neural network (balanced):")
print(classification_report(y_test, one_hot_from_probabilities(y_pred_deeper_balanced),
                            target_names=['building', 'barren_land', 'trees', 'grassland', 'road', 'water']))
print("\nReport for convolutional neural network:")
print(classification_report(y_test, one_hot_from_probabilities(y_pred_cnn),
                            target_names=['building', 'barren_land', 'trees', 'grassland', 'road', 'water']))
print("\nReport for convolutional neural network (balanced):")
print(classification_report(y_test, one_hot_from_probabilities(y_pred_cnn_balanced),
                            target_names=['building', 'barren_land', 'trees', 'grassland', 'road', 'water']))

# Print confusion matrices for all NN models
multilabel_confusion_matrix(y_test, y_pred_wider, 'Wider NN')
multilabel_confusion_matrix(y_test, y_pred_wider_balanced, 'Wider NN Class Balanced')
multilabel_confusion_matrix(y_test, y_pred_deeper, 'Deeper NN')
multilabel_confusion_matrix(y_test, y_pred_deeper_balanced, 'Deeper NN Class Balanced')
multilabel_confusion_matrix(y_test, y_pred_cnn, 'CNN')
multilabel_confusion_matrix(y_test, y_pred_cnn_balanced, 'CNN Class Balanced')

# Print accuracy for all NN models
print(accuracy_score(y_test, one_hot_from_probabilities(y_pred_wider)))
print(accuracy_score(y_test, one_hot_from_probabilities(y_pred_wider_balanced)))
print(accuracy_score(y_test, one_hot_from_probabilities(y_pred_deeper)))
print(accuracy_score(y_test, one_hot_from_probabilities(y_pred_deeper_balanced)))
print(accuracy_score(y_test, one_hot_from_probabilities(y_pred_cnn)))
print(accuracy_score(y_test, one_hot_from_probabilities(y_pred_cnn_balanced)))


"""# KNN and GNB"""

X, Y = get_batch("sat_6/X_test_sat6.csv", "sat_6/y_test_sat6.csv", 5000)
Xnew = data_transform(X)
X_train, X_test, y_train, y_test = train_test_split(Xnew, Y, test_size=0.2, random_state=12345)

# for loop to determine the best k value
for i in range(1, 25):
    KNN = KNeighborsClassifier(n_neighbors=i)
    KNN.fit(X_train, y_train)
    y_pred = KNN.predict(X_test)
    print("k value: " + str(i) + " accuracy score: " + str(accuracy_score(y_test, y_pred)))

# Code to determine what weightage paramater works the best

KNNEqual = KNeighborsClassifier(n_neighbors=23, p=1)
KNNEqual.fit(X_train, y_train)
y_pred = KNNEqual.predict(X_test)
print("Results for points having equal weight on the classification model:")
print("Precision Score " + str(accuracy_score(y_test, y_pred)))
print(classification_report(y_test, y_pred,
                            target_names=['Building', 'Barren land', 'Trees', 'Grassland', 'Road', 'Water'],
                            zero_division=0))
print(" ")

KNNDistance = KNeighborsClassifier(n_neighbors=23, weights='distance', p=1)
KNNDistance.fit(X_train, y_train)
y_pred = KNNDistance.predict(X_test)
print("Results for points having weight proportionate to distance on the classification model:")
print("Precision Score " + str(accuracy_score(y_test, y_pred)))
print(classification_report(y_test, y_pred,
                            target_names=['Building', 'Barren land', 'Trees', 'Grassland', 'Road', 'Water'],
                            zero_division=0))
print(" ")

# Code to determine what distance calculation is best

# L2 distance
KNNL2 = KNeighborsClassifier(n_neighbors=23, weights='distance', p=2)
KNNL2.fit(X_train, y_train)
y_pred = KNNL2.predict(X_test)
print("Data for L2 distance")
print("Precision Score " + str(accuracy_score(y_test, y_pred)))
print(classification_report(y_test, y_pred,
                            target_names=['Building', 'Barren land', 'Trees', 'Grassland', 'Road', 'Water'],
                            zero_division=0))
print(" ")

KNNL1 = KNeighborsClassifier(n_neighbors=23, weights='distance', p=1)
KNNL1.fit(X_train, y_train)
y_pred = KNNL1.predict(X_test)
print("Data for L1 distance")
print("Precision Score " + str(accuracy_score(y_test, y_pred)))
print("Log Loss " + str(log_loss(y_test, y_pred)))
print(classification_report(y_test, y_pred,
                            target_names=['Building', 'Barren land', 'Trees', 'Grassland', 'Road', 'Water'],
                            zero_division=0))
print(" ")

# Time plot to demonstrate program inefficiency

timeList = []
size = [100, 500, 1000, 1500, 2500, 3500, 5000]  # data size
for i in range(len(size)):
    X, Y = get_batch("sat_6/X_test_sat6.csv", "sat_6/y_test_sat6.csv", size[i])
    Xnew = data_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(Xnew, Y, test_size=0.2, random_state=12345)
    start_time = time.time()
    KNN2 = KNeighborsClassifier(n_neighbors=5, weights='distance', p=1)
    KNN2.fit(X_train, y_train)
    y_pred = KNN2.predict(X_test)
    timeList.append(time.time() - start_time)
plt.scatter(timeList, size, marker='o')
plt.show()

# GNB model
clf1 = GaussianNB()
class_labels = np.argmax(y_train, axis=1)
clf1.fit(X_train, class_labels)
new_labels = np.argmax(y_test, axis=1)
y_pred = clf1.predict(X_test)
print("Gaussian Naive Bayes results:")
print("Precision Score " + str(accuracy_score(np.argmax(y_test, axis=1), y_pred)))
print(classification_report(new_labels, y_pred,
                            target_names=['Building', 'Barren land', 'Trees', 'Grassland', 'Road', 'Water']))


"""# SOFTMAX REGRESSION"""

# changing the label identifiers to numbers number 0 to 5 (6 labels in total)
images, labels = get_batch("sat_6/X_train_sat6.csv", "sat_6/y_train_sat6.csv", 10000)
images_flat = data_transform(images)

label_flat = []
for item in labels:
    label_flat.append(label_names_num(item))

target_names = ['building', 'barren_land', 'trees', 'grassland', 'road', 'water']
from sklearn.model_selection import train_test_split

Xtrain, Xtest, Ytrain, Ytest = train_test_split(images_flat, label_flat, test_size=.1, random_state=42)


from sklearn.linear_model import LogisticRegression

# FIRST model
softmax = LogisticRegression(random_state=42,
                             solver='sag', tol=1e-5, max_iter=700, verbose=False,
                             multi_class='multinomial')
softmax.fit(Xtrain, Ytrain)
# predicting the test data
pred = softmax.predict(Xtest)
# accuracy of first model
print(classification_report(Ytest, pred, target_names=target_names))

# SECOND model
softmax1 = LogisticRegression(random_state=42,
                              solver='saga', tol=1e-5, max_iter=700, verbose=False,
                              multi_class='multinomial')
# fitting the model
softmax1.fit(Xtrain, Ytrain)
# predicting the test data
pred1 = softmax1.predict(Xtest)
print(classification_report(Ytest, pred1, target_names=target_names))

# THIRD model
softmax2 = LogisticRegression(random_state=42,
                              solver='sag', tol=1e-5, max_iter=300, verbose=False,
                              multi_class='multinomial')
# fitting the model
softmax2.fit(Xtrain, Ytrain)
# predicting the test data
pred2 = softmax2.predict(Xtest)
print(classification_report(Ytest, pred2, target_names=target_names))

# FOURTH model
softmax3 = LogisticRegression(random_state=42,
                              solver='saga', tol=1e-5, max_iter=300, verbose=False,
                              multi_class='multinomial', penalty='l1')
# fitting the model
softmax3.fit(Xtrain, Ytrain)
# predicting the test data
pred3 = softmax3.predict(Xtest)
print(classification_report(Ytest, pred3, target_names=target_names))

"""# RANDOM FOREST"""

# FIRST model
from sklearn import tree

Dt = tree.DecisionTreeClassifier()
Dt.fit(Xtrain, Ytrain)
tree_pred = Dt.predict(Xtest)
print(classification_report(Ytest, tree_pred, target_names=target_names))

# SECOND model
from sklearn.ensemble import RandomForestClassifier

rt = RandomForestClassifier(n_estimators=100, random_state=0)
rt.fit(Xtrain, Ytrain)
rand_pred = rt.predict(Xtest)
print(classification_report(Ytest, rand_pred, target_names=target_names))

# THIRD model
rt1 = RandomForestClassifier(n_estimators=200, random_state=0)
rt1.fit(Xtrain, Ytrain)
rand_pred1 = rt1.predict(Xtest)
print(classification_report(Ytest, rand_pred1, target_names=target_names))

# FOURTH model
rt2 = RandomForestClassifier(n_estimators=200, random_state=0, criterion='gini')
rt2.fit(Xtrain, Ytrain)
rand_pred2 = rt2.predict(Xtest)
print(classification_report(Ytest, rand_pred2, target_names=target_names))
