from tkinter import *
import math
# from sympy import Point, Polygon
from shapely.geometry import Polygon
from A_star import AstarSearch
from A_star import YAW_TOLERANCE as YAW_STEP

'''================= Your classes and methods ================='''
TRAJECTORY_COLOR = "#f56e6e"
FRONTIER_COLOR = "#ced2d9"

COORD_STEP = 20
# These functions will help you to check collisions with obstacles


def rotate(points, angle, center):
    angle = math.radians(angle)
    cos_val = math.cos(angle)
    sin_val = math.sin(angle)
    cx, cy = center
    new_points = []

    for x_old, y_old in points:
        x_old -= cx
        y_old -= cy
        x_new = x_old * cos_val - y_old * sin_val
        y_new = x_old * sin_val + y_old * cos_val
        new_points.append((x_new + cx, y_new + cy))

    return new_points


def get_polygon_from_position(position):
    x, y, yaw = position
    points = [(x - 50, y - 100), (x + 50, y - 100), (x + 50, y + 100), (x - 50, y + 100)]
    new_points = rotate(points, yaw * 180 / math.pi, (x, y))
    return Polygon(new_points)


def get_polygon_from_obstacle(obstacle):
    points = [(obstacle[0], obstacle[1]), (obstacle[2], obstacle[3]), (obstacle[4], obstacle[5]),
              (obstacle[6], obstacle[7])]
    return Polygon(points)


def collides(position, obstacle):
    return get_polygon_from_position(position).intersects(get_polygon_from_obstacle(obstacle))


def l2_heuristic(state1, state2):
    x1, y1, _ = state1
    x2, y2, _ = state2
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


def next_holonomic_states(state):
    x, y, yaw = state
    next_states = []
    for i in [-COORD_STEP, 0, COORD_STEP]:
        for j in [-COORD_STEP, 0, COORD_STEP]:
            if i == 0 and j == 0:
                continue
            next_states.append((x + i, y + j, yaw))
    return next_states


def sign(x):
    if x == 0:
        return 1
    return x / abs(x)


def next_nonholonomic_states(state):
    x, y, yaw = state
    next_states = []
    for dir in [COORD_STEP]:
        for yaw_ch in [-YAW_STEP, 0, YAW_STEP]:
            new_yaw = yaw + yaw_ch
            if abs(new_yaw) > math.pi:
                new_yaw = - sign(new_yaw) * (math.pi - (abs(new_yaw) % math.pi))

            x_ch = dir * math.sin(new_yaw)
            y_ch = -dir * math.cos(new_yaw)
            new_x = x + x_ch
            new_y = y + y_ch
            next_states.append((new_x, new_y, new_yaw))
    return next_states


