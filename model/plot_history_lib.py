import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from sklearn.metrics import confusion_matrix

def plot_history(history):
    """
    The plot_history function takes a history object as input and plots the training and validation loss
    and accuracy for each epoch. The function is called in the last cell of this notebook.
    
    :param history: Plot the training and validation loss and accuracy
    :return: A plot of the training and validation loss, as well as a plot of the training and validation accuracy
    """
    history_dict = history.history
    loss_values = history_dict['loss']
    val_loss_values = history_dict['val_loss']
    val_acc_values = history_dict['val_accuracy']

    epochs = range(1, len(history_dict['accuracy']) + 1)

    plt.style.use('dark_background')

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(epochs, loss_values, color='lime', label='Training loss')
    plt.plot(epochs, val_loss_values, color='orangered', label='Validation loss')
    plt.title('Training and validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(linestyle='--')

    plt.subplot(1, 2, 2)
    plt.plot(epochs, history_dict['accuracy'], color='lime', label='Training acc')
    plt.plot(epochs, val_acc_values, color='orangered', label='Validation acc')
    plt.title('Training and validation accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(linestyle='--')
    
    plt.tight_layout()
    plt.show()


def plot_precision_recall(history, classes):
    """
    The plot_precision_recall function takes in a history object and the classes of the dataset.
    It then plots precision and recall for each class on a bar chart.
    
    :param history: Plot the precision and recall for each class
    :param classes: Set the x-axis labels
    :return: A plot of precision and recall for each class
    """
    precision_values = [history.history[f'precision_class{i}'][-1] for i in range(10)]
    recall_values = [history.history[f'recall_class{i}'][-1] for i in range(10)]

    width = 0.25
    x = np.arange(len(classes))

    fig, ax1 = plt.subplots(figsize=(12, 5))

    ax1.bar(x, precision_values, width, label='Precision', color='lime')
    ax1.bar(x + width, recall_values, width, label='Recall', color='orangered')
    ax1.set_xlabel('Class')
    ax1.set_ylabel('Score')
    ax1.set_title('Precision and Recall for Each Class')
    ax1.set_xticks(x + width / 2)
    ax1.set_xticklabels(classes)
    ax1.set_yticks(np.arange(0, 1.1, 0.1))
    ax1.legend(loc='upper left')
    ax1.grid(axis='y', linestyle='--')

    fig.tight_layout()
    plt.show()


def plot_confusion_matrix(y_test, y_pred, classes):
    """
    The plot_confusion_matrix function takes in the following arguments:
        y_test - The true labels of the test set.
        y_pred - The predicted labels of the test set.
        classes - A list containing all possible class names (i.e., ['cat', 'dog'])
    
    :param y_test: Plot the true labels of the test set
    :param y_pred: Plot the predicted labels
    :param classes: Set the labels for each of the classes in our model
    :return: A confusion matrix plot
    """
    conf_matrix = confusion_matrix(np.argmax(y_test, axis=1), y_pred)

    plt.figure(figsize=(8, 6))

    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Greens", xticklabels=classes, yticklabels=classes)
    
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')

    plt.show()


def plot_metrics(history):

    """
    The plot_metrics function takes a history object as input and plots the precision, recall, and F-score per epoch.
    It also plots the precision vs recall curve for all epochs.
    
    
    :param history: Plot the metrics of the model
    :return: A plot of the precision, recall, and f-score per epoch
    """
    precision_per_epoch = []
    recall_per_epoch = []
    for i in range(10):
        precision_key = f'precision_class{i}'
        recall_key = f'recall_class{i}'
        precision_per_epoch.append(history.history[precision_key])
        recall_per_epoch.append(history.history[recall_key])

    precision_per_epoch = np.mean(np.array(precision_per_epoch), axis=0)
    recall_per_epoch = np.mean(np.array(recall_per_epoch), axis=0)
    f1_score_per_epoch = 2 * (precision_per_epoch * recall_per_epoch) / (precision_per_epoch + recall_per_epoch + 1e-8)

    epochs = range(1, len(precision_per_epoch) + 1)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(epochs, precision_per_epoch, label='Precision')
    plt.plot(epochs, recall_per_epoch, label='Recall')
    plt.plot(epochs, f1_score_per_epoch, label='F1-score')
    plt.title('Precision, Recall, and F1-score per epoch')
    plt.xlabel('Epochs')
    plt.ylabel('Metrics')
    plt.legend()
    plt.grid(linestyle='--')

    plt.subplot(1, 2, 2)
    plt.plot(recall_per_epoch, precision_per_epoch)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision vs Recall')
    plt.grid(linestyle='--')

    plt.tight_layout()
    plt.show()