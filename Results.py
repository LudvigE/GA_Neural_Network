import pickle, datetime, os

stats = os.listdir('statsv2/')
print(stats)
allt = []
for a in stats:
    t = []
    t.append(a)
    folder = "statsv2/"+a
    b=pickle.load(open(folder, "rb"))
    t.append(b)
    allt.append(t)

    
folder = "Final_Results"
print(allt)
pickle.dump(allt, open(folder, "wb"))

folder = "Final_Results"
save = pickle.load(open(folder, "rb"))
#print(save)
print(len(save))
for m in range(len(save)):
    print(save[m])
    
done =input("DONE=?")


