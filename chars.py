

from io import BytesIO
import matplotlib.pyplot as plt
from model import *




def get_main_image():
    loss_time = [get_loss_times(r) for r in data]
    losses = [get_loss(r) for r in data]
    damages = [get_damage(r) for r in data]
    plt.clf()
    plt.scatter(loss_time, losses, alpha=0.5)
    plt.xlabel('time')
    plt.ylabel('losss caused by ASF')
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    return img


def get_region_image(region):
    loss_time = [get_loss_times(r) for r in data if get_place(r)[0] == region]
    losses = [get_loss(r) for r in data if get_place(r)[0] == region]
    damages = [get_damage(r) for r in data if get_place(r)[0] == region]
    plt.clf()
    plt.scatter(loss_time, losses, alpha=0.5)
    plt.xlabel('time')
    plt.ylabel('losss caused by ASF')
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    return img
