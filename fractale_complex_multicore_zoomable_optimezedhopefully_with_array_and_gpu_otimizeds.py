import pygame
import cmath
import threading
from time import sleep, time
import numpy as np
from numba import jit
import yappi


# this time, we using numpy array to actualize the surfaces


class Game():
    def __init__(self):
        self.stopThread = False
        self.Ths = []  # list of the threads

        pygame.init()

        self.clock = pygame.time.Clock()

        self.timesaid = False

        self.loop_running = True
        self.drawn = False
        self.calculated = False

        self.MAX_ITERATION = 500  # nombre d'itérations maximales avant de considérer que la suite converge
        self.centerx = -0.75  # -0.59990625  # -0.750222 #-0.925 #-0.75
        self.centery = 0  # -0.4290703125  # 0.266 #0
        self.zoom = 1.25  # 0.05  # 0.000591 #1.25

        self.compute_dim(self.centerx, self.centery, self.zoom)
        self.LARGEUR, self.HAUTEUR = 1000, 1000  # taille de la fenêtre en pixels

        self.number_of_surfaces = 5
        self.calculated_surfaces = []

        self.rect_surfaces = {}  # -> list of rect surfaces updatable using array so it is faster hopefully

        self.screen = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Fractale de Mandelbrot")

        self.R = threading.Thread(target=self.run_surfaces)
        self.R.start()

    def compute_dim(self, centerx, centery, zoom):
        self.XMIN, self.XMAX = centerx - zoom, centerx + zoom
        self.YMIN, self.YMAX = centery - zoom, centery + zoom


    def reinit(self):
        self.compute_dim(self.centerx, self.centery, self.zoom)

        self.calculated = False
        self.calculated_surfaces = []
        self.drawn = False
        self.timesaid = False

        self.R = threading.Thread(target=self.run_surfaces)
        self.stopThread = False
        sleep(1)
        self.R.start()

    @staticmethod
    @jit(nopython=True)
    def mandelbrot_gpu( x, y, l, h, MAX_ITERATION, XMAX, XMIN, YMAX, YMIN, LARGEUR, HAUTEUR):
        result_array = [[(0, 0, 0) for p in range(h)] for _ in range(l)]
        # calculating mandelbrot

        # print(C)
        # calcul de mandelbrot
        # value = np.zeros((l, h))

        for x1 in range(l):
            # print(x1)
            for y1 in range(h):

                C = complex((x1 + x) * (XMAX - XMIN) / LARGEUR + XMIN,
                            ((y1 + y) * (YMIN - YMAX) / HAUTEUR + YMAX))

                N = 0 + 0j
                n = 0
                while (cmath.polar(N))[0] < 2 and n < MAX_ITERATION:
                    N = N ** 2 + C
                    n = n + 1

                if n == MAX_ITERATION:
                    result_array[x1][y1] = (255, 255, 255)
                else:
                    result_array[x1][y1] = (int(255 * n / MAX_ITERATION), int(255 * n / MAX_ITERATION),
                                            int(255 * n / MAX_ITERATION))

        return result_array


    def compute_surface(self, x, y):

        if self.LARGEUR - x > self.LARGEUR / self.number_of_surfaces:
            l = int(self.LARGEUR / self.number_of_surfaces)
        else:
            l = int(self.LARGEUR - x)

        if self.HAUTEUR - y > self.HAUTEUR / self.number_of_surfaces:
            h = int(self.HAUTEUR / self.number_of_surfaces)
        else:
            h = int(self.HAUTEUR - y)

        # self.rect_surfaces[str(x) + str(y)]["surf"].fill((90, 140, 190))


                    # print(int(255 * n / self.MAX_ITERATION))


        # print(np.array(result_array).shape)

        # value = np.empty((), dtype=object)
        # value[()] = (100, 0, 0)
        # result_array = np.full((l, h), value, dtype=object)  # initializing the array

        # result_array = [[(0, 0, 0) for p in range(h)] for _ in range(l)]



        result_array = self.mandelbrot_gpu(x, y, l, h, self.MAX_ITERATION, self.XMAX, self.XMIN, self.YMAX, self.YMIN, self.LARGEUR, self.HAUTEUR)

        # if n == self.MAX_ITERATION:
        #     result_array[x1][y1] = (255, 255, 255)
        # else:
        #     result_array[x1][y1] = (int(255 * n / self.MAX_ITERATION), int(255 * n / self.MAX_ITERATION),
        #                             int(255 * n / self.MAX_ITERATION))

        result_array = np.array([list(arr) for arr in result_array])
        self.rect_surfaces[str(x) + str(y)] = {"surf": pygame.surfarray.make_surface(result_array), "rect": pygame.Surface((l, h)).get_rect(topleft=(x, y))}

        #self.calculated_surfaces.append({"x": x, "y": y, "result_array": result_array, "id": str(x) + str(y)})

    def run_surfaces(self, ):
        self.t1 = time()
        if not self.calculated:
            self.NS = []
            # yappi.start()
            for self.y in range(0, self.HAUTEUR, int(self.HAUTEUR / self.number_of_surfaces)):
                for self.x in range(0, self.LARGEUR, int(self.LARGEUR / self.number_of_surfaces)):
                    self.Ths.append(threading.Thread(target=self.compute_surface, args=(self.x, self.y),
                                                     daemon=True))  # create a new thead
                    self.Ths[-1].start()  # start the new thread

                    if self.stopThread:
                        break
                if self.stopThread:
                    break

            if self.stopThread:
                self.stopThread = False
                print("exited calculating thread")
                self.Ths = []
                # self.NS = []
                # self.NS_bad = []
            else:


                self.stopThread = False
                print(len(self.NS))
                print("All thread started")
                for t in self.Ths:
                    t.join()
                sleep(1)
                self.calculated = True
                # yappi.stop()
                # threads = yappi.get_thread_stats()
                # for thread in threads:
                #     print(
                #         "Function stats for (%s) (%d)" % (thread.name, thread.id)
                #     )  # it is the Thread.__class__.__name__
                #     yappi.get_func_stats(ctx_id=thread.id).print_all()

    def draw_surfaces(self):
        if self.rect_surfaces != {} :

            for k, s in self.rect_surfaces.copy().items():
                self.screen.blit(s["surf"], s["rect"])
                del self.rect_surfaces[k]
            print(self.rect_surfaces.keys())


        # print(f"{self.calculated_surfaces = }")

        # for _s in self.calculated_surfaces:
        #     # print(f"drawing x : {_s['x']} y : {_s['y']}")
        #     for x2, col_l in enumerate(_s["result_array"]):
        #         for y2, col in enumerate(col_l):
        #             self.screen.set_at((_s["x"] + x2, _s["y"] + y2), col)
        #         # print(f"setting screen at {_s['x']+x2} {_s['y']+y2} with color {col}")
        #     self.calculated_surfaces.remove(_s)
            print("pygame.flip")
            pygame.display.flip()

    def loop(self):
        self.clock.tick(144)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Pour quitter l'application en fermant la fenêtre
                self.loop_running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.stopThread = True
                    sleep(0.1)
                    self.centerx = (pygame.mouse.get_pos()[0]) * (self.XMAX - self.XMIN) / self.LARGEUR + self.XMIN
                    self.centery = (pygame.mouse.get_pos()[1]) * (self.YMIN - self.YMAX) / self.HAUTEUR + self.YMAX
                    print(self.centerx)

                    self.reinit()

                if event.key == pygame.K_p:
                    print("zooming")
                    self.stopThread = True
                    self.zoom = self.zoom * 0.1
                    sleep(0.1)
                    self.reinit()

                if event.key == pygame.K_m:
                    print("dezooming")
                    self.stopThread = True
                    self.zoom = self.zoom * 10
                    sleep(0.1)
                    self.reinit()

                if event.key == pygame.K_1:
                    print("making more iteration")
                    self.MAX_ITERATION*=1.1
                    print(self.MAX_ITERATION)
                    self.stopThread = True
                    sleep(0.1)
                    self.reinit()

                if event.key == pygame.K_2:
                    print("making less iteration")
                    self.MAX_ITERATION*=0.9
                    print(self.MAX_ITERATION)
                    self.stopThread = True
                    sleep(0.1)
                    self.reinit()


        # if self.calculated == False:
        # print(f"len of calculated values : {len(self.NS)+len(self.NS_bad)}")
        if self.drawn == False:
            self.draw_surfaces()

        elif not self.timesaid:
            print(f"calculation took : {time() - self.t1}s ")
            self.timesaid = True
        # print("fps : "+str(self.clock.get_fps()))    #print fps

    def quit(self):
        pygame.quit()


G = Game()
sleep(1)
while True:
    G.loop()
    if G.loop_running == False:
        G.quit()
        break
