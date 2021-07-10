import pygame
import cmath

# Constantes
MAX_ITERATION = 500 # nombre d'itérations maximales avant de considérer que la suite converge
XMIN, XMAX, YMIN, YMAX = -2, +0.5, -1.25, +1.25 # bornes du repère
LARGEUR, HAUTEUR = 700, 700 # taille de la fenêtre en pixels

zoom = 1
# Initialisation et création d'une fenêtre aux dimensions spécifiéés munie d'un titre
pygame.init()
screen = pygame.display.set_mode((LARGEUR,HAUTEUR))
pygame.display.set_caption("Fractale de Mandelbrot")
# Création de l'ensemble de Mandelbrot
# Principe : on balaye l'écran pixel par pixel en convertissant le pixel en un point du plan de notre repère
# Si la suite converge, le point appartient à l'ensemble de Mandelbrot et on colore le pixel en noir
# Sinon la suite diverge, le point n'appartient pas à l'ensemble et on colore le pixel en blanc


NS = []
for y in range(HAUTEUR):
  for x in range(LARGEUR):
    C = complex((x * (XMAX - XMIN) / LARGEUR + XMIN)*zoom, (y * (YMIN - YMAX) / HAUTEUR + YMAX)*zoom)
    N = complex(0,0)
    n = 0
    while (cmath.polar(N))[0] < 2 and n < MAX_ITERATION: 
      N = N**2 + C
      n = n + 1
    if n == MAX_ITERATION:
        #screen.set_at((x, y), (0, 0, 0)) # On colore le pixel en noir -> code RGB : (0,0,0)
        NS.append((x, y, cmath.polar(N)[0]))
    else:
      screen.set_at((x, y), (int(255*n/MAX_ITERATION), int(255*n/MAX_ITERATION), int(255*n/MAX_ITERATION))) # On colore le pixel en blanc -> code RGB : (255,255,255)

print(len(NS))
mean = sum([v[2] for v in NS])/len(NS)
maxi = max([v[2] for v in NS])

for _ns in NS:
  screen.set_at((_ns[0], _ns[1]), (int(255*(0.1 + 0.8 *_ns[2]/maxi)),int(160 * (0.5 + 0.5 *abs(_ns[2]-mean)/maxi)),0))

print(int(255*(0.3 + 0.5 * _ns[2]/maxi)))

pygame.display.flip() # Mise à jour et rafraîchissement de la fenêtre graphique pour affichage
# Boucle infinie permettant d'afficher à l'écran la fenêtre graphique
# Sans ça, la fenêtre apparaît et disparaît aussitôt
loop = True
while loop:
  for event in pygame.event.get():
    if event.type == pygame.QUIT: # Pour quitter l'application en fermant la fenêtre
      loop = False
      
pygame.quit()
