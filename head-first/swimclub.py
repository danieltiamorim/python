import statistics
FOLDER = ("swimdata/")

def read_swim_data(filename):
    swimmer, age, distance, stroke = filename.removesuffix(".txt").split("-")
    with open(FOLDER+filename) as file:
        lines = file.readlines()
        times = lines[0].strip().split(",")
        converts = []
        for t in times:
            minutes, rest = t.split(":")
            seconds,hundredths = rest.split(".")
            converts.append((int(minutes) * 60 * 100) + (int(seconds) * 100) + int(hundredths))
            
    average = statistics.mean(converts)
    min_secs, hundredths = str(round(average / 100, 2 )).split(".")
    min_secs = int(min_secs)
    minutes = min_secs // 60 
    seconds = min_secs - minutes * 60
    average = str(minutes) + ":" + str(seconds) + "." + str(hundredths)
    
    return swimmer, age, distance, stroke, times, average