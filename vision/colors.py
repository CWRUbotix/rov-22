"""Gets the dominant colors in an image"""

from sklearn.cluster import KMeans
import numpy as np
import cv2

def centroid_histogram(clt):
    """Gets number of different clusters and returns a normalized histogram from number of pixels assigned to each cluster.
    For example: 'centroid_histogram(clusters)'"""

    num_labels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=num_labels)

    # normalize the histogram so it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()

    return hist

def plot_colors(hist, centroids):
    """Creates color bar window and plots the different colors of the image.
    For example: 'plot_colors(hist, clt.cluster_centers_)'"""

    # Dimensions of color bar window
    width = 500
    height = 50

    # Setting up the color bar window
    bar = np.zeros((height, width, 3), dtype="uint8")
    start_x = 0

    # Plot different colors
    for color in centroids:
        end_x = start_x + (width/len(centroids))
        cv2.rectangle(bar, (int(start_x), 0), (int(end_x), 50), color.astype("uint8").tolist(), -1)
        start_x = end_x

    return bar


def get_colors(image, clusters):
    """Gets the colors in an image and displays the histogram.
    For example: 'get_colors("coral", 8)'"""

    # cv2.imshow("Image", image)

    image = image.reshape(image.shape[0] * image.shape[1], 3)

    clt = KMeans(n_clusters=clusters)
    clt.fit(image)
    centroids = clt.cluster_centers_

    hist = centroid_histogram(clt)
    bar = plot_colors(hist, clt.cluster_centers_)

    # cv2.imshow("Colors", bar)

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return centroids