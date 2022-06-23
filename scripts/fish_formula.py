#Calculates the Biomass of the Fish
print('Input (N)um fish, (L)en fish, a, b in that order:')
numFish, fishLength, a, b = float(input()), float(input()), float(input()), float(input())

biomass = numFish * a * (fishLength ** b)
print(biomass)
