import pygame
import cmath
import threading
from time import sleep, time
import numpy as np
import yappi

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

        self.MAX_ITERATION = 100  # nombre d'itérations maximales avant de considérer que la suite converge
        self.centerx = -0.75 #-0.59990625  # -0.750222 #-0.925 #-0.75
        self.centery = 0 #-0.4290703125  # 0.266 #0
        self.zoom = 1.25 #0.05  # 0.000591 #1.25

        self.compute_dim(self.centerx, self.centery, self.zoom)
        self.LARGEUR, self.HAUTEUR = 700,700  # taille de la fenêtre en pixels

        self.number_of_surfaces = 10
        self.calculated_surfaces = []


        self.screen = pygame.display.set_mode((self.LARGEUR, self.HAUTEUR))
        pygame.display.set_caption("Fractale de Mandelbrot")

        self.R = threading.Thread(target=self.run_surfaces)
        self.R.start()

    def compute_dim(self, centerx, centery, zoom):
        self.XMIN, self.XMAX = centerx - zoom, centerx + zoom
        self.YMIN, self.YMAX = centery - zoom, centery + zoom

    def mandelbrot(self, _C, x, y):
        _N = complex(0, 0)
        _n = 0
        while (cmath.polar(_N))[0] < 2 and _n < self.MAX_ITERATION:
            _N = _N ** 2 + _C
            _n = _n + 1
        if _n == self.MAX_ITERATION:
            # screen.set_at((x, y), (0, 0, 0)) # On colore le pixel en noir -> code RGB : (0,0,0)
            self.NS.append((x, y, cmath.polar(_N)[0], _n))
        else:
            self.NS_bad.append((x, y, cmath.polar(_N)[0], _n))

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

    def compute_surface(self, x, y):

      if self.LARGEUR-x > self.LARGEUR/self.number_of_surfaces :
        l = int(self.LARGEUR/self.number_of_surfaces)
      else:
        l = int(self.LARGEUR-x)

      if self.HAUTEUR - y > self.HAUTEUR / self.number_of_surfaces:
        h = int(self.HAUTEUR / self.number_of_surfaces)
      else:
        h = int(self.HAUTEUR - y)

      value = np.empty((), dtype=object)
      value[()] = (100, 0, 0)
      result_array = np.full((l, h), value, dtype=object) #initializing the array


      for x1 in range(l):
        #print(x1)
        for y1 in range(h):
          C = complex((x1 + x) * (self.XMAX - self.XMIN) / self.LARGEUR + self.XMIN,
          ((y1 + y)* (self.YMIN - self.YMAX) / self.HAUTEUR + self.YMAX))
          #print(C)
          #calcul de mandelbrot
          N = complex(0, 0)
          n = 0
          while (cmath.polar(N))[0] < 2 and n < self.MAX_ITERATION:
            N = N ** 2 + C
            n = n + 1

          if n == self.MAX_ITERATION:
            result_array[x1][y1] = (255, 255, 255)
          else:
            result_array[x1][y1] = (int(255 * n / self.MAX_ITERATION), int(255 * n / self.MAX_ITERATION), int(255 * n / self.MAX_ITERATION))
            #print(int(255 * n / self.MAX_ITERATION))
      self.calculated_surfaces.append({"x" : x, "y" : y, "result_array":result_array})




    def run_surfaces(self, ):
        self.t1 = time()
        if not self.calculated:
            self.NS = []
            yappi.start()
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

                self.calculated = True
                self.stopThread = False
                print(len(self.NS))
                print("All thread started")
                for t in self.Ths:
                    t.join()
                yappi.stop()
                threads = yappi.get_thread_stats()
                for thread in threads:
                    print(
                        "Function stats for (%s) (%d)" % (thread.name, thread.id)
                    )  # it is the Thread.__class__.__name__
                    yappi.get_func_stats(ctx_id=thread.id).print_all()

    def run(self):
        self.t1 = time()
        if self.calculated == False:
            print("starting creation of threads")
            self.NS = []
            self.NS_bad = []
            self.x, self.y = 0, 0
            for self.y in range(self.HAUTEUR):
                for self.x in range(self.LARGEUR):
                    self.C = complex((self.x * (self.XMAX - self.XMIN) / self.LARGEUR + self.XMIN),
                                     (self.y * (self.YMIN - self.YMAX) / self.HAUTEUR + self.YMAX))
                    self.Ths.append(
                        threading.Thread(target=self.mandelbrot, args=(self.C, self.x, self.y), daemon=True))
                    self.Ths[-1].start()
                    # print("statring new thread")
                    # NS_bad = values that does not converge

                    # self.screen.set_at((self.x, self.y), (int(255*self.n/self.MAX_ITERATION), int(255*self.n/self.MAX_ITERATION), int(255*self.n/self.MAX_ITERATION))) # On colore le pixel en blanc -> code RGB : (255,255,255)
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
                self.Ths = []
                self.NS = []
                self.NS_bad = []
                self.calculated = True
                self.stopThread = False
                print(len(self.NS))
                print("All thread started")

    def draw(self):
        # self.mean = sum([v[2] for v in self.NS])/len(self.NS)
        # self.maxi = max([v[2] for v in self.NS])
        # print(len(self.NS)+len(self.NS_bad))
        if self.drawn == False:
            for _ns in self.NS:
                # self.screen.set_at((_ns[0], _ns[1]), (int(255*(0.1 + 0.8 *_ns[2]/self.maxi)),int(160 * (0.5 + 0.5 *abs(_ns[2]-self.mean)/self.maxi)),0))
                self.screen.set_at((_ns[0], _ns[1]), (255, 255, 255))
                try:
                    self.NS.remove(_ns)
                except:
                    pass

            for _ns_bad in self.NS_bad:
                self.screen.set_at((_ns_bad[0], _ns_bad[1]), (
                int(255 * _ns_bad[3] / self.MAX_ITERATION), int(255 * _ns_bad[3] / self.MAX_ITERATION),
                int(255 * _ns_bad[3] / self.MAX_ITERATION)))
                try:
                    self.NS_bad.remove(_ns_bad)
                except:
                    pass

        pygame.display.flip()
        if self.calculated and len(self.NS) + len(self.NS_bad) == 0:
            self.drawn = True

            # self.drawn = True
            # print("frame")
        # print(int(255*(0.3 + 0.5 * _ns[2]/self.maxi)))

    def draw_surfaces(self):
      if self.drawn == False:
        if self.calculated_surfaces != []:
          #print(f"{self.calculated_surfaces = }")

          for _s in self.calculated_surfaces:
            #print(f"drawing x : {_s['x']} y : {_s['y']}")
            for x2, col_l in enumerate(_s["result_array"]):
              for y2, col in enumerate(col_l):
                self.screen.set_at((_s["x"]+x2, _s["y"]+y2), col)
              #print(f"setting screen at {_s['x']+x2} {_s['y']+y2} with color {col}")
            self.calculated_surfaces.remove(_s)
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
