# mandelbrot-fractal-pygame

This is a Mandelbrot fractal explorer using pygame for rendering and numba (gpu) for the calculation.
You will need numpy, pygame, numba and yappi. You can simply run each file with python using :
```python3 file.py```. Each file explains what is uses in its name. 


quelques exemples de programmes pour dessiner des fractales avec pygame, 

n'hésitez pas à modifier les valeurs HAUTEUR et LARGEUR de la fenêtre et la valeur MAXITERATION 

les couleurs sont effectuées de manière assez bancale



librairies à intaller (avec pip notamment) :
	
pygame(affichage graphique), numpy(traitement de données), numba(optimisation gpu) , yappi(comme cprofile mais fonctionne avec des threads)





## fonctionnement idéal:

#### lancement fenetre pygame, initialisation du thread de calcul:

	# thread de calcul:
		- sépare la grille en carré de x par x et mets chaque carré dans une Queue/liste
		-vérifie qu'il ne doit pas stopper car changement de zoom/endroit:
			- démarre sois un thread de carré, sois un process de carré (multithreading ou multiprocessing)
			- quand tous les threads sont démarrés, actualise calculated = True


	# thread/proccess de carré:
		- pour chaque pixel associe la couleur RGB associé
		- ajoute une grille ou array de x par x dans la liste générale L

	# loop pygame:
		- event:
			si click gauche:
				zoom, stoppe le thread de calcul
				
		- regarde si nouveaux array dans L
		- sinon regarde dans la liste L si des choses sont présentes et les actualise si c'est le cas, enleve les arrays de déssinés de la liste
		- screen.blit()
		
		
		
# c'est fait! et avec du calcul gpu avec jit en plus !!!!!!!!
