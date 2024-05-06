import tkinter as tk
import functools
import random
import math
from PIL import ImageTk, Image


class Pedestrian:
    """Κλάση Pedestrian για τη δημιουργία των πεζών και τις λειτουργίες τους"""
    # Οι θέσεις όπου εμφανίζονται οι πεζοί όταν δημιουργούνται
    pedestrian_starting_positions = {"1": (-40, 360), "2": (780, 1130),
                                     "3": (1882, 720), "4": (1060, -40)}
    speed = 3
    speed_by_direction = {"1": (speed, 0), "2": (0, -speed), "3": (-speed, 0), "4": (0, speed)}
    num_of_person_images = 2
    num_of_steps = 2
    ped_img_file = f"../images/pedestrians/Person_#_$.png"
    # Μέγιστος αριθμός πεζών που μπορούν να υπάρχουν ταυτόχρονα
    pedestrian_limit = 10
    # Λίστα με τους ενεργούς πεζούς
    ped_dict = {"1": [], "2": [], "3": [], "4": []}
    total_ped_list = []

    def __init__(self, image, direction, canvas, window):
        """Μέθοδος που δέχεται τις παραμέτρους και δημιουργεί ένα καινούριο αυτοκίνητο"""
        self.image = image
        self.direction = direction
        self.speed = Pedestrian.speed_by_direction[str(self.direction)]
        self.moving = True
        self.stopped = None
        self.step = 0
        self.frames = 0
        self.x = Pedestrian.pedestrian_starting_positions[str(self.direction)][0]
        self.y = Pedestrian.pedestrian_starting_positions[str(self.direction)][1]
        self.root = window
        self.canvas = canvas
        self.pedestrian = self.canvas.create_image(self.x, self.y, image=self.image["st"])
        Pedestrian.ped_dict[str(self.direction)].append(self)
        Pedestrian.total_ped_list.append(self)
        self.move_ped()
        if self.spawn_collision():
            self.delete_ped()

    def move_ped(self):
        """Μέθοδος όπου διαχειρίζεται την κίνηση του κάθε πεζού"""
        if self.moving:
            # Εφόσον ο πεζός κινείται ελέγχει την απόσταση από τον προπορευόμενο πεζό
            # και αν αυτή είναι κάτω από την οριζόμενη τιμή ακινητοποιείται
            for ped in Pedestrian.ped_dict[str(self.direction)]:
                if self != ped and self.direction == ped.direction:
                    if self.direction == 1 and 0 < ped.x - self.x < 120:
                        self.moving = False
                        self.speed = (0, 0)
                        self.stopped = ped
                        self.root.after(30, self.move_ped)
                    elif self.direction == 3 and 0 < self.x - ped.x < 120:
                        self.moving = False
                        self.speed = (0, 0)
                        self.stopped = ped
                        self.root.after(30, self.move_ped)
                    elif self.direction == 2 and 0 < self.y - ped.y < 120:
                        self.moving = False
                        self.speed = (0, 0)
                        self.stopped = ped
                        self.root.after(30, self.move_ped)
                    elif self.direction == 4 and 0 < ped.y - self.y < 120:
                        self.moving = False
                        self.speed = (0, 0)
                        self.stopped = ped
                        self.root.after(30, self.move_ped)
        if self.moving:
            # Εφόσον κινείται ο πεζός αν είναι εντός των ορίων του καμβά συνεχίζει την κίνησή του
            # αλλιώς διαγράφεται
            if -100 < self.x < 1932 and -100 < self.y < 1180:
                self.canvas.move(self.pedestrian, self.speed[0], self.speed[1])
                self.x += self.speed[0]
                self.y += self.speed[1]
                self.frames += 1
                if self.frames == 9:
                    self.step += 1
                    self.frames = 0
                if self.step == Pedestrian.num_of_steps:
                    self.step = 0
                self.canvas.itemconfig(self.pedestrian, image=self.image[str(self.step)])
                self.root.after(30, self.move_ped)
            else:
                self.delete_ped()
        else:
            # Εφόσον είναι σταματημένος ο πεζός, αν μεγαλώσει η απόσταση από τον πεζό για το
            # οποίο σταμάτησε ξεκινάει πάλι να κινείται
            if (self.direction == 1 or self.direction == 3) and abs(self.x - self.stopped.x) > 180:
                self.moving = True
                self.speed = Pedestrian.speed_by_direction[str(self.direction)]
                self.stopped = None
                self.root.after(500, self.move_ped)
            elif (self.direction == 2 or self.direction == 4) and abs(self.y - self.stopped.y) > 180:
                self.moving = True
                self.speed = Pedestrian.speed_by_direction[str(self.direction)]
                self.stopped = None
                self.root.after(500, self.move_ped)

    def delete_ped(self):
        """Μέθοδος η οποία διαγράφει τον πεζό εφόσον εξέλθει των ορίων του καμβά"""
        self.canvas.delete(self.pedestrian)
        Pedestrian.ped_dict[str(self.direction)].remove(self)
        Pedestrian.total_ped_list.remove(self)

    def spawn_collision(self):
        """Μέθοδος η οποία ελέγχει αν ο πεζός που θα δημιουργηθεί θα συγκρουσθεί με ήδη
        υπάρχον πεζό"""
        for ped in Pedestrian.ped_dict[str(self.direction)]:
            if ped != self and math.sqrt(abs(self.x - ped.x)**2 + abs(self.y - ped.y)**2) < 40:
                return True
        return False

    @classmethod
    def pedestrian_creator(cls, ped_images, canvas, root):
        """Μέθοδος η οποία δημιουργεί συνεχώς ένα καινούριο αυτοκίνητο μετά το πέρας ενός
           συγκεκριμένου χρονικού διαστήματος"""
        if len(Pedestrian.total_ped_list) < Pedestrian.pedestrian_limit:
            rand_num = random.randint(1, 100)
            if rand_num <= 35:
                direction = 1
            elif rand_num <= 50:
                direction = 2
            elif rand_num <= 75:
                direction = 3
            else:
                direction = 4
            ped_image = random.choice(list(ped_images[str(direction)].values()))
            Pedestrian(image=ped_image, direction=direction, canvas=canvas, window=root)
        root.after(4000, functools.partial(Pedestrian.pedestrian_creator, ped_images, canvas, root))

    @classmethod
    def create_images(cls):
        # Δημιουργία λεξικού με τις φωτογραφίες των πεζών ανάλογα με την κατεύθυνση
        # του κάθε ένα
        images = {}
        for x in range(0, len(Pedestrian.speed_by_direction)):
            ped_images = {}
            for i in range(0, Pedestrian.num_of_person_images):
                ped_images[str(i + 1)] = {}
                for y in range(0, Pedestrian.num_of_steps):
                    ped_images[str(i + 1)][str(y)] = ImageTk.PhotoImage(Image.open(Pedestrian.ped_img_file.replace("#", str(i)).replace("$", str(y))).rotate(90 * x, expand=True))
                ped_images[str(i + 1)]["st"] = ImageTk.PhotoImage(Image.open(Pedestrian.ped_img_file.replace("#", str(i)).replace("$", "st")).rotate(90 * x, expand=True))
            images[str(x + 1)] = ped_images
        return images
