from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import math

class ElytraSim:
    def __init__(self, vx, vy):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.ticks = 0
        pass

    def resetPos(self):
        self.x = 0.0
        self.y = 0.0
        self.ticks = 0

    def speed(self):
        return 20*math.sqrt(self.vx*self.vx + self.vy*self.vy)

    # From http://imgur.com/a/Vwyjl
    # Positive is down
    def tick(self, pitch, rocket=False):
        self.ticks += 1
        pitch = pitch * 3.14159265 / 180.0
        pitchcos = math.cos(pitch)
        sqrpitchcos = pitchcos * pitchcos
        lookX = 1.0 * -pitchcos
        hvel = abs(self.vx)

        self.vy += -0.08 + sqrpitchcos * 0.06

        if self.vy < 0 and pitchcos > 0:
            yaccel = self.vy * -0.1 * sqrpitchcos
            #print(yaccel, self.vy)
            self.vy += yaccel
            self.vx += lookX * yaccel / pitchcos
        if pitch < 0:
            yaccel = hvel * -math.sin(pitch) * 0.04
            self.vy += yaccel * 3.2
            self.vx -= lookX * yaccel / pitchcos

        # If the rocket is set, force velocity to 32m/s (1.6m/tick)
        if rocket:
            self.vx = -math.cos(pitch) * 1.6
            self.vy = -math.sin(pitch) * 1.6

        self.vx *= 0.99
        self.vy *= 0.98
        self.x += self.vx
        self.y += self.vy
        pass

# This does a run with a profile of cruise, then once we're below y=0 climb
# up at some angle for climbTicks and then return to cruising.
def runLongRange(cruisePitch, climbPitch, climbTicks):
    elytra = ElytraSim(0,0)
    numBoosts = 0
    boostLeft = 0
    maxAlt = 0
    for i in range(5000):
        for i in range(20):
            elytra.tick(cruisePitch)
        if elytra.y < 0.0:
            # Boost for 1.5s
            numBoosts += 1
            for i in range(climbTicks):
                elytra.tick(climbPitch, True)
                maxAlt = max(elytra.y,maxAlt)
    return elytra, numBoosts, maxAlt

def getLongRangeStats(cruisePitch, climbPitch, climbTicks):
    elytra, numBoosts, maxAlt = runLongRange(cruisePitch, climbPitch, climbTicks)
    speed = abs(elytra.x) / (elytra.ticks / 20.0)
    boost_ratio = abs(elytra.x) / numBoosts
    maxrange = abs(elytra.x) / (elytra.ticks / 20.0 / 4.0) * 431
    return speed, maxrange, boost_ratio, maxAlt

# Compute some 3d data
X = []
Y = []
Z = []
for climbPitch in range(-90, -10, 10):
    x = []
    y = []
    z = []
    for cruisePitch in range(-20, 60, 5):
        speed, maxrange, boost_ratio, _ = getLongRangeStats(cruisePitch, climbPitch, 2*30) # Two 30-tick (1.5-second) boosts
        x.append(climbPitch)
        y.append(cruisePitch)
        z.append(maxrange)
    X.append(x)
    Y.append(y)
    Z.append(z)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(X, Y, Z)
plt.show()

# Compute some graphs for matplotlib
pitches = []
boost_ratios = []
max_ranges = []
speeds = []
for pitch in range(-20,60,2):
    speed, maxrange, boost_ratio, _ = getLongRangeStats(pitch, -90, 2*30)
    pitches.append(pitch)
    boost_ratios.append(boost_ratio)
    max_ranges.append(maxrange)
    speeds.append(speed)

plt.figure(1)
plt.subplot(311)
plt.title("Range (m) vs. pitch (degrees, - is up)")
plt.plot(pitches, max_ranges)

plt.subplot(312)
plt.title("Speed (m/s) vs. pitch")
plt.plot(pitches, speeds)

plt.subplot(313)
plt.title("Boost ratio (m/boost) vs. pitch")
plt.plot(pitches, boost_ratios)
#plt.show()

bestCruisePitch = pitches[max_ranges.index(max(max_ranges))]
climbPitches = []
max_ranges = []
for pitch in range(10,90,2):
    speed, maxrange, boost_ratio, maxAlt = getLongRangeStats(bestCruisePitch, -pitch, 2*30)
    #print(maxAlt)
    climbPitches.append(-pitch)
    max_ranges.append(maxrange)

plt.figure(2)
plt.title("Max range vs. climb pitch")
plt.plot(climbPitches, max_ranges)

plt.show()