class Window:
    """================= Your Main Function ================="""

    def __init__(self):
        self.planner = AstarSearch(self.obstacle_aware_l2, l2_heuristic, next_nonholonomic_states)
        self.prev_trajectory = []
        self.root = Tk()
        self.root.title("")
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.root.geometry(f'{self.width}x{self.height}')
        self.canvas = Canvas(self.root, bg="#777777", height=self.height, width=self.width)
        self.canvas.pack()
        # self.points = [0, 500, 500/2, 0, 500, 500]

    def obstacle_aware_l2(self, state1, state2):
        for obstacle in self.get_obstacles():
            if collides(state1, obstacle) or collides(state2, obstacle):
                return math.inf
        return l2_heuristic(state1, state2)

    def go(self, event):
        self.delete_prev_trajectory()

        # Write your code here

        print("Start position:", self.get_start_position())
        print("Target position:", self.get_target_position())
        print("Obstacles:", self.get_obstacles())

        # Example of collision calculation

        number_of_collisions = 0
        for obstacle in self.get_obstacles():
            if collides(self.get_start_position(), obstacle):
                number_of_collisions += 1
        print("Start position collides with", number_of_collisions, "obstacles")

        start = self.get_start_position()
        target = self.get_target_position()
        trajectory, frontier = self.planner.build_trajectory(start, target)
        print(trajectory)
        self.draw_trajectory(frontier, FRONTIER_COLOR)
        self.draw_trajectory(trajectory, TRAJECTORY_COLOR)

    def draw_trajectory(self, trajectory, color):
        for (center_x, center_y, yaw) in trajectory:
            block = [[center_x - 1, center_y - 5],
                     [center_x + 1, center_y - 5],
                     [center_x + 1, center_y + 5],
                     [center_x - 1, center_y + 5]]
            block = rotate(block, yaw * 180 / math.pi, (center_x, center_y))
            self.prev_trajectory.append(self.draw_block(block, color))

    def delete_prev_trajectory(self, *args):
        for block in self.prev_trajectory:
            self.canvas.delete(block)

    '''================= Interface Methods ================='''

    def get_obstacles(self):
        obstacles = []
        potential_obstacles = self.canvas.find_all()
        for i in potential_obstacles:
            if (i > 2):
                coords = self.canvas.coords(i)
                if coords:
                    obstacles.append(coords)
        return obstacles

    def get_start_position(self):
        x, y = self.get_center(2)  # Purple block has id 2
        yaw = self.get_yaw(2)
        return x, y, yaw

    def get_target_position(self):
        x, y = self.get_center(1)  # Green block has id 1
        yaw = self.get_yaw(1)
        return x, y, yaw

    def get_center(self, id_block):
        coords = self.canvas.coords(id_block)
        center_x, center_y = ((coords[0] + coords[4]) / 2, (coords[1] + coords[5]) / 2)
        return [center_x, center_y]

    def get_yaw(self, id_block):
        center_x, center_y = self.get_center(id_block)
        first_x = 0.0
        first_y = -1.0
        second_x = 1.0
        second_y = 0.0
        points = self.canvas.coords(id_block)
        end_x = (points[0] + points[2]) / 2
        end_y = (points[1] + points[3]) / 2
        direction_x = end_x - center_x
        direction_y = end_y - center_y
        length = math.hypot(direction_x, direction_y)
        unit_x = direction_x / length
        unit_y = direction_y / length
        cos_yaw = unit_x * first_x + unit_y * first_y
        sign_yaw = unit_x * second_x + unit_y * second_y
        if (sign_yaw >= 0):
            return math.acos(cos_yaw)
        else:
            return -math.acos(cos_yaw)

    def get_vertices(self, id_block):
        return self.canvas.coords(id_block)

    '''=================================================='''

    def rotate(self, points, angle, center):
        angle = math.radians(angle)
        cos_val = math.cos(angle)
        sin_val = math.sin(angle)
        cx, cy = center
        new_points = []

        for x_old, y_old in points:
            x_old -= cx
            y_old -= cy
            x_new = x_old * cos_val - y_old * sin_val
            y_new = x_old * sin_val + y_old * cos_val
            new_points.append(x_new + cx)
            new_points.append(y_new + cy)

        return new_points

    def start_block(self, event):
        widget = event.widget
        widget.start_x = event.x
        widget.start_y = event.y

    def in_rect(self, point, rect):
        x_start, x_end = min(rect[::2]), max(rect[::2])
        y_start, y_end = min(rect[1::2]), max(rect[1::2])

        if x_start < point[0] < x_end and y_start < point[1] < y_end:
            return True

    def motion_block(self, event):
        widget = event.widget

        for i in range(1, 10):
            if widget.coords(i) == []:
                break
            if self.in_rect([event.x, event.y], widget.coords(i)):
                coords = widget.coords(i)
                id = i
                break

        res_cords = []
        try:
            coords
        except:
            return

        for ii, i in enumerate(coords):
            if ii % 2 == 0:
                res_cords.append(i + event.x - widget.start_x)
            else:
                res_cords.append(i + event.y - widget.start_y)

        widget.start_x = event.x
        widget.start_y = event.y
        widget.coords(id, res_cords)
        widget.center = ((res_cords[0] + res_cords[4]) / 2, (res_cords[1] + res_cords[5]) / 2)

    def draw_block(self, points, color):
        x = self.canvas.create_polygon(points, fill=color)
        return x

    def distance(self, x1, y1, x2, y2):
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def set_id_block(self, event):
        widget = event.widget

        for i in range(1, 10):
            if widget.coords(i) == []:
                break
            if self.in_rect([event.x, event.y], widget.coords(i)):
                coords = widget.coords(i)
                id = i
                widget.id_block = i
                break

        widget.center = ((coords[0] + coords[4]) / 2, (coords[1] + coords[5]) / 2)

    def rotate_block(self, event):
        angle = 0
        widget = event.widget

        if widget.id_block == None:
            for i in range(1, 10):
                if widget.coords(i) == []:
                    break
                if self.in_rect([event.x, event.y], widget.coords(i)):
                    coords = widget.coords(i)
                    id = i
                    widget.id_block == i
                    break
        else:
            id = widget.id_block
            coords = widget.coords(id)

        wx, wy = event.x_root, event.y_root
        try:
            coords
        except:
            return

        block = coords
        center = widget.center
        x, y = block[2], block[3]

        cat1 = self.distance(x, y, block[4], block[5])
        cat2 = self.distance(wx, wy, block[4], block[5])
        hyp = self.distance(x, y, wx, wy)

        if wx - x > 0:
            angle = math.acos((cat1 ** 2 + cat2 ** 2 - hyp ** 2) / (2 * cat1 * cat2))
        elif wx - x < 0:
            angle = -math.acos((cat1 ** 2 + cat2 ** 2 - hyp ** 2) / (2 * cat1 * cat2))

        new_block = self.rotate([block[0:2], block[2:4], block[4:6], block[6:8]], angle, center)
        self.canvas.coords(id, new_block)

    def delete_block(self, event):
        widget = event.widget.children["!canvas"]
        for i in range(1, 10):
            if widget.coords(i) == []:
                break
            if self.in_rect([event.x, event.y], widget.coords(i)):
                widget.coords(i, [0, 0])
                break

    def create_block(self, event):
        block = [[0, 100], [100, 100], [100, 300], [0, 300]]

        id = self.draw_block(block, "black")

        self.canvas.tag_bind(id, "<Button-1>", self.start_block)
        self.canvas.tag_bind(id, "<Button-3>", self.set_id_block)
        self.canvas.tag_bind(id, "<B1-Motion>", self.motion_block)
        self.canvas.tag_bind(id, "<B3-Motion>", self.rotate_block)

    def make_draggable(self, widget):
        widget.bind("<Button-1>", self.drag_start)
        widget.bind("<B1-Motion>", self.drag_motion)

    def drag_start(self, event):
        widget = event.widget
        widget.start_x = event.x
        widget.start_y = event.y

    def drag_motion(self, event):
        widget = event.widget
        x = widget.winfo_x() - widget.start_x + event.x + 200
        y = widget.winfo_y() - widget.start_y + event.y + 100
        widget.place(rely=0.0, relx=0.0, x=x, y=y)

    def create_button_create(self):
        button = Button(
            text="New",
            bg="#555555",
            activebackground="blue",
            borderwidth=0
        )

        button.place(rely=0.0, relx=0.0, x=200, y=100, anchor=SE, width=200, height=100)
        button.bind("<Button-1>", self.create_block)

    def create_button_clear(self):
        button = Button(
            text="Remove Trajectory",
            bg="#555555",
            activebackground="blue",
            borderwidth=0
        )

        button.place(rely=0.0, relx=0.0, x=400, y=100, anchor=SE, width=200, height=100)
        button.bind("<Button-1>", self.delete_prev_trajectory)

    def create_green_block(self, center_x):
        block = [[center_x - 50, 100],
                 [center_x + 50, 100],
                 [center_x + 50, 300],
                 [center_x - 50, 300]]

        id = self.draw_block(block, "green")

        self.canvas.tag_bind(id, "<Button-1>", self.start_block)
        self.canvas.tag_bind(id, "<Button-3>", self.set_id_block)
        self.canvas.tag_bind(id, "<B1-Motion>", self.motion_block)
        self.canvas.tag_bind(id, "<B3-Motion>", self.rotate_block)

    def create_purple_block(self, center_x, center_y):
        block = [[center_x - 50, center_y - 300],
                 [center_x + 50, center_y - 300],
                 [center_x + 50, center_y - 100],
                 [center_x - 50, center_y - 100]]

        id = self.draw_block(block, "purple")

        self.canvas.tag_bind(id, "<Button-1>", self.start_block)
        self.canvas.tag_bind(id, "<Button-3>", self.set_id_block)
        self.canvas.tag_bind(id, "<B1-Motion>", self.motion_block)
        self.canvas.tag_bind(id, "<B3-Motion>", self.rotate_block)

    def create_button_go(self):
        button = Button(
            text="Go",
            bg="#555555",
            activebackground="blue",
            borderwidth=0
        )

        button.place(rely=0.0, relx=1.0, x=0, y=200, anchor=SE, width=100, height=200)
        button.bind("<Button-1>", self.go)

    def run(self):
        root = self.root

        self.create_button_create()
        self.create_button_go()
        self.create_button_clear()
        self.create_green_block(self.width / 2)
        self.create_purple_block(self.width / 2, self.height)

        root.bind("<Delete>", self.delete_block)

        root.mainloop()


if __name__ == "__main__":
    run = Window()
    run.run()
